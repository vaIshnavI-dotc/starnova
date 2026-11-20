import json
from datetime import datetime, timezone
from app.core.database import connect
from app.core.auth import hash_password


def seed_demo_data():
    now_iso = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        # Check if demo user already exists
        existing_user = db.execute(
            "SELECT id FROM users WHERE email = ?",
            ("demo@signalnoise.app",)
        ).fetchone()

        if existing_user:
            return  # Already seeded, idempotent

        user_id = "u_demo"
        db.execute("""
            INSERT INTO users (id, name, email, password_hash, created_at, is_demo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (
            user_id,
            "Demo User",
            "demo@signalnoise.app",
            hash_password("demo1234"),
            now_iso
        ))

        # Sources
        # 1. Neel: 4 tips, 1 worked
        db.execute("""
            INSERT OR REPLACE INTO sources (source_id, display_name, source_type, sebi_registered, data_origin, user_id, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, ("s_neel", "Neel", "friend", 0, "synthetic", user_id))

        db.execute("""
            INSERT OR REPLACE INTO source_stats (
                source_id, n_tips, n_hits, post_mean, ci_low, ci_high, evidence_level,
                avg_excess_return, brier, raw_hit_rate, shrunk_hit_rate, overconfidence_gap,
                user_id, label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "s_neel", 4, 1, 0.31, 0.10, 0.55, "low",
            -1.8, 0.22, 0.25, 0.31, 0.15,
            user_id, "Too early to tell"
        ))

        # 2. Kushal: 3 tips, 2 worked
        db.execute("""
            INSERT OR REPLACE INTO sources (source_id, display_name, source_type, sebi_registered, data_origin, user_id, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, ("s_kushal", "Kushal", "friend", 0, "synthetic", user_id))

        db.execute("""
            INSERT OR REPLACE INTO source_stats (
                source_id, n_tips, n_hits, post_mean, ci_low, ci_high, evidence_level,
                avg_excess_return, brier, raw_hit_rate, shrunk_hit_rate, overconfidence_gap,
                user_id, label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "s_kushal", 3, 2, 0.55, 0.20, 0.85, "low",
            2.1, 0.18, 0.67, 0.55, 0.05,
            user_id, "Too early to tell"
        ))

        # 3. Anonymous: 5 tips, 1 worked
        db.execute("""
            INSERT OR REPLACE INTO sources (source_id, display_name, source_type, sebi_registered, data_origin, user_id, is_demo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, ("s_anon", "Anonymous tip", "anonymous", 0, "synthetic", user_id))

        db.execute("""
            INSERT OR REPLACE INTO source_stats (
                source_id, n_tips, n_hits, post_mean, ci_low, ci_high, evidence_level,
                avg_excess_return, brier, raw_hit_rate, shrunk_hit_rate, overconfidence_gap,
                user_id, label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "s_anon", 5, 1, 0.27, 0.08, 0.50, "medium",
            -5.4, 0.30, 0.20, 0.27, 0.25,
            user_id, "Too early to tell"
        ))

        # Tips
        neel_tips = [
            ("t_neel_1", "s_neel", "2026-10-15T10:00:00Z", "Tata Motors will hit 950 by next month on massive EV order win and JLR margin expansion.", "TATAMOTORS", "Tata Motors", "bullish", 950.0, 30, '["urgent","breakout"]', 0.9, 1, 12.4, 3.2, 9.2, 1),
            ("t_neel_2", "s_neel", "2026-09-10T10:00:00Z", "BEL bags major defence radar deal, easy 15% upside in 30 days.", "BEL", "Bharat Electronics", "bullish", 320.0, 30, '["guaranteed"]', 0.85, 0, -4.2, 1.6, -5.8, 0),
            ("t_neel_3", "s_neel", "2026-08-12T10:00:00Z", "HAL order book solid, quick swing trade to 4800.", "HAL", "Hindustan Aeronautics", "bullish", 4800.0, 30, '["sure shot"]', 0.8, 0, -2.5, 3.6, -6.1, 0),
            ("t_neel_4", "s_neel", "2026-07-20T10:00:00Z", "BHEL thermal power orders flowing in, target 310.", "BHEL", "Bharat Heavy Electricals", "bullish", 310.0, 30, '["double"]', 0.8, 0, -8.0, 1.5, -9.5, 0),
        ]

        kushal_tips = [
            ("t_kushal_1", "s_kushal", "2026-09-01T10:00:00Z", "Infosys large deal pipeline looking strong this quarter, target 1900.", "INFY", "Infosys", "bullish", 1900.0, 30, '["solid"]', 0.9, 1, 8.5, 3.4, 5.1, 1),
            ("t_kushal_2", "s_kushal", "2026-08-15T10:00:00Z", "TCS BFSI demand turnaround imminent, buy for 4200.", "TCS", "Tata Consultancy Services", "bullish", 4200.0, 30, '["safe"]', 0.88, 1, 6.2, 2.2, 4.0, 1),
            ("t_kushal_3", "s_kushal", "2026-10-01T10:00:00Z", "Zomato quick commerce Blinkit expansion will explode margins, target 280.", "ZOMATO", "Zomato", "bullish", 280.0, 30, '["huge upside"]', 0.85, 0, -6.1, 2.0, -8.1, 0),
        ]

        anon_tips = [
            ("t_anon_1", "s_anon", "2026-09-05T10:00:00Z", "Suzlon energy transition boom target 65 in 30 days.", "SUZLON", "Suzlon Energy", "bullish", 65.0, 30, '["rocket"]', 0.8, 1, 15.0, 4.0, 11.0, 1),
            ("t_anon_2", "s_anon", "2026-09-12T10:00:00Z", "IREDA green energy lending rally target 240 next week.", "IREDA", "Indian Renewable Energy", "bullish", 240.0, 30, '["guaranteed"]', 0.75, 0, -11.0, 2.5, -13.5, 0),
            ("t_anon_3", "s_anon", "2026-08-18T10:00:00Z", "Reliance Power turnaround news coming, target 45.", "RPOWER", "Reliance Power", "bullish", 45.0, 30, '["multibagger"]', 0.7, 0, -14.0, 1.8, -15.8, 0),
            ("t_anon_4", "s_anon", "2026-07-25T10:00:00Z", "Vodafone Idea fundraising close, target 18.", "IDEA", "Vodafone Idea", "bullish", 18.0, 30, '["insider"]', 0.7, 0, -18.0, 1.2, -19.2, 0),
            ("t_anon_5", "s_anon", "2026-06-15T10:00:00Z", "Yes Bank NPA resolution spike to 30.", "YESBANK", "Yes Bank", "bullish", 30.0, 30, '["easy money"]', 0.65, 0, -7.0, 2.0, -9.0, 0),
        ]

        for tip_id, sid, posted, text, ticker, sname, direction, tgt, horizon, conf_words, conf, hit, ret_pct, bench_pct, excess_ret, outcome_worked in neel_tips + kushal_tips + anon_tips:
            db.execute("""
                INSERT OR REPLACE INTO tips (
                    tip_id, source_id, posted_at, raw_text, language, ticker, direction,
                    target_price, horizon_days, confidence_words, extraction_conf, data_origin,
                    user_id, is_demo, stock_name, claim, red_flags
                ) VALUES (?, ?, ?, ?, 'en', ?, ?, ?, ?, ?, ?, 'synthetic', ?, 1, ?, ?, ?)
            """, (
                tip_id, sid, posted, text, ticker, direction,
                tgt, horizon, conf_words, conf,
                user_id, sname, text, '["urgency","unsupported_claim"]'
            ))

            status_val = "worked" if outcome_worked else "missed"
            db.execute("""
                INSERT OR REPLACE INTO scored_tips (
                    tip_id, outcome, entry_price, exit_price, return_pct, cost_pct,
                    benchmark_return_pct, excess_return, hit, scored_at,
                    return_7d, return_30d, return_90d, status_7d, status_30d, status_90d
                ) VALUES (?, ?, ?, ?, ?, 0.1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tip_id, status_val, 100.0, 100.0 * (1 + ret_pct / 100.0), ret_pct,
                bench_pct, excess_ret, hit, posted,
                ret_pct * 0.4, ret_pct, ret_pct, status_val, status_val, status_val
            ))

        # Decisions: including 4 bought after an 8%+ jump, 3 of which lost
        decisions_data = [
            ("d_demo_ireda", user_id, "t_anon_2", "bought", 30, 240.0, 10.0, 4, "Renewable energy loan growth surge", 3, 1, "2026-09-12T12:00:00Z", 215.0, 11.2, 1),
            ("d_demo_rpower", user_id, "t_anon_3", "bought", 30, 45.0, 8.0, 3, "Debt restructuring approval", 4, 1, "2026-08-18T12:00:00Z", 39.0, 9.5, 1),
            ("d_demo_idea", user_id, "t_anon_4", "bought", 30, 18.0, 12.0, 2, "Bank debt conversion to equity", 4, 1, "2026-07-25T12:00:00Z", 15.2, 8.4, 1),
            ("d_demo_suzlon", user_id, "t_anon_1", "bought", 30, 65.0, 8.0, 4, "Wind order book execution speedup", 2, 1, "2026-09-05T12:00:00Z", 56.5, 10.1, 0),
            ("d_demo_tata", user_id, "t_neel_1", "bought", 30, 950.0, 8.0, 3, "JLR Q3 EBITDA margin expansion above 14%", 3, 1, "2026-10-16T10:00:00Z", 812.4, 6.2, 0),
        ]

        for did, uid, tid, act, timef, tgt, max_loss, conf, thesis, gaps, locked, locked_at, price, jump7, loss in decisions_data:
            db.execute("""
                INSERT OR REPLACE INTO decisions (
                    decision_id, user_id, tip_id, action, timeframe_days, exit_target,
                    max_loss_pct, confidence, thesis, gaps_count, locked, locked_at,
                    created_at, price_at_decision, jump_7d_at_decision, outcome_loss, is_demo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                did, uid, tid, act, timef, tgt,
                max_loss, conf, thesis, gaps, locked, locked_at,
                locked_at or now_iso, price, jump7, loss
            ))

        # Alerts (3 of different types, unread count = 2)
        alert_1_results = {
            "d7": {"status": "worked", "return_pct": 5.2, "benchmark_pct": 1.1},
            "d30": {"status": "worked", "return_pct": 12.4, "benchmark_pct": 3.2},
            "d90": {"status": "pending", "return_pct": None, "benchmark_pct": None}
        }
        db.execute("""
            INSERT OR REPLACE INTO alerts (
                alert_id, user_id, type, title, body, tip_id, source_name, results, read, created_at, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 1)
        """, (
            "a_1", user_id, "outcome_confirmed", "Neel's Tata Motors tip hit target",
            "TATAMOTORS reached 950 target (+12.4% return).", "t_neel_1", "Neel",
            json.dumps(alert_1_results), "2026-11-15T14:30:00Z"
        ))

        alert_2_results = {
            "d7": {"status": "pending", "return_pct": None, "benchmark_pct": None},
            "d30": {"status": "missed", "return_pct": -6.1, "benchmark_pct": 2.0},
            "d90": {"status": "pending", "return_pct": None, "benchmark_pct": None}
        }
        db.execute("""
            INSERT OR REPLACE INTO alerts (
                alert_id, user_id, type, title, body, tip_id, source_name, results, read, created_at, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 1)
        """, (
            "a_2", user_id, "negative_outcome", "Kushal's Zomato tip missed horizon",
            "ZOMATO failed to hold target after 30 days (-6.1% return).", "t_kushal_3", "Kushal",
            json.dumps(alert_2_results), "2026-11-10T09:15:00Z"
        ))

        alert_3_results = {
            "d7": {"status": "worked", "return_pct": 3.8, "benchmark_pct": 0.5},
            "d30": {"status": "pending", "return_pct": None, "benchmark_pct": None},
            "d90": {"status": "pending", "return_pct": None, "benchmark_pct": None}
        }
        db.execute("""
            INSERT OR REPLACE INTO alerts (
                alert_id, user_id, type, title, body, tip_id, source_name, results, read, created_at, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 1)
        """, (
            "a_3", user_id, "new_update", "7-day checkpoint on BEL",
            "BEL is up +3.8% vs Nifty +0.5% at day 7.", "t_neel_2", "Neel",
            json.dumps(alert_3_results), "2026-11-05T16:00:00Z"
        ))
