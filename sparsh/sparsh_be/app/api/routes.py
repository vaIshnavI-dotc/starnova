from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import json
import re
import uuid

from app.core.database import connect
from app.schemas.models import AnalyzeRequest, EvalSessionRequest, EvalDecisionRequest
from app.services.analytics import source_stats_row

router = APIRouter(prefix="/api/v1")


def err(code, message, status=404):
    raise HTTPException(
        status_code=status,
        detail={
            "error": code,
            "message": message,
            "request_id": f"r_{uuid.uuid4().hex[:8]}"
        }
    )


# ---------------------------------------------------------
# META
# ---------------------------------------------------------

@router.get("/meta")
def meta():
    with connect() as db:
        nt = db.execute("SELECT COUNT(*) FROM tips").fetchone()[0]
        ns = db.execute("SELECT COUNT(*) FROM sources").fetchone()[0]

        split = db.execute("""
            SELECT data_origin, COUNT(*) AS n
            FROM tips
            GROUP BY data_origin
        """).fetchall()

    counts = {r["data_origin"]: r["n"] for r in split}

    return {
        "dataset": {
            "n_tips": nt,
            "n_sources": ns,
            "real": counts.get("real", 0),
            "synthetic": counts.get("synthetic", 0)
        },
        "assumptions": {
            "cost_model": "0.1% brokerage + STT, flat",
            "evidence_thresholds": {
                "insufficient": "<5",
                "low": "5-14",
                "moderate": "15-29",
                "high": "30+"
            },
            "benchmark": "NIFTY 50 (^NSEI)"
        },
        "frozen_at": None
    }


# ---------------------------------------------------------
# SOURCES
# ---------------------------------------------------------

