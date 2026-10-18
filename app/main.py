from fastapi import FastAPI

app = FastAPI(title="Music API")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
