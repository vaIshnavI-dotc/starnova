from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/archive", tags=["archive"])

@router.get("/verify/{archive_id}")
def verify_archive(archive_id: str):
    raise HTTPException(status_code=501, detail="Archive verification not implemented")

@router.get("/chain/head")
def chain_head():
    raise HTTPException(status_code=501, detail="Hash-chain archive not implemented")
