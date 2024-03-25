from domain.user_schemas import UserReturnForm
from fastapi import APIRouter

health_check_router = APIRouter(tags=["Heath check"])


@health_check_router.get("/", response_model=UserReturnForm, status_code=200)
async def health_check():
    return UserReturnForm(message="Healthy! :)")
