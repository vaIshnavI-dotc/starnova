import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import connect
from app.core.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=4)


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.post("/signup", status_code=201)
def signup(req: SignupRequest):
    email_clean = req.email.strip().lower()
    with connect() as db:
        existing = db.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?",
            (email_clean,)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "validation_error",
                    "message": "Email is already registered",
                    "details": {"email": "already_exists"}
                }
            )

        user_id = f"u_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        db.execute("""
            INSERT INTO users (id, name, email, password_hash, created_at, is_demo)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (
            user_id,
            req.name.strip(),
            email_clean,
            hash_password(req.password),
            now
        ))

    token = create_token(user_id, email_clean)
    return {
        "token": token,
        "user": {
            "id": user_id,
            "name": req.name.strip(),
            "email": email_clean
        }
    }


@router.post("/login", status_code=200)
def login(req: LoginRequest):
    email_clean = req.email.strip().lower()
    with connect() as db:
        user = db.execute(
            "SELECT id, name, email, password_hash FROM users WHERE LOWER(email) = ?",
            (email_clean,)
        ).fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "unauthorized",
                "message": "Invalid email or password",
                "details": {}
            }
        )

    token = create_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.get("/me", status_code=200)
def me(user: dict = Depends(get_current_user)):
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }
