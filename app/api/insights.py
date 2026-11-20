from fastapi import APIRouter, Depends
from app.core.database import connect
from app.core.auth import get_current_user

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", status_code=200)
def get_insights(user: dict = Depends(get_current_user)):
    insights_list = []
    with connect() as db:
        # Insight 1: 8%+ jump pattern
        row_jump = db.execute("""
            SELECT
                COUNT(*) AS total_bought,
                SUM(CASE WHEN outcome_loss = 1 THEN 1 ELSE 0 END) AS lost_count
            FROM decisions
            WHERE user_id = ? AND action = 'bought' AND jump_7d_at_decision >= 8.0
        """, (user["id"],)).fetchone()

        if row_jump and row_jump["total_bought"] and row_jump["total_bought"] > 0:
            count = row_jump["total_bought"]
            lost = row_jump["lost_count"]
            insights_list.append({
                "id": "i_jump_loss_pattern",
                "text": f"You've bought after an 8%+ jump {count} times. {lost} lost money.",
                "evidence_count": count
            })

        # Insight 2: Skipping vs Buying gap analysis
        row_gaps = db.execute("""
            SELECT
                action,
                AVG(gaps_count) AS avg_gaps
            FROM decisions
            WHERE user_id = ? AND action IN ('bought', 'skipped')
            GROUP BY action
        """, (user["id"],)).fetchall()

        if len(row_gaps) >= 2:
            gap_data = {r["action"]: round(r["avg_gaps"], 1) for r in row_gaps}
            bought_gaps = gap_data.get("bought", 0)
            skipped_gaps = gap_data.get("skipped", 0)
            insights_list.append({
                "id": "i_gaps_correlation",
                "text": f"Decisions you skipped had an average of {skipped_gaps} unverified thesis links, compared to {bought_gaps} for buys.",
                "evidence_count": len(row_gaps)
            })

    return {"insights": insights_list}
