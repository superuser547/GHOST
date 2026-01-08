from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ValidationIssueLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    """
    Single validation issue produced by the validation engine.

    - code: short machine-readable identifier of the rule.
    - level: severity (error or warning).
    - message: human-readable description (for UI).
    - block_id: optional block identifier this issue refers to.
    - hint: optional suggestion on how to fix the issue.
    """

    code: str
    level: ValidationIssueLevel
    message: str
    block_id: Optional[UUID] = None
    hint: Optional[str] = None


class ValidationResult(BaseModel):
    """
    Result of validating a report.

    - errors: list of validation issues with level=ERROR
    - warnings: list of validation issues with level=WARNING
    """

    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """
        Convenience property: returns True if there are no errors.
        Warnings do not affect validity.
        """

        return not self.errors
