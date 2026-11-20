import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.database import connect
from app.services.llm import (
    extract_tip_from_image,
    split_thesis,
    check_link,
    select_questions,
    detect_investment
)
from app.services.market_data import (
    get_stock_name,
    get_price_and_7d_change
)


def get_or_create_source(db, user_id: str, sender_name: str) -> Tuple[str, Dict[str, Any]]:
    # Check if user already has this source
    row = db.execute("""
        SELECT s.*, st.n_tips, st.n_hits, st.shrunk_hit_rate, st.evidence_level, st.label
        FROM sources s
        LEFT JOIN source_stats st USING(source_id)
        WHERE (s.user_id = ? OR s.user_id IS NULL) AND LOWER(s.display_name) = LOWER(?)
        ORDER BY s.user_id DESC
        LIMIT 1
    """, (user_id, sender_name.strip())).fetchone()

    if row:
        source_id = row["source_id"]
        return source_id, {
            "source_id": source_id,
            "source_name": row["display_name"],
            "tips_total": row["n_tips"] or 0,
            "tips_worked": row["n_hits"] or 0,
            "shrunk_hit_rate": row["shrunk_hit_rate"] if row["shrunk_hit_rate"] is not None else 0.5,
            "evidence_level": row["evidence_level"] or "none",
            "label": row["label"] or "Too early to tell"
        }

    # Create new source for this user
    source_id = f"s_{uuid.uuid4().hex[:8]}"
    stype = "anonymous" if "anonymous" in sender_name.lower() else "friend"
    db.execute("""
        INSERT INTO sources (source_id, display_name, source_type, sebi_registered, data_origin, user_id, is_demo)
        VALUES (?, ?, ?, 0, 'synthetic', ?, 0)
    """, (source_id, sender_name.strip(), stype, user_id))

    db.execute("""
        INSERT INTO source_stats (
            source_id, n_tips, n_hits, post_mean, ci_low, ci_high,
            evidence_level, avg_excess_return, brier, raw_hit_rate,
            shrunk_hit_rate, overconfidence_gap, user_id, label
        ) VALUES (?, 0, 0, 0.5, 0.0, 1.0, 'none', 0.0, 0.25, 0.0, 0.5, 0.0, ?, 'Too early to tell')
    """, (source_id, user_id))

    return source_id, {
        "source_id": source_id,
        "source_name": sender_name.strip(),
        "tips_total": 0,
        "tips_worked": 0,
        "shrunk_hit_rate": 0.5,
        "evidence_level": "none",
        "label": "Too early to tell"
    }


def check_for_pattern_insight(db, user_id: str, ticker: str, change_7d: Optional[float]) -> Optional[Dict[str, Any]]:
    # Check if user has a pattern of buying after 8%+ jumps
    row = db.execute("""
        SELECT
            COUNT(*) AS total_bought_after_jump,
            SUM(CASE WHEN outcome_loss = 1 THEN 1 ELSE 0 END) AS lost_count
        FROM decisions
        WHERE user_id = ? AND action = 'bought' AND jump_7d_at_decision >= 8.0
    """, (user_id,)).fetchone()

    total_bought = row["total_bought_after_jump"] if row else 0
    lost = row["lost_count"] if row else 0

    if total_bought >= 2:
        return {
            "type": "insight",
            "text": f"You've bought after an 8%+ jump {total_bought} times. {lost} lost money."
        }
    return None


