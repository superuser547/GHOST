from __future__ import annotations

import re
from typing import Iterable, List

from app.models import (
    AppendixBlock,
    BaseBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    Report,
    SectionBlock,
    SubsectionBlock,
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


def rule_list_marker_format(report: Report) -> List[ValidationIssue]:
    """
    Проверяет, что элементы списков не содержат вручную вставленных маркеров
    или номеров (например, "- пункт" или "1) пункт").

    Маркер/нумерация должны задаваться через поле `list_type`, а не в тексте.
    """
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if not isinstance(block, ListBlock):
            continue

        for item in block.items:
            if LIST_MARKER_PREFIX_RE.match(item or ""):
                issues.append(
                    ValidationIssue(
                        code="LIST_MARKER_FORMAT",
                        level=ValidationIssueLevel.WARNING,
                        message=(
                            "Элементы списка не должны содержать вручную "
                            "вставленные маркеры или номера (например, '- ' "
                            "или '1)'). Укажите тип списка в `list_type`, а "
                            "формат маркера будет настроен автоматически."
                        ),
                        block_id=block.id,
                    )
                )
                break

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


def rule_figure_requirements(report: Report) -> List[ValidationIssue]:
    """
    Дополнительные требования к подписям рисунков.

    Подпись должна иметь вид 'Рисунок N – Название' (или аналогичные
    варианты с 'Рис.' / 'Figure' / 'Fig.'), то есть:

    - начинается с допустимого префикса и номера (проверяет FIGURE_PATTERN);
    - содержит символ '–' и текст после него.
    """
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if not isinstance(block, FigureBlock):
            continue

        caption = (block.caption or "").strip()
        if not caption:
            continue

        dash_index = caption.find("–")
        if dash_index == -1 or caption[dash_index + 1 :].strip() == "":
            issues.append(
                ValidationIssue(
                    code="FIGURE_REQUIREMENTS",
                    level=ValidationIssueLevel.WARNING,
                    message=(
                        "Подпись рисунка должна иметь вид "
                        "'Рисунок N – Название' согласно методическим "
                        "указаниям."
                    ),
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


def rule_table_requirements(report: Report) -> List[ValidationIssue]:
    """
    Дополнительные требования к таблицам:

    - Подпись должна иметь вид 'Таблица N – Название'.
    - Таблица не должна содержать отдельную колонку с порядковым номером
      ('№', '№ п/п', 'Номер' и т. п.) в первой колонке шапки.
    """
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if not isinstance(block, TableBlock):
            continue

        caption = (block.caption or "").strip()
        if caption:
            if TABLE_PATTERN.match(caption):
                dash_index = caption.find("–")
                if dash_index == -1 or caption[dash_index + 1 :].strip() == "":
                    issues.append(
                        ValidationIssue(
                            code="TABLE_REQUIREMENTS",
                            level=ValidationIssueLevel.WARNING,
                            message=(
                                "Подпись таблицы должна иметь вид "
                                "'Таблица N – Название' согласно методическим "
                                "указаниям."
                            ),
                            block_id=block.id,
                        )
                    )

        if not block.rows:
            continue

        header_row = block.rows[0]
        if not header_row:
            continue

        first_cell = (header_row[0] or "").strip().lower()
        if first_cell.startswith("№") or "номер" in first_cell:
            issues.append(
                ValidationIssue(
                    code="TABLE_REQUIREMENTS",
                    level=ValidationIssueLevel.WARNING,
                    message=(
                        "Таблица не должна содержать отдельную колонку с "
                        "порядковым номером (например, '№' или '№ п/п') "
                        "согласно методическим указаниям."
                    ),
                    block_id=block.id,
                )
            )

    return issues


def rule_section_ends_with_media(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if isinstance(block, (SectionBlock, SubsectionBlock)):
            if not block.children:
                continue
            last_child = block.children[-1]
            if isinstance(last_child, (FigureBlock, TableBlock)):
                issues.append(
                    ValidationIssue(
                        code="SECTION_ENDS_WITH_MEDIA",
                        level=ValidationIssueLevel.ERROR,
                        message=(
                            "Раздел или подраздел не должен оканчиваться рисунком "
                            "или таблицей. После рисунка/таблицы должен следовать "
                            "текст."
                        ),
                        block_id=last_child.id,
                    )
                )

    return issues


def rule_appendix_labels_unique(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    appendices: List[AppendixBlock] = [
        block for block in report.blocks if isinstance(block, AppendixBlock)
    ]

    by_label: dict[str, List[AppendixBlock]] = {}
    for appendix in appendices:
        by_label.setdefault(appendix.label, []).append(appendix)

    for label, blocks in by_label.items():
        if len(blocks) > 1:
            for block in blocks:
                issues.append(
                    ValidationIssue(
                        code="APPENDIX_LABELS_UNIQUE",
                        level=ValidationIssueLevel.ERROR,
                        message=(
                            f"Метка приложения '{label}' используется более одного "
                            "раза."
                        ),
                        block_id=block.id,
                    )
                )

    return issues


def rule_appendix_labels_order(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    appendices: List[AppendixBlock] = [
        block for block in report.blocks if isinstance(block, AppendixBlock)
    ]

    if len(appendices) <= 1:
        return issues

    labels = [appendix.label for appendix in appendices]
    sorted_labels = sorted(labels)

    if labels != sorted_labels:
        issues.append(
            ValidationIssue(
                code="APPENDIX_LABELS_ORDER",
                level=ValidationIssueLevel.WARNING,
                message="Приложения должны идти в алфавитном порядке (А, Б, В, ...).",
            )
        )

    return issues


FIGURE_PATTERN = re.compile(r"^\s*(Рисунок|Рис\.|Figure|Fig\.)\s+(\d+)")
TABLE_PATTERN = re.compile(r"^\s*(Таблица|Табл\.|Table|Tab\.)\s+(\d+)")
LIST_MARKER_PREFIX_RE = re.compile(r"^\s*(?:[-•—]|\d+[.)])\s+")


def rule_figure_table_numbering_consistent(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    figure_numbers: List[int] = []
    figure_blocks: List[FigureBlock] = []
    table_numbers: List[int] = []
    table_blocks: List[TableBlock] = []

    for block in iter_blocks(report):
        if isinstance(block, FigureBlock):
            caption = block.caption or ""
            match = FIGURE_PATTERN.match(caption)
            if not match:
                issues.append(
                    ValidationIssue(
                        code="FIGURE_TABLE_NUMBERING_CONSISTENT",
                        level=ValidationIssueLevel.ERROR,
                        message="Подпись рисунка должна начинаться с 'Рисунок N'.",
                        block_id=block.id,
                    )
                )
                continue
            number = int(match.group(2))
            figure_numbers.append(number)
            figure_blocks.append(block)
        elif isinstance(block, TableBlock):
            caption = block.caption or ""
            match = TABLE_PATTERN.match(caption)
            if not match:
                issues.append(
                    ValidationIssue(
                        code="FIGURE_TABLE_NUMBERING_CONSISTENT",
                        level=ValidationIssueLevel.ERROR,
                        message="Подпись таблицы должна начинаться с 'Таблица N'.",
                        block_id=block.id,
                    )
                )
                continue
            number = int(match.group(2))
            table_numbers.append(number)
            table_blocks.append(block)

    if figure_numbers:
        expected = 1
        for number, block in zip(figure_numbers, figure_blocks, strict=False):
            if number != expected:
                issues.append(
                    ValidationIssue(
                        code="FIGURE_TABLE_NUMBERING_CONSISTENT",
                        level=ValidationIssueLevel.ERROR,
                        message=(
                            "Нумерация рисунков должна быть последовательной "
                            f"(ожидалось {expected}, найдено {number})."
                        ),
                        block_id=block.id,
                    )
                )
                expected = number + 1
            else:
                expected += 1

    if table_numbers:
        expected = 1
        for number, block in zip(table_numbers, table_blocks, strict=False):
            if number != expected:
                issues.append(
                    ValidationIssue(
                        code="FIGURE_TABLE_NUMBERING_CONSISTENT",
                        level=ValidationIssueLevel.ERROR,
                        message=(
                            "Нумерация таблиц должна быть последовательной "
                            f"(ожидалось {expected}, найдено {number})."
                        ),
                        block_id=block.id,
                    )
                )
                expected = number + 1
            else:
                expected += 1

    return issues


def rule_references_present_if_needed(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    has_references_block = any(
        isinstance(block, ReferencesBlock) for block in iter_blocks(report)
    )

    if not has_references_block:
        issues.append(
            ValidationIssue(
                code="REFERENCES_PRESENT_IF_NEEDED",
                level=ValidationIssueLevel.WARNING,
                message=(
                    "В отчёте отсутствует список использованных источников. "
                    "Если при подготовке отчёта использовалась литература, "
                    "добавьте раздел со списком источников."
                ),
            )
        )

    return issues


def rule_list_of_references_not_empty(report: Report) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for block in iter_blocks(report):
        if isinstance(block, ReferencesBlock):
            if not block.items:
                issues.append(
                    ValidationIssue(
                        code="LIST_OF_REFERENCES_NOT_EMPTY",
                        level=ValidationIssueLevel.ERROR,
                        message=(
                            "Список использованных источников не должен быть пустым."
                        ),
                        block_id=block.id,
                    )
                )

    return issues


RULES.extend(
    [
        rule_required_sections_present,
        rule_section_order,
        rule_non_empty_lists,
        rule_list_marker_format,
        rule_figure_has_caption,
        rule_figure_requirements,
        rule_table_has_caption,
        rule_table_requirements,
        rule_section_ends_with_media,
        rule_appendix_labels_unique,
        rule_appendix_labels_order,
        rule_figure_table_numbering_consistent,
        rule_references_present_if_needed,
        rule_list_of_references_not_empty,
    ]
)
