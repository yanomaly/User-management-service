from domain.base import ReturnMessage
from fastapi import APIRouter

health_check_router = APIRouter(tags=["Heath check"])


@health_check_router.get("/", response_model=ReturnMessage, status_code=200)
async def health_check():
    return ReturnMessage(message="Healthy! :)")
