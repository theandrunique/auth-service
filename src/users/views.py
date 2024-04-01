from fastapi import APIRouter

router = APIRouter(tags=["users"])


@router.get("/me")
async def get_me():
    ...


