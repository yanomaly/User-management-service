from fastapi import FastAPI

from user_management_service.router import health_check_router

app = FastAPI()

app.include_router(health_check_router)
