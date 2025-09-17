from fastapi import APIRouter


router = APIRouter(tags=["default"])


@router.get("/health")
def health():
    return {"status": "ok"}


