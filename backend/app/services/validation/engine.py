from __future__ import annotations

from typing import Callable, List

from app.models import Report, ValidationIssue, ValidationIssueLevel, ValidationResult

ValidationRule = Callable[[Report], List[ValidationIssue]]

#: Глобальный реестр правил валидации.
RULES: List[ValidationRule] = []


def validate_report(report: Report) -> ValidationResult:
    """
    Запускает все зарегистрированные правила валидации для переданного отчёта и
    агрегирует их замечания в единый ValidationResult.

    На текущем этапе (C2) реестр RULES пуст, поэтому функция всегда возвращает
    пустой результат (без ошибок и предупреждений).
    """

    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []

    for rule in RULES:
        issues = rule(report)
        for issue in issues:
            if issue.level == ValidationIssueLevel.ERROR:
                errors.append(issue)
            else:
                warnings.append(issue)

    return ValidationResult(errors=errors, warnings=warnings)


from . import rules  # noqa: F401,E402
