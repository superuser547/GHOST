from __future__ import annotations

from typing import Callable, List

from app.models import Report, ValidationIssue, ValidationIssueLevel, ValidationResult

ValidationRule = Callable[[Report], List[ValidationIssue]]

#: Global registry of validation rules.
RULES: List[ValidationRule] = []


def validate_report(report: Report) -> ValidationResult:
    """
    Run all registered validation rules against the given report and
    aggregate their issues into a single ValidationResult.

    At this stage (C2) the RULES registry is empty, so the function will
    always return an empty result (no errors, no warnings).
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
