from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkType(str, Enum):
    PRACTICE = "practice"
    LAB = "lab"
    ESSAY = "essay"
    COURSE = "course"
    OTHER = "other"


class ReportBlockType(str, Enum):
    TITLE_PAGE = "title_page"
    TOC = "toc"
    SECTION = "section"
    SUBSECTION = "subsection"
    TEXT = "text"
    LIST = "list"
    TABLE = "table"
    FIGURE = "figure"
    REFERENCES = "references"
    APPENDIX = "appendix"


class ReportMeta(BaseModel):
    """
    Метаданные отчёта для генерации титульной страницы
    и формирования имени файла.
    """

    preset: str = "misis_v1"

    work_type: WorkType
    work_number: Optional[int] = None

    discipline: str
    topic: str

    student_full_name: str
    group: str
    semester: str

    direction_code: str
    direction_name: str
    department: str

    teacher_full_name: str
    submission_date: date


class BaseBlock(BaseModel):
    """
    Базовый блок в структуре отчёта.

    Специализированные типы блоков (раздел, текст, таблица, рисунок и т.д.)
    будут расширять эту модель в следующих коммитах.
    """

    id: UUID = Field(default_factory=uuid4)
    type: ReportBlockType
    children: List["BaseBlock"] = Field(default_factory=list)


class SectionBlock(BaseBlock):
    """
    Верхнеуровневый раздел отчёта (например, ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ).
    """

    type: Literal[ReportBlockType.SECTION] = ReportBlockType.SECTION
    title: str
    special_kind: Optional[Literal["INTRO", "CONCLUSION", "REFERENCES"]] = None


class SubsectionBlock(BaseBlock):
    """
    Подраздел внутри раздела (уровень 2 или 3).
    """

    type: Literal[ReportBlockType.SUBSECTION] = ReportBlockType.SUBSECTION
    level: Literal[2, 3]
    title: str


class TextBlock(BaseBlock):
    """
    Текстовый блок: один или несколько абзацев.
    """

    type: Literal[ReportBlockType.TEXT] = ReportBlockType.TEXT
    text: str


class ListBlock(BaseBlock):
    """
    Маркированный или нумерованный список.
    """

    type: Literal[ReportBlockType.LIST] = ReportBlockType.LIST
    list_type: Literal["bulleted", "numbered"]
    items: List[str] = Field(default_factory=list)


class TableBlock(BaseBlock):
    """
    Таблица с подписью и двумерными данными.
    """

    type: Literal[ReportBlockType.TABLE] = ReportBlockType.TABLE
    caption: str
    rows: List[List[str]] = Field(default_factory=list)


class FigureBlock(BaseBlock):
    """
    Рисунок (изображение) с подписью.
    """

    type: Literal[ReportBlockType.FIGURE] = ReportBlockType.FIGURE
    caption: str
    file_name: str


class ReferencesBlock(BaseBlock):
    """
    Список использованных источников.
    """

    type: Literal[ReportBlockType.REFERENCES] = ReportBlockType.REFERENCES
    items: List[str] = Field(default_factory=list)


class AppendixBlock(BaseBlock):
    """
    Приложение (например, ПРИЛОЖЕНИЕ А) с собственными блоками.
    """

    type: Literal[ReportBlockType.APPENDIX] = ReportBlockType.APPENDIX
    label: str
    title: str


BaseBlock.model_rebuild()
