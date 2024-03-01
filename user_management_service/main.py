import uvicorn
from auth.router import auth_router
from config import Settings
from fastapi import FastAPI
from router import health_check_router
from users.router import user_router, users_router

app = FastAPI()

app.include_router(health_check_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(users_router)

settings = Settings()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
