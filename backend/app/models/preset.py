from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class FormattingPreset(BaseModel):
    """
    Пресет оформления отчёта.

    Пока содержит только метаданные, достаточные для UI.
    Конкретные параметры (поля, шрифты, стили) будут использоваться
    по `id` внутри сервисов генерации DOCX.

    Поля:
    - id: машинное имя пресета (например, "misis_v1").
    - title: человекочитаемое название (для отображения в UI).
    - description: краткое описание, что это за пресет.
    - is_default: флаг пресета по умолчанию.
    """

    id: str
    title: str
    description: Optional[str] = None
    is_default: bool = False
