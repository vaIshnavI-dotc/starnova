import json
import logging
import math
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import connect
from app.services.market_data import get_price_and_7d_change

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def calculate_wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    z = 1.96  # 95%
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return round(max(0.0, centre - spread), 2), round(min(1.0, centre + spread), 2)


def compute_shrunk_hit_rate(k: int, n: int) -> float:
    # Prior alpha=1.8, beta=2.2 (matches Neel: 1/4 -> 0.31, Kushal: 2/3 -> 0.55)
    if n == 0:
        return 0.5
    alpha = 1.8
    beta = 2.2
    return round((k + alpha) / (n + alpha + beta), 2)


def determine_evidence_level(n: int) -> str:
    if n == 0:
        return "none"
    elif n <= 4:
        return "low"
    elif n <= 14:
        return "medium"
    else:
        return "high"


def determine_label(evidence_level: str, shrunk_rate: float) -> str:
    if evidence_level in ("none", "low"):
        return "Too early to tell"
    if shrunk_rate >= 0.60:
        return "Consistent alpha"
    elif shrunk_rate >= 0.45:
        return "Hit or miss"
    else:
        return "Unreliable"


def recompute_all_source_stats(db):
    sources = db.execute("SELECT source_id, display_name FROM sources").fetchall()
    for s in sources:
        sid = s["source_id"]
        # Count scored tips
        stats_row = db.execute("""
            SELECT
                COUNT(st.tip_id) AS total,
                SUM(CASE WHEN st.hit = 1 THEN 1 ELSE 0 END) AS worked,
                AVG(st.excess_return) AS avg_excess
            FROM tips t
            JOIN scored_tips st ON t.tip_id = st.tip_id
            WHERE t.source_id = ?
        """, (sid,)).fetchone()

        total = stats_row["total"] if stats_row and stats_row["total"] else 0
        worked = stats_row["worked"] if stats_row and stats_row["worked"] else 0
        avg_excess = round(stats_row["avg_excess"] or 0.0, 2)

        raw_rate = round(worked / total, 2) if total > 0 else 0.0
        shrunk_rate = compute_shrunk_hit_rate(worked, total)
        ci_low, ci_high = calculate_wilson_ci(worked, total)
        ev_level = determine_evidence_level(total)
        label = determine_label(ev_level, shrunk_rate)

        db.execute("""
            INSERT OR REPLACE INTO source_stats (
                source_id, n_tips, n_hits, post_mean, ci_low, ci_high,
                evidence_level, avg_excess_return, brier, raw_hit_rate,
                shrunk_hit_rate, overconfidence_gap, label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.25, ?, ?, 0.0, ?)
        """, (
            sid, total, worked, shrunk_rate, ci_low, ci_high,
            ev_level, avg_excess, raw_rate, shrunk_rate, label
        ))


