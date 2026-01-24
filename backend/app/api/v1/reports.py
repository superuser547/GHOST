from __future__ import annotations

import base64
import binascii
import re
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models import Report, ValidationResult
from app.services.docx import build_docx
from app.services.validation.engine import validate_report


class ExportDocxRequest(BaseModel):
    """
    Тело запроса для экспорта отчёта в DOCX.

    Поля:
    - report: структура отчёта (метаданные + блоки).
    - preset_id: id пресета оформления (по умолчанию "misis_v1").
    - title_template: содержимое DOCX-файла шаблона титульного листа
      в виде bytes (FastAPI/Pydantic передаёт его как base64-строку).
    """

    report: Report
    preset_id: str = "misis_v1"
    title_template: bytes | None = None


def _slugify(value: str) -> str:
    """
    Простейший slugify: оставляет только буквы/цифры/подчёркивания/дефисы,
    пробелы заменяет на подчёркивания.

    Используется для формирования имени файла.
    """
    value = value.strip().replace(" ", "_")
    value = re.sub(r"[^\w\-]+", "", value, flags=re.ASCII)
    return value or "report"


def _build_report_filename(report: Report) -> str:
    """
    Формирует имя итогового файла по метаданным отчёта.

    Формат (пример):
    Иванов_Иван_Иванович_ББИ-24-3_Информатика_Практическая_работа_1.docx
    """
    meta = report.meta

    student_part = _slugify(meta.student_full_name)
    group_part = _slugify(meta.group)
    discipline_part = _slugify(meta.discipline)

    work_type_name = (
        meta.work_type_custom
        if meta.work_type_custom
        else meta.work_type.name.capitalize()
    )
    work_type_part = _slugify(work_type_name)

    parts = [student_part, group_part, discipline_part, work_type_part]

    if meta.work_number is not None:
        parts.append(str(meta.work_number))

    base_name = "_".join(filter(None, parts)) or "report"
    return f"{base_name}.docx"


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


@router.post("/export/docx")
def export_report_docx(payload: ExportDocxRequest):
    """
    Экспорт отчёта в DOCX.

    Последовательность:
    1. Валидация отчёта.
       - Если есть ошибки (errors), вернуть 422 и ValidationResult.
       - Предупреждения (warnings) не блокируют экспорт.
    2. Построение DOCX по структуре отчёта и пресету.
    3. Возврат файла с корректным Content-Type и Content-Disposition.
    """
    validation_result = validate_report(payload.report)

    if validation_result.errors:
        raise HTTPException(
            status_code=422,
            detail=validation_result.model_dump(),
        )

    title_template = payload.title_template
    if title_template is not None and not title_template.startswith(b"PK"):
        try:
            decoded = base64.b64decode(title_template, validate=True)
        except binascii.Error:
            decoded = None
        if decoded:
            title_template = decoded

    docx_bytes = build_docx(
        report=payload.report,
        preset_id=payload.preset_id,
        title_template=title_template,
    )

    filename = _build_report_filename(payload.report)

    return StreamingResponse(
        BytesIO(docx_bytes),
        media_type=(
            "application/vnd.openxmlformats-officedocument." "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
