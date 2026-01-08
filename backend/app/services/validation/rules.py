from __future__ import annotations

from typing import Iterable, List

from app.models import (
    BaseBlock,
    FigureBlock,
    ListBlock,
    Report,
    SectionBlock,
    TableBlock,
    ValidationIssue,
    ValidationIssueLevel,
)

from .engine import RULES


def iter_blocks(report: Report) -> Iterable[BaseBlock]:
    """
    Depth-first traversal of all blocks in the report, including nested children.
    """

    stack: List[BaseBlock] = list(report.blocks)
    while stack:
        block = stack.pop()
        yield block
        if block.children:
            stack.extend(reversed(block.children))


def rule_required_sections_present(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    sections: List[SectionBlock] = [
        block for block in report.blocks if isinstance(block, SectionBlock)
    ]

    has_intro = any(section.special_kind == "INTRO" for section in sections)
    has_conclusion = any(section.special_kind == "CONCLUSION" for section in sections)

    if not has_intro:
        issues.append(
            ValidationIssue(
                code="REQUIRED_SECTIONS_PRESENT",
                level=ValidationIssueLevel.ERROR,
                message="В отчёте отсутствует раздел ВВЕДЕНИЕ.",
            )
        )

    if not has_conclusion:
        issues.append(
            ValidationIssue(
                code="REQUIRED_SECTIONS_PRESENT",
                level=ValidationIssueLevel.ERROR,
                message="В отчёте отсутствует раздел ЗАКЛЮЧЕНИЕ.",
            )
        )

    return issues


def rule_section_order(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    indexed_sections = [
        (idx, block)
        for idx, block in enumerate(report.blocks)
        if isinstance(block, SectionBlock)
    ]

    if not indexed_sections:
        return issues

    intro_positions = [
        idx for idx, section in indexed_sections if section.special_kind == "INTRO"
    ]
    conclusion_positions = [
        idx for idx, section in indexed_sections if section.special_kind == "CONCLUSION"
    ]

    if intro_positions:
        first_section_idx = indexed_sections[0][0]
        if min(intro_positions) != first_section_idx:
            issues.append(
                ValidationIssue(
                    code="SECTION_ORDER",
                    level=ValidationIssueLevel.ERROR,
                    message="Раздел ВВЕДЕНИЕ должен быть первым разделом отчёта.",
                )
            )

    if conclusion_positions:
        last_section_idx = indexed_sections[-1][0]
        if max(conclusion_positions) != last_section_idx:
            issues.append(
                ValidationIssue(
                    code="SECTION_ORDER",
                    level=ValidationIssueLevel.ERROR,
                    message="Раздел ЗАКЛЮЧЕНИЕ должен быть последним разделом отчёта.",
                )
            )

    if intro_positions and conclusion_positions:
        if max(intro_positions) >= min(conclusion_positions):
            issues.append(
                ValidationIssue(
                    code="SECTION_ORDER",
                    level=ValidationIssueLevel.ERROR,
                    message="Раздел ВВЕДЕНИЕ должен располагаться перед ЗАКЛЮЧЕНИЕМ.",
                )
            )

    return issues


def rule_non_empty_lists(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if isinstance(block, ListBlock) and not block.items:
            issues.append(
                ValidationIssue(
                    code="NON_EMPTY_LISTS",
                    level=ValidationIssueLevel.ERROR,
                    message="Список не должен быть пустым.",
                    block_id=block.id,
                )
            )

    return issues


def rule_figure_has_caption(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if isinstance(block, FigureBlock):
            if not block.caption or not block.caption.strip():
                issues.append(
                    ValidationIssue(
                        code="FIGURE_HAS_CAPTION",
                        level=ValidationIssueLevel.ERROR,
                        message="У каждого рисунка должна быть подпись.",
                        block_id=block.id,
                    )
                )

    return issues


def rule_table_has_caption(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if isinstance(block, TableBlock):
            if not block.caption or not block.caption.strip():
                issues.append(
                    ValidationIssue(
                        code="TABLE_HAS_CAPTION",
                        level=ValidationIssueLevel.ERROR,
                        message="У каждой таблицы должна быть подпись.",
                        block_id=block.id,
                    )
                )

    return issues


RULES.extend(
    [
        rule_required_sections_present,
        rule_section_order,
        rule_non_empty_lists,
        rule_figure_has_caption,
        rule_table_has_caption,
    ]
)
