import uvicorn
from fastapi import FastAPI

from user_management_service.router import health_check_router

app = FastAPI()

app.include_router(health_check_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
