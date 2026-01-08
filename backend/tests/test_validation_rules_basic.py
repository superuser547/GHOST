from datetime import date

from app.models import (
    FigureBlock,
    ListBlock,
    Report,
    ReportMeta,
    SectionBlock,
    TableBlock,
    TextBlock,
    WorkType,
)
from app.services.validation import rules as validation_rules
from app.services.validation.engine import validate_report


def build_valid_report() -> Report:
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

    intro = SectionBlock(title="ВВЕДЕНИЕ", special_kind="INTRO")
    intro.children.append(TextBlock(text="Краткое введение."))

    main_section = SectionBlock(title="1 Постановка задачи")
    main_section.children.append(
        ListBlock(list_type="numbered", items=["Первый пункт", "Второй пункт"])
    )
    main_section.children.append(
        TableBlock(
            caption="Таблица 1 – Пример данных",
            rows=[["Колонка 1", "Колонка 2"], ["1", "2"]],
        )
    )
    main_section.children.append(
        FigureBlock(
            caption="Рисунок 1 – Схема",
            file_name="figure1.png",
        )
    )

    conclusion = SectionBlock(title="ЗАКЛЮЧЕНИЕ", special_kind="CONCLUSION")
    conclusion.children.append(TextBlock(text="Здесь формулируются выводы."))

    return Report(meta=meta, blocks=[intro, main_section, conclusion])


def test_valid_report_has_no_issues_for_basic_rules():
    report = build_valid_report()

    result = validate_report(report)

    assert validation_rules
    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []


def test_missing_intro_section_produces_error():
    report = build_valid_report()
    report.blocks = [
        block
        for block in report.blocks
        if not (isinstance(block, SectionBlock) and block.special_kind == "INTRO")
    ]

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "REQUIRED_SECTIONS_PRESENT" in error_codes


def test_missing_conclusion_section_produces_error():
    report = build_valid_report()
    report.blocks = [
        block
        for block in report.blocks
        if not (isinstance(block, SectionBlock) and block.special_kind == "CONCLUSION")
    ]

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "REQUIRED_SECTIONS_PRESENT" in error_codes


def test_wrong_section_order_produces_section_order_error():
    report = build_valid_report()
    blocks = report.blocks
    report.blocks = [blocks[2], blocks[1], blocks[0]]

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "SECTION_ORDER" in error_codes


def test_empty_list_produces_non_empty_lists_error():
    report = build_valid_report()

    for block in report.blocks:
        if isinstance(block, SectionBlock):
            for child in block.children:
                if isinstance(child, ListBlock):
                    child.items = []
                    break

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "NON_EMPTY_LISTS" in error_codes


def test_empty_captions_for_table_and_figure_produce_errors():
    report = build_valid_report()

    for block in report.blocks:
        if isinstance(block, SectionBlock):
            for child in block.children:
                if isinstance(child, TableBlock):
                    child.caption = "   "
                if isinstance(child, FigureBlock):
                    child.caption = ""

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "TABLE_HAS_CAPTION" in error_codes
    assert "FIGURE_HAS_CAPTION" in error_codes
