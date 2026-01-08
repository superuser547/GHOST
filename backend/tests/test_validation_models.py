from uuid import uuid4

from app.models import ValidationIssue, ValidationIssueLevel, ValidationResult


def test_validation_issue_basic():
    block_id = uuid4()
    issue = ValidationIssue(
        code="SECTION_ORDER",
        level=ValidationIssueLevel.ERROR,
        message="Разделы идут в неправильном порядке.",
        block_id=block_id,
        hint="Проверьте порядок: Введение, Основная часть, Заключение.",
    )

    assert issue.code == "SECTION_ORDER"
    assert issue.level is ValidationIssueLevel.ERROR
    assert "неправильном порядке" in issue.message
    assert issue.block_id == block_id
    assert "Проверьте порядок" in (issue.hint or "")


def test_validation_result_is_valid_property():
    result = ValidationResult()
    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []

    error_issue = ValidationIssue(
        code="EMPTY_SECTION",
        level=ValidationIssueLevel.ERROR,
        message="Раздел не должен быть пустым.",
    )
    warning_issue = ValidationIssue(
        code="SHORT_CONCLUSION",
        level=ValidationIssueLevel.WARNING,
        message="Заключение слишком короткое.",
    )

    result.errors.append(error_issue)
    result.warnings.append(warning_issue)

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert len(result.warnings) == 1


def test_validation_result_serialization():
    issue = ValidationIssue(
        code="NO_INTRO",
        level=ValidationIssueLevel.ERROR,
        message="В отчёте отсутствует раздел ВВЕДЕНИЕ.",
    )

    result = ValidationResult(errors=[issue])

    data = result.model_dump()
    assert "errors" in data
    assert "warnings" in data
    assert isinstance(data["errors"], list)
    assert data["warnings"] == []

    first = data["errors"][0]
    assert first["code"] == "NO_INTRO"
    assert first["level"] == "error"
    assert "отсутствует раздел ВВЕДЕНИЕ" in first["message"]

    restored = ValidationResult(**data)
    assert len(restored.errors) == 1
    assert restored.errors[0].code == "NO_INTRO"
    assert restored.errors[0].level is ValidationIssueLevel.ERROR
