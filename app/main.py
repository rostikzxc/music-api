from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import InvalidCredentials, InvalidToken, UserDeactivated, UsernameTaken
from app.routers.auth import router as auth_router

app = FastAPI(title="Music API")

app.include_router(auth_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(UsernameTaken)
async def username_taken_handler(request: Request, exc: UsernameTaken) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Username already taken"})


@app.exception_handler(InvalidCredentials)
async def invalid_creadentials_handler(reuqest: Request, exc: InvalidCredentials) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid username or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(UserDeactivated)
async def user_deactivated_handler(request: Request, exc: UserDeactivated) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "User deactivated"})


@app.exception_handler(InvalidToken)
async def invalid_token_handler(request: Request, exc: InvalidToken) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
