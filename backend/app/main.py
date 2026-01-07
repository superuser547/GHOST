from fastapi import FastAPI

app = FastAPI(
    title="GHOST Report Builder API",
    description="Backend API for the GHOST report constructor (MISIS / GOST).",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple healthcheck endpoint to verify that the backend is running."""
    return {"status": "ok"}