@router.get("/sources")
def sources(
    sort: str = Query("shrunk_hit_rate"),
    order: str = Query("desc"),
    min_tips: int = Query(1, ge=1),
    evidence: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    sortmap = {
        "shrunk_hit_rate": "shrunk_hit_rate",
        "n_tips": "n_tips",
        "avg_excess_return": "avg_excess_return"
    }

    if sort not in sortmap or order not in ("asc", "desc"):
        err("validation_error", "Invalid sort or order", 422)

    with connect() as db:
        rows = db.execute("""
            SELECT
                s.*,
                st.n_tips,
                st.n_hits,
                st.raw_hit_rate,
                st.shrunk_hit_rate,
                st.post_mean,
                st.ci_low,
                st.ci_high,
                st.avg_excess_return,
                st.overconfidence_gap,
                st.evidence_level
            FROM sources s
            LEFT JOIN source_stats st USING(source_id)
            WHERE COALESCE(st.n_tips, 0) >= ?
        """, (min_tips,)).fetchall()

    items = [source_stats_row(r) for r in rows]

    if evidence:
        items = [
            item for item in items
            if item.get("evidence_level") == evidence
        ]

    sort_field = sortmap[sort]

    # Keep sources with missing scores at the bottom.
    items.sort(
        key=lambda item: (
            item.get(sort_field) is None,
            -(item.get(sort_field) or 0)
            if order == "desc"
            else (item.get(sort_field) or 0)
        )
    )

    total = len(items)
    start = (page - 1) * page_size

    return {
        "items": items[start:start + page_size],
        "page": page,
        "page_size": page_size,
        "total": total
    }


# ---------------------------------------------------------
# SOURCE DETAIL
# ---------------------------------------------------------

@router.get("/sources/{source_id}")
def source_detail(source_id: str):
    with connect() as db:
        src = db.execute(
            "SELECT * FROM sources WHERE source_id=?",
            (source_id,)
        ).fetchone()

        if not src:
            err("not_found", f"No source with id {source_id}")

        stat = db.execute(
            "SELECT * FROM source_stats WHERE source_id=?",
            (source_id,)
        ).fetchone()

        tips = db.execute("""
            SELECT t.*, s.*
            FROM tips t
            LEFT JOIN scored_tips s USING(tip_id)
            WHERE t.source_id=?
            ORDER BY t.posted_at DESC
        """, (source_id,)).fetchall()

    return {
        "stats": source_stats_row(stat) if stat else None,
        "tips": [{"tip": dict(t)} for t in tips],
        "timeline": [],
        "flags": []
    }


# ---------------------------------------------------------
# TIP DETAIL
# ---------------------------------------------------------

@router.get("/tips/{tip_id}")
def tip_detail(tip_id: str):
    with connect() as db:
        tip = db.execute(
            "SELECT * FROM tips WHERE tip_id=?",
            (tip_id,)
        ).fetchone()

        if not tip:
            err("not_found", f"No tip with id {tip_id}")

        scored = db.execute(
            "SELECT * FROM scored_tips WHERE tip_id=?",
            (tip_id,)
        ).fetchone()

        arch = db.execute(
            "SELECT seq, tip_hash FROM archive_chain WHERE tip_id=?",
            (tip_id,)
        ).fetchone()

    return {
        "tip": dict(tip),
        "scored": dict(scored) if scored else None,
        "flags": [],
        "archive": dict(arch) if arch else None
    }


# ---------------------------------------------------------
# COORDINATION FLAGS
# ---------------------------------------------------------

@router.get("/coordination/flags")
def coordination_flags():
    with connect() as db:
        rows = db.execute("""
            SELECT *
            FROM coord_flags
            ORDER BY window_start DESC
        """).fetchall()

    return {
        "items": [dict(row) for row in rows]
    }


# ---------------------------------------------------------
# COORDINATION GRAPH
# ---------------------------------------------------------

@router.get("/coordination/graph")
def coordination_graph(ticker: str = Query(..., min_length=1)):
    ticker = ticker.upper()

    nodes = {}
    edges = []

    with connect() as db:
        rows = db.execute(
            "SELECT * FROM coord_edges WHERE ticker=?",
            (ticker,)
        ).fetchall()

        for row in rows:
            for sid in (row["source_a"], row["source_b"]):

                if sid and sid not in nodes:
                    source = db.execute("""
                        SELECT display_name
                        FROM sources
                        WHERE source_id=?
                    """, (sid,)).fetchone()

                    nodes[sid] = {
                        "id": sid,
                        "type": "source",
                        "label": source["display_name"] if source else sid
                    }

            nodes[ticker] = {
                "id": ticker,
                "type": "ticker",
                "label": ticker
            }

            if row["source_a"]:
                edges.append({
                    "source": row["source_a"],
                    "target": ticker,
                    "posted_at": None,
                    "lead_rank": None
                })

            if row["source_b"]:
                edges.append({
                    "source": row["source_b"],
                    "target": ticker,
                    "posted_at": None,
                    "lead_rank": None
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }


# ---------------------------------------------------------
# ARCHIVE VERIFICATION
# ---------------------------------------------------------

@router.get("/archive/verify/{tip_id}")
def archive_verify(tip_id: str):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM archive_chain WHERE tip_id=?",
            (tip_id,)
        ).fetchone()

    if not row:
        err("not_found", f"No archive entry for tip {tip_id}")

    return {
        "tip_id": tip_id,
        "stored_hash": row["tip_hash"],
        "recomputed_hash": None,
        "chain_valid": None,
        "seq": row["seq"],
        "prev_hash": row["prev_hash"],
        "anchor": None
    }


@router.get("/archive/chain/head")
def archive_head():
    with connect() as db:
        row = db.execute("""
            SELECT *
            FROM archive_chain
            ORDER BY seq DESC
            LIMIT 1
        """).fetchone()

    if not row:
        return {
            "seq": 0,
            "chain_hash": None,
            "ts": None,
            "anchor_tx": None
        }

    return {
        "seq": row["seq"],
        "chain_hash": row["chain_hash"],
        "ts": row["ts"],
        "anchor_tx": row["anchor_tx"]
    }


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    ticker_match = re.search(
        r"\b([A-Z]{2,12})\b",
        req.text.upper()
    )

    if not ticker_match:
        err("unparseable_tip", "No ticker found", 422)

    ticker = ticker_match.group(1)

    with connect() as db:
        tip = db.execute("""
            SELECT *
            FROM tips
            WHERE ticker=?
            ORDER BY posted_at DESC
            LIMIT 1
        """, (ticker,)).fetchone()

    if tip:
        return {
            "mode": "cached",
            "extraction": {
                "ticker": ticker,
                "direction": tip["direction"],
                "target_price": tip["target_price"],
                "horizon_days": tip["horizon_days"],
                "confidence_words": json.loads(
                    tip["confidence_words"] or "[]"
                ),
                "language": tip["language"],
                "extraction_conf": tip["extraction_conf"]
            },
            "source": {
                "matched": True,
                "stats": None
            },
            "reference_class": None,
            "flags": [],
            "archive": None,
            "disclaimer": (
                "Informational only. This tool does not give buy or sell advice."
            )
        }

    err(
        "extractor_unavailable",
        "No cached extraction found and live extractor is not configured.",
        503
    )


# ---------------------------------------------------------
# EVALUATION SESSIONS
# ---------------------------------------------------------

@router.post("/eval/sessions", status_code=201)
def eval_session(req: EvalSessionRequest):
    session_id = f"s_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        count = db.execute(
            "SELECT COUNT(*) FROM eval_sessions"
        ).fetchone()[0]

        arm = "tool" if count % 2 == 0 else "control"

        db.execute(
            "INSERT INTO eval_sessions VALUES(?,?,?)",
            (session_id, arm, now)
        )

        tips = db.execute("""
            SELECT tip_id, raw_text, ticker, direction,
                   posted_at, source_type
            FROM tips
            ORDER BY RANDOM()
            LIMIT 5
        """).fetchall()

        items = []

        for i, tip in enumerate(tips):
            item_id = f"i_{uuid.uuid4().hex[:8]}"

            db.execute(
                "INSERT INTO eval_items VALUES(?,?,?,?)",
                (item_id, session_id, tip["tip_id"], i + 1)
            )

            items.append({
                "item_id": item_id,
                "tip": dict(tip)
            })

    return {
        "session_id": session_id,
        "arm": arm,
        "items": items
    }


