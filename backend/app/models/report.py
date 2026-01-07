from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional
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


BaseBlock.model_rebuild()
