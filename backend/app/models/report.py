from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class WorkType(str, Enum):
    PRACTICE = "practice"
    LAB = "lab"
    ESSAY = "essay"
    COURSE = "course"
    OTHER = "other"


class ReportMeta(BaseModel):
    """
    Meta-information about the report used both for title page
    generation and for file naming.
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
