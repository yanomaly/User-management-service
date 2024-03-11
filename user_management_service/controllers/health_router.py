from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

health_check_router = APIRouter(tags=["Heath check"])


@health_check_router.get("/")
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Healthy! :)"}
    )