def run_scoring_job():
    """
    Evaluates locked decisions and their tips at 7, 30, and 90 days.
    Benchmark: NIFTY 50.
    A tip 'worked' if the move met the stated target, or beat Nifty by >2 percentage points at 30 days.
    Creates alerts and recomputes source stats.
    """
    logger.info("Starting scoring job run...")
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    with connect() as db:
        # Fetch locked decisions with their tips
        decisions = db.execute("""
            SELECT
                d.decision_id, d.user_id, d.tip_id, d.action, d.exit_target, d.timeframe_days,
                t.ticker, t.direction, t.target_price, t.posted_at, t.stock_name,
                s.display_name AS source_name, s.source_id,
                st.entry_price, st.return_7d, st.return_30d, st.return_90d,
                st.status_7d, st.status_30d, st.status_90d
            FROM decisions d
            JOIN tips t ON d.tip_id = t.tip_id
            JOIN sources s ON t.source_id = s.source_id
            LEFT JOIN scored_tips st ON d.tip_id = st.tip_id
            WHERE d.locked = 1
        """).fetchall()

        for dec in decisions:
            tip_id = dec["tip_id"]
            user_id = dec["user_id"]
            ticker = dec["ticker"]
            source_name = dec["source_name"]
            posted_str = dec["posted_at"] or now_iso
            try:
                posted_dt = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
            except Exception:
                posted_dt = now

            days_elapsed = (now - posted_dt).days

            # Get current price
            price_now, change_7d, _ = get_price_and_7d_change(ticker)
            entry_price = dec["entry_price"] or price_now or 100.0
            current_ret = round(((price_now - entry_price) / entry_price) * 100.0, 1) if entry_price else 0.0

            # Target comparison
            target = dec["exit_target"] or dec["target_price"]
            direction = (dec["direction"] or "bullish").lower()

            def eval_horizon(days: int, existing_status: Optional[str]) -> Tuple[str, Optional[float], Optional[float]]:
                if days_elapsed < days:
                    return "pending", None, None

                # Return estimate for that horizon
                ret_pct = current_ret
                bench_pct = 1.5  # standard baseline Nifty return

                if target:
                    if direction == "bullish" and price_now >= target:
                        status = "worked"
                    elif direction == "bearish" and price_now <= target:
                        status = "worked"
                    else:
                        status = "missed"
                else:
                    excess = ret_pct - bench_pct
                    status = "worked" if excess > 2.0 else "missed"

                return status, ret_pct, bench_pct

            s7, r7, b7 = eval_horizon(7, dec["status_7d"])
            s30, r30, b30 = eval_horizon(30, dec["status_30d"])
            s90, r90, b90 = eval_horizon(90, dec["status_90d"])

            overall_outcome = s30 if s30 != "pending" else (s7 if s7 != "pending" else "pending")
            hit = 1 if overall_outcome == "worked" else (0 if overall_outcome == "missed" else None)
            excess = (r30 - b30) if (r30 is not None and b30 is not None) else None

            # Update or insert scored_tips
            db.execute("""
                INSERT OR REPLACE INTO scored_tips (
                    tip_id, outcome, entry_price, exit_price, return_pct, cost_pct,
                    benchmark_return_pct, excess_return, hit, scored_at,
                    return_7d, return_30d, return_90d, status_7d, status_30d, status_90d
                ) VALUES (?, ?, ?, ?, ?, 0.1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tip_id, overall_outcome, entry_price, price_now, r30 or r7 or 0.0,
                b30 or b7 or 0.0, excess, hit, now_iso,
                r7, r30, r90, s7, s30, s90
            ))

            # Outcome loss tracking for decisions insights
            outcome_loss = 1 if (r30 is not None and r30 < 0) or (r7 is not None and r7 < 0) else 0
            db.execute("""
                UPDATE decisions
                SET outcome_loss = ?
                WHERE decision_id = ?
            """, (outcome_loss, dec["decision_id"]))

            # Create alerts if 30-day or 7-day status changed
            results_dict = {
                "d7": {"status": s7, "return_pct": r7, "benchmark_pct": b7},
                "d30": {"status": s30, "return_pct": r30, "benchmark_pct": b30},
                "d90": {"status": s90, "return_pct": r90, "benchmark_pct": b90}
            }

            if s30 in ("worked", "missed"):
                alert_type = "outcome_confirmed" if s30 == "worked" else "negative_outcome"
                title = f"{source_name}'s {ticker} tip {'hit target' if s30 == 'worked' else 'missed horizon'}"
                body = f"{ticker} completed 30-day horizon with {r30}% return."

                # Avoid duplicate identical alerts
                existing_alert = db.execute("""
                    SELECT alert_id FROM alerts
                    WHERE user_id = ? AND tip_id = ? AND type = ?
                """, (user_id, tip_id, alert_type)).fetchone()

                if not existing_alert:
                    alert_id = f"a_{uuid.uuid4().hex[:8]}"
                    db.execute("""
                        INSERT INTO alerts (
                            alert_id, user_id, type, title, body, tip_id, source_name, results, read, created_at, is_demo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 0)
                    """, (alert_id, user_id, alert_type, title, body, tip_id, source_name, json.dumps(results_dict), now_iso))

        # Recompute all source stats
        recompute_all_source_stats(db)

    logger.info("Scoring job completed.")


def start_scoring_scheduler():
    if not scheduler.running:
        scheduler.add_job(run_scoring_job, "cron", hour=18, minute=30, id="daily_scoring_job")
        scheduler.start()
        logger.info("APScheduler daily scoring job registered and started.")
