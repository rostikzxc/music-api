from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import UsernameTaken
from app.routers.auth import router as auth_router

app = FastAPI(title="Music API")

app.include_router(auth_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(UsernameTaken)
async def username_taken_handler(request: Request, exc: UsernameTaken) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Username already taken"})
