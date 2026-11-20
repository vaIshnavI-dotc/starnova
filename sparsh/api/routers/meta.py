from fastapi import APIRouter

router = APIRouter(tags=["meta"])

@router.get("/meta")
def get_meta():
    return {"name": "Sparsh", "version": "0.1.0", "status": "scaffold"}