def process_chat_message(
    user: dict,
    conversation_id: Optional[str],
    text: Optional[str],
    image_bytes: Optional[bytes],
    image_filename: Optional[str]
) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    user_id = user["id"]

    with connect() as db:
        conv = None
        if conversation_id:
            conv = db.execute(
                "SELECT * FROM conversations WHERE conversation_id = ? AND user_id = ?",
                (conversation_id, user_id)
            ).fetchone()

        if not conv:
            conversation_id = f"c_{uuid.uuid4().hex[:8]}"
            db.execute("""
                INSERT INTO conversations (conversation_id, user_id, stage, questions_asked, questions_max, questions_history, created_at, updated_at)
                VALUES (?, ?, 'intake', 0, 6, '[]', ?, ?)
            """, (conversation_id, user_id, now_iso, now_iso))
            stage = "intake"
            questions_asked = 0
            questions_max = 6
            questions_history = []
            tip_id = None
            thesis = None
        else:
            stage = conv["stage"]
            questions_asked = conv["questions_asked"]
            questions_max = conv["questions_max"]
            questions_history = json.loads(conv["questions_history"] or "[]")
            tip_id = conv["tip_id"]
            thesis = conv["thesis"]

        # Record incoming user message
        user_message_id = f"m_{uuid.uuid4().hex[:8]}"
        user_text = text or ""
        db.execute("""
            INSERT INTO messages (message_id, conversation_id, role, created_at, image_url, blocks, quick_replies)
            VALUES (?, ?, 'user', ?, ?, ?, NULL)
        """, (
            user_message_id,
            conversation_id,
            now_iso,
            image_filename,
            json.dumps([{"type": "text", "content": user_text}])
        ))

        # Check for completed investment statement
        if user_text:
            inv_res = detect_investment(user_text)
            if inv_res.get("detected"):
                draft = inv_res["draft"]
                confirm_token = uuid.uuid4().hex
                expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                db.execute("""
                    INSERT INTO investment_drafts (confirm_token, user_id, draft_data, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (confirm_token, user_id, json.dumps(draft), expires_at, now_iso))

                assistant_blocks = [
                    {
                        "type": "investment_confirm",
                        "confirm_token": confirm_token,
                        "draft": draft
                    }
                ]
                asst_msg_id = f"m_{uuid.uuid4().hex[:8]}"
                db.execute("""
                    INSERT INTO messages (message_id, conversation_id, role, created_at, image_url, blocks, quick_replies)
                    VALUES (?, ?, 'assistant', ?, NULL, ?, '[]')
                """, (asst_msg_id, conversation_id, now_iso, json.dumps(assistant_blocks)))

                return {
                    "conversation_id": conversation_id,
                    "stage": stage,
                    "questions_asked": questions_asked,
                    "questions_max": questions_max,
                    "blocks": assistant_blocks,
                    "quick_replies": []
                }

        # STATE MACHINE TRANSITIONS
        # 1. Intake: if image is present or stage is intake
        if stage == "intake" or image_bytes is not None or (stage == "locked" and image_bytes):
            tip_extraction = extract_tip_from_image(
                image_bytes=image_bytes,
                filename=image_filename,
                text_fallback=user_text
            )

            sender_name = tip_extraction.get("sender") or "Neel"
            stock = tip_extraction["stock"]
            ticker = stock["ticker"]
            claim = tip_extraction["claim"]
            red_flags = tip_extraction["red_flags"]

            source_id, source_info = get_or_create_source(db, user_id, sender_name)
            new_tip_id = f"t_{uuid.uuid4().hex[:8]}"

            price_now, change_7d_pct, note = get_price_and_7d_change(ticker)

            db.execute("""
                INSERT INTO tips (
                    tip_id, source_id, posted_at, raw_text, language, ticker, direction,
                    target_price, horizon_days, confidence_words, extraction_conf, data_origin,
                    user_id, is_demo, stock_name, claim, red_flags
                ) VALUES (?, ?, ?, ?, 'en', ?, 'bullish', NULL, 30, '[]', 0.9, 'synthetic', ?, 0, ?, ?, ?)
            """, (
                new_tip_id, source_id, now_iso, claim, ticker,
                user_id, stock["name"], claim, json.dumps(red_flags)
            ))

            claim_card = {
                "type": "claim_card",
                "tip_id": new_tip_id,
                "sender": sender_name,
                "source_id": source_id,
                "stock": {"name": stock["name"], "ticker": ticker},
                "claim": claim,
                "red_flags": red_flags
            }

            source_record = {
                "type": "source_record",
                "source_id": source_id,
                "source_name": sender_name,
                "tips_total": source_info["tips_total"],
                "tips_worked": source_info["tips_worked"],
                "shrunk_hit_rate": source_info["shrunk_hit_rate"],
                "evidence_level": source_info["evidence_level"],
                "label": source_info["label"]
            }

            context_card = {
                "type": "context_card",
                "ticker": ticker,
                "price_now": price_now,
                "change_7d_pct": change_7d_pct,
                "since_tip_pct": None,
                "note": note
            }

            text_block = {
                "type": "text",
                "content": "What is your own reasoning or thesis for this trade? Why do you believe this move will happen?"
            }

            blocks = [claim_card, source_record, context_card]

            # Check if there is an insight to show
            insight_block = check_for_pattern_insight(db, user_id, ticker, change_7d_pct)
            if insight_block:
                blocks.append(insight_block)

            blocks.append(text_block)

            # Update conversation state
            new_stage = "awaiting_thesis"
            db.execute("""
                UPDATE conversations
                SET stage = ?, tip_id = ?, questions_asked = 0, questions_history = '[]', updated_at = ?
                WHERE conversation_id = ?
            """, (new_stage, new_tip_id, now_iso, conversation_id))

            asst_msg_id = f"m_{uuid.uuid4().hex[:8]}"
            db.execute("""
                INSERT INTO messages (message_id, conversation_id, role, created_at, image_url, blocks, quick_replies)
                VALUES (?, ?, 'assistant', ?, NULL, ?, '[]')
            """, (asst_msg_id, conversation_id, now_iso, json.dumps(blocks)))

            return {
                "conversation_id": conversation_id,
                "stage": new_stage,
                "questions_asked": 0,
                "questions_max": questions_max,
                "blocks": blocks,
                "quick_replies": []
            }

        # 2. Awaiting Thesis: user writes thesis reasoning
        if stage == "awaiting_thesis":
            thesis_text = user_text
            tip_row = db.execute("SELECT * FROM tips WHERE tip_id = ?", (tip_id,)).fetchone()
            ticker = tip_row["ticker"] if tip_row else "TATAMOTORS"

            raw_links = split_thesis(thesis_text)
            evaluated_links = []
            gaps_count = 0

            for lk in raw_links:
                eval_res = check_link(lk["text"], ticker)
                status = eval_res["status"]
                evidence = eval_res["evidence"] if status == "backed" else None
                if status in ("no_evidence", "unchecked"):
                    gaps_count += 1

                link_id = f"l_{uuid.uuid4().hex[:6]}"
                db.execute("""
                    INSERT INTO thesis_links (link_id, conversation_id, tip_id, text, status, evidence_summary, evidence_source_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    link_id, conversation_id, tip_id, lk["text"], status,
                    evidence.get("summary") if evidence else None,
                    evidence.get("source_url") if evidence else None,
                    now_iso
                ))

                evaluated_links.append({
                    "id": link_id,
                    "text": lk["text"],
                    "status": status,
                    "evidence": evidence
                })

            thesis_chain = {
                "type": "thesis_chain",
                "links": evaluated_links,
                "gaps_count": gaps_count,
                "total_links": len(evaluated_links),
                "summary": f"{gaps_count} of {len(evaluated_links)} links have no evidence."
            }

            # Pick the FIRST question
            next_q = select_questions(evaluated_links, questions_history, ticker)
            blocks = [thesis_chain]
            quick_replies = []

            if next_q:
                questions_asked = 1
                questions_history.append(next_q["id"])
                new_stage = "questioning"
                blocks.append({
                    "type": "text",
                    "content": next_q["question"]
                })
                quick_replies = [{"label": "Don't know", "value": "__dont_know__"}]
            else:
                new_stage = "gate"

            db.execute("""
                UPDATE conversations
                SET stage = ?, thesis = ?, questions_asked = ?, questions_history = ?, updated_at = ?
                WHERE conversation_id = ?
            """, (new_stage, thesis_text, questions_asked, json.dumps(questions_history), now_iso, conversation_id))

            asst_msg_id = f"m_{uuid.uuid4().hex[:8]}"
            db.execute("""
                INSERT INTO messages (message_id, conversation_id, role, created_at, image_url, blocks, quick_replies)
                VALUES (?, ?, 'assistant', ?, NULL, ?, ?)
            """, (asst_msg_id, conversation_id, now_iso, json.dumps(blocks), json.dumps(quick_replies)))

            return {
                "conversation_id": conversation_id,
                "stage": new_stage,
                "questions_asked": questions_asked,
                "questions_max": questions_max,
                "blocks": blocks,
                "quick_replies": quick_replies
            }

        # 3. Questioning stage: user responds to question or sends __dont_know__
        if stage == "questioning":
            if user_text.strip() == "__dont_know__":
                # Mark latest unchecked link as no_evidence
                latest_link = db.execute("""
                    SELECT link_id FROM thesis_links
                    WHERE conversation_id = ? AND status = 'unchecked'
                    ORDER BY created_at DESC LIMIT 1
                """, (conversation_id,)).fetchone()
                if latest_link:
                    db.execute("""
                        UPDATE thesis_links SET status = 'no_evidence'
                        WHERE link_id = ?
                    """, (latest_link["link_id"],))

            tip_row = db.execute("SELECT * FROM tips WHERE tip_id = ?", (tip_id,)).fetchone()
            ticker = tip_row["ticker"] if tip_row else "TATAMOTORS"

            db_links = db.execute("""
                SELECT * FROM thesis_links WHERE conversation_id = ?
            """, (conversation_id,)).fetchall()
            links_list = [dict(l) for l in db_links]

            # Check if we should ask another question
            next_q = None
            if questions_asked < questions_max:
                next_q = select_questions(links_list, questions_history, ticker)

            if next_q and questions_asked + 1 <= questions_max:
                questions_asked += 1
                questions_history.append(next_q["id"])
                blocks = [
                    {
                        "type": "text",
                        "content": next_q["question"]
                    }
                ]
                quick_replies = [{"label": "Don't know", "value": "__dont_know__"}]
                new_stage = "questioning"
            else:
                # Reached question limit or exhausted pool -> move to GATE
                new_stage = "gate"
                quick_replies = []

                # Count gaps
                gaps = db.execute("""
                    SELECT COUNT(*) FROM thesis_links
                    WHERE conversation_id = ? AND status != 'backed'
                """, (conversation_id,)).fetchone()[0]

                # Create unlocked decision
                decision_id = f"d_{uuid.uuid4().hex[:8]}"
                price_now, change_7d_pct, _ = get_price_and_7d_change(ticker)
                db.execute("""
                    INSERT INTO decisions (
                        decision_id, user_id, tip_id, action, timeframe_days, exit_target,
                        max_loss_pct, confidence, thesis, gaps_count, locked, locked_at,
                        created_at, price_at_decision, jump_7d_at_decision, outcome_loss, is_demo
                    ) VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?, ?, 0, NULL, ?, ?, ?, 0, 0)
                """, (decision_id, user_id, tip_id, thesis, gaps, now_iso, price_now, change_7d_pct))

                blocks = [
                    {
                        "type": "text",
                        "content": "All trade audit questions complete. Review your trade parameters in the decision gate below to lock your decision."
                    },
                    {
                        "type": "decision_gate",
                        "decision_id": decision_id,
                        "tip_id": tip_id,
                        "required_fields": ["action", "timeframe_days", "exit_target", "max_loss_pct", "confidence"],
                        "values": {
                            "action": None,
                            "timeframe_days": None,
                            "exit_target": None,
                            "max_loss_pct": None,
                            "confidence": None
                        },
                        "locked": False,
                        "locked_at": None
                    }
                ]

            db.execute("""
                UPDATE conversations
                SET stage = ?, questions_asked = ?, questions_history = ?, updated_at = ?
                WHERE conversation_id = ?
            """, (new_stage, questions_asked, json.dumps(questions_history), now_iso, conversation_id))

            asst_msg_id = f"m_{uuid.uuid4().hex[:8]}"
            db.execute("""
                INSERT INTO messages (message_id, conversation_id, role, created_at, image_url, blocks, quick_replies)
                VALUES (?, ?, 'assistant', ?, NULL, ?, ?)
            """, (asst_msg_id, conversation_id, now_iso, json.dumps(blocks), json.dumps(quick_replies)))

            return {
                "conversation_id": conversation_id,
                "stage": new_stage,
                "questions_asked": questions_asked,
                "questions_max": questions_max,
                "blocks": blocks,
                "quick_replies": quick_replies
            }

        # 4. Gate / Locked / Chitchat
        if stage in ("gate", "locked"):
            blocks = [
                {
                    "type": "text",
                    "content": "This decision checkpoint is already complete. You can lock your decision via the gate above or send a new tip screenshot to start an audit."
                }
            ]
            quick_replies = []
            return {
                "conversation_id": conversation_id,
                "stage": stage,
                "questions_asked": questions_asked,
                "questions_max": questions_max,
                "blocks": blocks,
                "quick_replies": quick_replies
            }

        # Chitchat fallback
        blocks = [
            {
                "type": "text",
                "content": "Welcome to Tip Checkpoint. Send a stock tip screenshot or text to audit the claim before taking a position."
            }
        ]
        return {
            "conversation_id": conversation_id,
            "stage": "chitchat",
            "questions_asked": 0,
            "questions_max": 6,
            "blocks": blocks,
            "quick_replies": []
        }
