from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from app.core.database import connect
from app.core.auth import get_current_user

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post("/lock", status_code=200)
async def lock_decision(request: Request, user: dict = Depends(get_current_user)):
    try:
        body = await request.json()
    except Exception:
        body = {}

    missing_fields = []
    decision_id = body.get("decision_id")
    if not decision_id:
        missing_fields.append("decision_id")

    action = body.get("action")
    if not action or action not in ("bought", "skipped", "watching"):
        missing_fields.append("action")

    timeframe_days = body.get("timeframe_days")
    if timeframe_days is None or not isinstance(timeframe_days, int) or timeframe_days <= 0:
        missing_fields.append("timeframe_days")

    exit_target = body.get("exit_target")
    if exit_target is None or not (isinstance(exit_target, (int, float))) or exit_target <= 0:
        missing_fields.append("exit_target")

    max_loss_pct = body.get("max_loss_pct")
    if max_loss_pct is None or not (isinstance(max_loss_pct, (int, float))) or max_loss_pct <= 0 or max_loss_pct > 100:
        missing_fields.append("max_loss_pct")

    confidence = body.get("confidence")
    if confidence is None or not isinstance(confidence, int) or confidence < 1 or confidence > 5:
        missing_fields.append("confidence")

    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "gate_incomplete",
                "message": f"Gate incomplete: {', '.join(missing_fields)} missing or invalid",
                "details": {"missing_fields": missing_fields}
            }
        )

    now_iso = datetime.now(timezone.utc).isoformat()

    with connect() as db:
        dec = db.execute(
            "SELECT * FROM decisions WHERE decision_id = ? AND user_id = ?",
            (decision_id, user["id"])
        ).fetchone()

        if not dec:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "not_found",
                    "message": f"Decision {decision_id} not found",
                    "details": {}
                }
            )

        db.execute("""
            UPDATE decisions
            SET action = ?, timeframe_days = ?, exit_target = ?, max_loss_pct = ?,
                confidence = ?, locked = 1, locked_at = ?
            WHERE decision_id = ?
        """, (
            action, timeframe_days, exit_target, max_loss_pct,
            confidence, now_iso, decision_id
        ))

        updated = db.execute(
            "SELECT * FROM decisions WHERE decision_id = ?",
            (decision_id,)
        ).fetchone()

    return {
        "decision": {
            "id": updated["decision_id"],
            "tip_id": updated["tip_id"],
            "action": updated["action"],
            "timeframe_days": updated["timeframe_days"],
            "exit_target": updated["exit_target"],
            "max_loss_pct": updated["max_loss_pct"],
            "confidence": updated["confidence"],
            "thesis": updated["thesis"],
            "gaps_count": updated["gaps_count"],
            "locked_at": updated["locked_at"]
        }
    }


@router.get("", status_code=200)
def list_decisions(user: dict = Depends(get_current_user)):
    with connect() as db:
        rows = db.execute("""
            SELECT
                d.*,
                t.ticker,
                t.stock_name,
                s.display_name AS source_name
            FROM decisions d
            JOIN tips t ON d.tip_id = t.tip_id
            JOIN sources s ON t.source_id = s.source_id
            WHERE d.user_id = ?
            ORDER BY d.created_at DESC
        """, (user["id"],)).fetchall()

    items = []
    for r in rows:
        ticker = r["ticker"] or "UNKNOWN"
        stock_name = r["stock_name"] or ticker
        items.append({
            "id": r["decision_id"],
            "tip_id": r["tip_id"],
            "action": r["action"],
            "timeframe_days": r["timeframe_days"],
            "exit_target": r["exit_target"],
            "max_loss_pct": r["max_loss_pct"],
            "confidence": r["confidence"],
            "thesis": r["thesis"],
            "gaps_count": r["gaps_count"],
            "locked_at": r["locked_at"],
            "stock": {
                "name": stock_name,
                "ticker": ticker
            },
            "source_name": r["source_name"] or "Unknown"
        })

    return {"decisions": items}