# ---------------------------------------------------------
# EVALUATION DECISIONS
# ---------------------------------------------------------

@router.post("/eval/decisions", status_code=201)
def eval_decision(req: EvalDecisionRequest):
    now = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        session = db.execute("""
            SELECT 1
            FROM eval_sessions
            WHERE session_id=?
        """, (req.session_id,)).fetchone()

        if not session:
            err("not_found", f"No session {req.session_id}")

        item = db.execute("""
            SELECT 1
            FROM eval_items
            WHERE item_id=? AND session_id=?
        """, (req.item_id, req.session_id)).fetchone()

        if not item:
            err("not_found", "Item not found in session")

        db.execute("""
            INSERT OR REPLACE INTO eval_decisions
            VALUES(?,?,?,?,?,?)
        """, (
            req.session_id,
            req.item_id,
            req.decision,
            req.confidence,
            req.position_pct,
            now
        ))

    return {
        "ok": True
    }


# ---------------------------------------------------------
# EVALUATION RESULTS
# ---------------------------------------------------------

@router.get("/eval/results")
def eval_results():
    return {
        "arms": {
            "control": {
                "n_participants": 0,
                "mean_return_pct": None,
                "pnd_tips_followed_pct": None,
                "brier": None
            },
            "tool": {
                "n_participants": 0,
                "mean_return_pct": None,
                "pnd_tips_followed_pct": None,
                "brier": None
            }
        },
        "effect": {
            "metric": "mean_return_pct",
            "diff": None,
            "ci_low": None,
            "ci_high": None,
            "test": "welch_t"
        },
        "note": "No evaluation results available yet."
    }