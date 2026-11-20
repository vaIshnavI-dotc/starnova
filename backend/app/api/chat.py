import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from app.core.database import connect
from app.core.auth import get_current_user
from app.services.chat_flow import process_chat_message

router = APIRouter(tags=["chat"])


@router.post("/chat/message", status_code=200)
async def post_chat_message(
    conversation_id: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user)
):
    if not text and not image:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "validation_error",
                "message": "At least one of text or image is required",
                "details": {}
            }
        )

    image_bytes = None
    image_filename = None
    if image:
        image_bytes = await image.read()
        image_filename = image.filename

    return process_chat_message(
        user=user,
        conversation_id=conversation_id,
        text=text,
        image_bytes=image_bytes,
        image_filename=image_filename
    )


@router.get("/conversations/{conversation_id}", status_code=200)
def get_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    with connect() as db:
        conv = db.execute("""
            SELECT * FROM conversations
            WHERE conversation_id = ? AND user_id = ?
        """, (conversation_id, user["id"])).fetchone()

        if not conv:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "not_found",
                    "message": f"Conversation {conversation_id} not found",
                    "details": {}
                }
            )

        messages_rows = db.execute("""
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,)).fetchall()

    messages = []
    for m in messages_rows:
        blocks = json.loads(m["blocks"] or "[]")
        messages.append({
            "id": m["message_id"],
            "role": m["role"],
            "created_at": m["created_at"],
            "image_url": m["image_url"],
            "blocks": blocks
        })

    return {
        "conversation_id": conv["conversation_id"],
        "stage": conv["stage"],
        "questions_asked": conv["questions_asked"],
        "questions_max": conv["questions_max"],
        "messages": messages
    }
