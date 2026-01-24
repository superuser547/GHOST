from __future__ import annotations

from typing import List

from fastapi import APIRouter

from app.models.preset import FormattingPreset
from app.services.presets import get_all_presets

router = APIRouter(
    prefix="/api/v1/presets",
    tags=["presets"],
)


@router.get("/", response_model=List[FormattingPreset])
def list_presets() -> List[FormattingPreset]:
    """
    Возвращает список доступных пресетов оформления.

    Используется фронтендом для заполнения выпадающего списка выбора
    оформления отчёта.
    """
    return get_all_presets()
