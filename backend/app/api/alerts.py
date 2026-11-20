import json
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import connect
from app.core.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", status_code=200)
def get_alerts(user: dict = Depends(get_current_user)):
    with connect() as db:
        rows = db.execute("""
            SELECT * FROM alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user["id"],)).fetchall()

        unread = db.execute("""
            SELECT COUNT(*) FROM alerts
            WHERE user_id = ? AND read = 0
        """, (user["id"],)).fetchone()[0]

    alerts_list = []
    for r in rows:
        results_val = json.loads(r["results"] or "{}")
        alerts_list.append({
            "id": r["alert_id"],
            "type": r["type"],
            "title": r["title"],
            "body": r["body"],
            "tip_id": r["tip_id"],
            "source_name": r["source_name"],
            "results": results_val,
            "created_at": r["created_at"],
            "read": bool(r["read"])
        })

    return {
        "unread_count": unread,
        "alerts": alerts_list
    }


@router.post("/{alert_id}/read", status_code=200)
def mark_alert_read(alert_id: str, user: dict = Depends(get_current_user)):
    with connect() as db:
        alert = db.execute("""
            SELECT alert_id FROM alerts
            WHERE alert_id = ? AND user_id = ?
        """, (alert_id, user["id"])).fetchone()

        if not alert:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "not_found",
                    "message": f"Alert {alert_id} not found",
                    "details": {}
                }
            )

        db.execute("""
            UPDATE alerts
            SET read = 1
            WHERE alert_id = ?
        """, (alert_id,))

        unread = db.execute("""
            SELECT COUNT(*) FROM alerts
            WHERE user_id = ? AND read = 0
        """, (user["id"],)).fetchone()[0]

    return {"unread_count": unread}


@router.post("/read_all", status_code=200)
def mark_all_alerts_read(user: dict = Depends(get_current_user)):
    with connect() as db:
        db.execute("""
            UPDATE alerts
            SET read = 1
            WHERE user_id = ?
        """, (user["id"],))

    return {"unread_count": 0}
