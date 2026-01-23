from fastapi import FastAPI

from app.api.v1.reports import router as reports_router

app = FastAPI(
    title="API конструктора отчётов GHOST",
    description="API серверной части конструктора отчётов GHOST (МИСИС / ГОСТ).",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Простой эндпоинт проверки состояния для проверки работы бэкенда."""
    return {"status": "ok"}


app.include_router(reports_router, prefix="/api/v1")
