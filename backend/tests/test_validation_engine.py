from datetime import date
from typing import List

from app.models import (
    Report,
    ReportMeta,
    ValidationIssue,
    ValidationIssueLevel,
    WorkType,
)
from app.services.validation.engine import RULES, validate_report


def test_validate_report_with_empty_rules_returns_empty_result():
    assert RULES == []

    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Тестовый отчёт",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    report = Report(meta=meta, blocks=[])

    result = validate_report(report)

    assert result.errors == []
    assert result.warnings == []
    assert result.is_valid is True


def test_validate_report_applies_rules_and_aggregates_issues():
    original_rules = list(RULES)
    RULES.clear()

    def dummy_rule(report: Report) -> List[ValidationIssue]:
        return [
            ValidationIssue(
                code="DUMMY_ERROR",
                level=ValidationIssueLevel.ERROR,
                message="Тестовая ошибка.",
            ),
            ValidationIssue(
                code="DUMMY_WARNING",
                level=ValidationIssueLevel.WARNING,
                message="Тестовое предупреждение.",
            ),
        ]

    RULES.append(dummy_rule)

    meta = ReportMeta(
        work_type=WorkType.ESSAY,
        work_number=None,
        discipline="Физика",
        topic="Тест",
        student_full_name="Тест Тест Тест",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра",
        teacher_full_name="Преподаватель Преподаватель",
        submission_date=date(2025, 2, 1),
    )

    report = Report(meta=meta, blocks=[])

    result = validate_report(report)

    assert len(result.errors) == 1
    assert len(result.warnings) == 1
    assert result.errors[0].code == "DUMMY_ERROR"
    assert result.warnings[0].code == "DUMMY_WARNING"
    assert result.is_valid is False

    RULES.clear()
    RULES.extend(original_rules)
