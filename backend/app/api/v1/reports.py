from __future__ import annotations

from fastapi import APIRouter

from app.models import Report, ValidationResult
from app.services.validation.engine import validate_report

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.post("/validate", response_model=ValidationResult)
def validate_report_endpoint(report: Report) -> ValidationResult:
    """
    Проверяет отчёт по всем подключённым правилам валидации.

    Тело запроса: Report (JSON).
    Ответ: ValidationResult (JSON) со списками ошибок и предупреждений.
    """

    return validate_report(report)
