from datetime import date

from app.models import (
    AppendixBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    Report,
    ReportMeta,
    SectionBlock,
    TableBlock,
    TextBlock,
    WorkType,
)
from app.services.validation import rules as validation_rules
from app.services.validation.engine import validate_report
from app.services.validation.rules import iter_blocks


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
            caption="Рисунок 1 – Схема установки",
            file_name="figure1.png",
        )
    )
    main_section.children.append(TextBlock(text="Комментарий к рисунку и таблице."))

    conclusion = SectionBlock(title="ЗАКЛЮЧЕНИЕ", special_kind="CONCLUSION")
    conclusion.children.append(TextBlock(text="Здесь формулируются выводы."))

    references = ReferencesBlock(
        items=[
            "ГОСТ 7.0.5-2008. Библиографическая ссылка.",
            "Методические указания НИТУ МИСИС по оформлению отчётов.",
        ]
    )

    appendix = AppendixBlock(
        label="А",
        title="Дополнительные материалы",
        children=[TextBlock(text="Текст приложения.")],
    )

    return Report(
        meta=meta,
        blocks=[intro, main_section, conclusion, references, appendix],
    )


def test_valid_report_has_no_issues_for_all_rules():
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


def test_section_ending_with_figure_produces_section_ends_with_media_error():
    report = build_valid_report()

    for block in report.blocks:
        if isinstance(block, SectionBlock) and block.special_kind is None:
            if isinstance(block.children[-1], TextBlock):
                block.children.pop()
            break

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "SECTION_ENDS_WITH_MEDIA" in error_codes


def test_duplicate_appendix_labels_produce_unique_error():
    report = build_valid_report()

    report.blocks.append(
        AppendixBlock(
            label="А",
            title="Ещё одно приложение А",
            children=[TextBlock(text="Дублирующая метка приложения.")],
        )
    )

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "APPENDIX_LABELS_UNIQUE" in error_codes


def test_appendix_labels_out_of_order_produce_warning():
    report = build_valid_report()

    appendices = [block for block in report.blocks if isinstance(block, AppendixBlock)]
    assert appendices, "В build_valid_report должно быть хотя бы одно приложение"
    app_a = appendices[0]

    report.blocks = [
        block for block in report.blocks if not isinstance(block, AppendixBlock)
    ]
    app_b = AppendixBlock(
        label="Б",
        title="Приложение Б",
        children=[TextBlock(text="Приложение Б.")],
    )
    report.blocks.extend([app_b, app_a])

    result = validate_report(report)

    warning_codes = {issue.code for issue in result.warnings}
    assert "APPENDIX_LABELS_ORDER" in warning_codes


def test_incorrect_figure_numbering_produces_numbering_error():
    report = build_valid_report()

    for block in iter_blocks(report):
        if isinstance(block, FigureBlock):
            block.caption = "Рисунок 2 – Неправильный номер"
            break

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "FIGURE_TABLE_NUMBERING_CONSISTENT" in error_codes


def test_missing_references_block_produces_warning():
    report = build_valid_report()

    report.blocks = [
        block for block in report.blocks if not isinstance(block, ReferencesBlock)
    ]

    result = validate_report(report)

    warning_codes = {issue.code for issue in result.warnings}
    assert "REFERENCES_PRESENT_IF_NEEDED" in warning_codes


def test_empty_references_block_produces_error():
    report = build_valid_report()

    for block in iter_blocks(report):
        if isinstance(block, ReferencesBlock):
            block.items = []
            break

    result = validate_report(report)

    error_codes = {issue.code for issue in result.errors}
    assert "LIST_OF_REFERENCES_NOT_EMPTY" in error_codes


def test_list_with_manual_markers_produces_warning():
    report = build_valid_report()

    for block in iter_blocks(report):
        if isinstance(block, ListBlock):
            block.items = ["- Первый пункт", "2) Второй пункт"]
            break

    result = validate_report(report)

    warning_codes = {issue.code for issue in result.warnings}
    assert "LIST_MARKER_FORMAT" in warning_codes


def test_table_with_order_number_column_produces_warning():
    report = build_valid_report()

    for block in iter_blocks(report):
        if isinstance(block, TableBlock):
            block.rows = [
                ["№", "Колонка 2"],
                ["1", "a"],
                ["2", "b"],
            ]
            break

    result = validate_report(report)

    warning_codes = {issue.code for issue in result.warnings}
    assert "TABLE_REQUIREMENTS" in warning_codes


def test_figure_with_incorrect_caption_format_produces_warning():
    report = build_valid_report()

    for block in iter_blocks(report):
        if isinstance(block, FigureBlock):
            block.caption = "Схема установки"
            break

    result = validate_report(report)

    warning_codes = {issue.code for issue in result.warnings}
    assert "FIGURE_REQUIREMENTS" in warning_codes
