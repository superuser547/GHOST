from __future__ import annotations

from typing import Dict, List, Optional

from app.models.preset import FormattingPreset

# Словарь всех доступных пресетов, ключ — id пресета.
_PRESETS: Dict[str, FormattingPreset] = {
    "misis_v1": FormattingPreset(
        id="misis_v1",
        title="МИСИС, ГОСТ 7.32-2017",
        description="Оформление отчёта по методическим указаниям НИТУ «МИСиС».",
        is_default=True,
    ),
}


def get_all_presets() -> List[FormattingPreset]:
    """
    Возвращает список всех доступных пресетов оформления.
    """
    return list(_PRESETS.values())


def get_preset(preset_id: str) -> Optional[FormattingPreset]:
    """
    Возвращает пресет по id или None, если такого нет.
    """
    return _PRESETS.get(preset_id)
