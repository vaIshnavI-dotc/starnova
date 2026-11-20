import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import connect
from app.core.auth import get_current_user
from app.services.market_data import get_stock_name, get_price_and_7d_change

router = APIRouter(prefix="/investments", tags=["investments"])


class ConfirmInvestmentRequest(BaseModel):
    confirm_token: str = Field(min_length=1)
    ticker: Optional[str] = None
    quantity: Optional[float] = None
    avg_price: Optional[float] = None
    purchase_date: Optional[str] = None


@router.post("/confirm", status_code=201)
def confirm_investment(req: ConfirmInvestmentRequest, user: dict = Depends(get_current_user)):
    now_iso = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        draft_row = db.execute("""
            SELECT * FROM investment_drafts
            WHERE confirm_token = ? AND user_id = ?
        """, (req.confirm_token, user["id"])).fetchone()

        if not draft_row:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "validation_error",
                    "message": "Invalid or expired confirmation token",
                    "details": {"confirm_token": "not_found"}
                }
            )

        if draft_row["expires_at"] < now_iso:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "validation_error",
                    "message": "Confirmation token has expired",
                    "details": {"confirm_token": "expired"}
                }
            )

        draft = json.loads(draft_row["draft_data"])

        # Override with any user-provided edits
        ticker = (req.ticker or draft["ticker"]).upper().replace(".NS", "")
        quantity = req.quantity if req.quantity is not None else float(draft["quantity"])
        avg_price = req.avg_price if req.avg_price is not None else float(draft["avg_price"])
        purchase_date = req.purchase_date or draft["purchase_date"]
        stock_name = draft.get("stock_name") or get_stock_name(ticker)

        # Check for matching tip
        linked_tip = db.execute("""
            SELECT tip_id FROM tips
            WHERE user_id = ? AND ticker = ?
            ORDER BY posted_at DESC LIMIT 1
        """, (user["id"], ticker)).fetchone()
        linked_tip_id = linked_tip["tip_id"] if linked_tip else None

        investment_id = f"inv_{uuid.uuid4().hex[:8]}"

        db.execute("""
            INSERT INTO investments (
                investment_id, user_id, ticker, stock_name, quantity,
                avg_price, purchase_date, linked_tip_id, created_at, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            investment_id, user["id"], ticker, stock_name, quantity,
            avg_price, purchase_date, linked_tip_id, now_iso
        ))

        # Delete draft once confirmed
        db.execute("DELETE FROM investment_drafts WHERE confirm_token = ?", (req.confirm_token,))

    # Market price
    price_now, _, _ = get_price_and_7d_change(ticker)
    current_value = round(quantity * price_now, 2) if price_now is not None else None

    return {
        "investment": {
            "id": investment_id,
            "ticker": ticker,
            "stock_name": stock_name,
            "quantity": quantity,
            "avg_price": avg_price,
            "purchase_date": purchase_date,
            "current_price": price_now,
            "current_value": current_value,
            "linked_tip_id": linked_tip_id
        }
    }


@router.get("", status_code=200)
def list_investments(user: dict = Depends(get_current_user)):
    with connect() as db:
        rows = db.execute("""
            SELECT * FROM investments
            WHERE user_id = ?
            ORDER BY purchase_date DESC
        """, (user["id"],)).fetchall()

    investments = []
    for r in rows:
        ticker = r["ticker"]
        qty = r["quantity"]
        price_now, _, _ = get_price_and_7d_change(ticker)
        current_val = round(qty * price_now, 2) if price_now is not None else None
        investments.append({
            "id": r["investment_id"],
            "ticker": ticker,
            "stock_name": r["stock_name"] or get_stock_name(ticker),
            "quantity": qty,
            "avg_price": r["avg_price"],
            "purchase_date": r["purchase_date"],
            "current_price": price_now,
            "current_value": current_val,
            "linked_tip_id": r["linked_tip_id"]
        })

    return {"investments": investments}
