import uvicorn
from config import Settings
from controllers.auth_routers import auth_router
from controllers.health_router import health_check_router
from controllers.user_routers import user_router, users_router
from fastapi import FastAPI

app = FastAPI(root_path="/ums")

app.include_router(health_check_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(users_router)

settings = Settings()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
