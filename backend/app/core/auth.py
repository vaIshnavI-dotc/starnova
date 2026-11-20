import os
from datetime import datetime, timezone, timedelta
from typing import Optional
import bcrypt
import jwt
from fastapi import Header, HTTPException, Depends
from app.core.database import connect

JWT_SECRET = os.getenv("JWT_SECRET", "starnova-signalnoise-jwt-secret-key-32charsmin")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "unauthorized",
                "message": "Missing or invalid Authorization header",
                "details": {}
            }
        )
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "unauthorized",
                "message": "Invalid or expired token",
                "details": {}
            }
        )
    user_id = payload["sub"]
    with connect() as db:
        user = db.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "unauthorized",
                "message": "User not found",
                "details": {}
            }
        )
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    with connect() as db:
        user = db.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    if not user:
        return None
    return {"id": user["id"], "name": user["name"], "email": user["email"]}
