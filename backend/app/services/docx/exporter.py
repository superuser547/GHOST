from __future__ import annotations

from io import BytesIO
from typing import Dict

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from app.models import (
    AppendixBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    Report,
    ReportBlock,
    ReportMeta,
    SectionBlock,
    SubsectionBlock,
    TableBlock,
    TextBlock,
    WorkType,
)
from app.services.docx.numbering import ensure_multilevel_heading_numbering
from app.services.presets import get_preset


def _format_work_type(meta: ReportMeta) -> str:
    """
    Возвращает человекочитаемое название типа работы для титульного листа.

    Если work_type == OTHER и задано work_type_custom, используется оно.
    Иначе используется предопределённое русскоязычное название.
    """
    if meta.work_type is WorkType.OTHER and meta.work_type_custom:
        return meta.work_type_custom

    mapping: Dict[WorkType, str] = {
        WorkType.PRACTICE: "Практическая работа",
        WorkType.LAB: "Лабораторная работа",
        WorkType.ESSAY: "Реферат",
        WorkType.COURSE: "Курсовая работа",
        WorkType.OTHER: "Другая работа",
    }
    return mapping.get(meta.work_type, meta.work_type.value)


def _build_title_placeholders(meta: ReportMeta) -> Dict[str, str]:
    """
    Формирует словарь плейсхолдеров для титульного листа по REQUIREMENTS:

    - {{STUDENT_NAME}}, {{GROUP}}, {{SEMESTER}}, {{DIRECTION_CODE}},
      {{DIRECTION_NAME}}, {{DEPARTMENT}}, {{DISCIPLINE}},
      {{WORK_TYPE}}, {{WORK_NUMBER}}, {{TOPIC}}, {{TEACHER_NAME}},
      а также год/дата.
    """
    values: Dict[str, str] = {
        "{{STUDENT_NAME}}": meta.student_full_name,
        "{{GROUP}}": meta.group,
        "{{SEMESTER}}": meta.semester,
        "{{DIRECTION_CODE}}": meta.direction_code,
        "{{DIRECTION_NAME}}": meta.direction_name,
        "{{DEPARTMENT}}": meta.department,
        "{{DISCIPLINE}}": meta.discipline,
        "{{WORK_TYPE}}": _format_work_type(meta),
        "{{TOPIC}}": meta.topic,
        "{{TEACHER_NAME}}": meta.teacher_full_name,
    }

    if meta.work_number is not None:
        values["{{WORK_NUMBER}}"] = str(meta.work_number)

    submission_year = meta.submission_date.year
    values["{{YEAR}}"] = str(submission_year)
    values["{{SUBMISSION_DATE}}"] = meta.submission_date.isoformat()

    return values


def _replace_placeholders_in_document(
    doc: Document, placeholders: Dict[str, str]
) -> None:
    """
    Заменяет плейсхолдеры вида {{NAME}} во всех параграфах и таблицах
    документа, стараясь сохранить форматирование (работаем с runs).
    """

    def replace_in_runs(runs, mapping: Dict[str, str]) -> None:
        for run in runs:
            text = run.text
            if not text:
                continue
            for key, value in mapping.items():
                if key in text:
                    text = text.replace(key, value)
            run.text = text

    for paragraph in doc.paragraphs:
        replace_in_runs(paragraph.runs, placeholders)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_runs(paragraph.runs, placeholders)


def _apply_page_settings_for_misis(doc: Document) -> None:
    """
    Настраивает параметры страницы по методичке МИСИС:

    - формат A4;
    - поля: левое 3 см, правое 1,5 см, верх/низ 2 см.
    """
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)


def _apply_base_text_style_for_misis(doc: Document) -> None:
    """
    Настраивает стиль Normal по п. 5.3:

    - Times New Roman, 12 pt;
    - выравнивание по ширине;
    - отступ первой строки 1,25 см;
    - межстрочный интервал 1,5;
    - интервалы до/после 0 pt.
    """
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)

    paragraph_format = style.paragraph_format
    paragraph_format.left_indent = Cm(0)
    paragraph_format.right_indent = Cm(0)
    paragraph_format.first_line_indent = Cm(1.25)
    paragraph_format.line_spacing = 1.5
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)


def _apply_heading_styles_for_misis(doc: Document) -> None:
    """
    Настраивает базовые стили заголовков 1–3 уровней:

    - Times New Roman, 12 pt, bold;
    - межстрочный интервал 1,5;
    - без отступа первой строки.
    """
    for style_name in ["Heading 1", "Heading 2", "Heading 3"]:
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue

        font = style.font
        font.name = "Times New Roman"
        font.size = Pt(12)
        font.bold = True
        font.color.rgb = RGBColor(0, 0, 0)

        paragraph_format = style.paragraph_format
        paragraph_format.left_indent = Cm(0)
        paragraph_format.right_indent = Cm(0)
        paragraph_format.first_line_indent = Cm(0)
        paragraph_format.line_spacing = 1.5
        paragraph_format.space_before = Pt(0)
        paragraph_format.space_after = Pt(0)


def _add_simple_title_page(doc: Document, meta: ReportMeta) -> None:
    """
    Простейший титульный лист, если пользовательский шаблон не предоставлен.
    Служит временной заглушкой до загрузки настоящего шаблона.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ТИТУЛЬНЫЙ ЛИСТ (шаблон не задан)")
    run.bold = True

    doc.add_paragraph()
    doc.add_paragraph(f"Дисциплина: {meta.discipline}")
    doc.add_paragraph(f"Тема: {meta.topic}")
    doc.add_paragraph(f"Студент: {meta.student_full_name}")
    doc.add_paragraph(f"Группа: {meta.group}")
    doc.add_paragraph(f"Преподаватель: {meta.teacher_full_name}")


def _append_section_block(doc: Document, block: SectionBlock) -> None:
    if block.special_kind == "INTRO":
        title = "ВВЕДЕНИЕ"
        align = WD_ALIGN_PARAGRAPH.CENTER
        style_name = "Heading 1"
    elif block.special_kind == "CONCLUSION":
        title = "ЗАКЛЮЧЕНИЕ"
        align = WD_ALIGN_PARAGRAPH.CENTER
        style_name = "Heading 1"
    elif block.special_kind == "REFERENCES":
        title = "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"
        align = WD_ALIGN_PARAGRAPH.CENTER
        style_name = "Heading 1"
    else:
        title = block.title
        align = WD_ALIGN_PARAGRAPH.LEFT
        style_name = "Heading 1"

    paragraph = doc.add_paragraph(title, style=style_name)
    paragraph.alignment = align


def _append_subsection_block(doc: Document, block: SubsectionBlock) -> None:
    style_name = "Heading 2" if block.level == 2 else "Heading 3"
    paragraph = doc.add_paragraph(block.title, style=style_name)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT


def _append_text_block(doc: Document, block: TextBlock) -> None:
    raw = block.text or ""
    parts = [part.strip() for part in raw.split("\n\n") if part.strip()]
    if not parts:
        return
    for part in parts:
        doc.add_paragraph(part, style="Normal")


def _append_list_block(doc: Document, block: ListBlock) -> None:
    if not block.items:
        return

    for idx, item in enumerate(block.items, start=1):
        if not item:
            continue
        if block.list_type == "numbered":
            text = f"{idx}) {item}"
        else:
            text = f"– {item}"

        paragraph = doc.add_paragraph(text, style="Normal")
        pf = paragraph.paragraph_format
        pf.left_indent = Cm(1.25)
        pf.first_line_indent = Cm(0)
        pf.line_spacing = 1.5
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def _append_table_block(doc: Document, block: TableBlock) -> None:
    if not block.rows:
        return

    caption_paragraph = doc.add_paragraph(block.caption or "", style="Normal")
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cpf = caption_paragraph.paragraph_format
    cpf.left_indent = Cm(0)
    cpf.first_line_indent = Cm(0)
    cpf.space_before = Pt(12)
    cpf.space_after = Pt(6)

    rows_count = len(block.rows)
    cols_count = len(block.rows[0]) if block.rows[0] else 0
    if cols_count == 0:
        return

    table = doc.add_table(rows=rows_count, cols=cols_count)
    table.style = "Table Grid"
    table.autofit = True

    for r_idx, row in enumerate(block.rows):
        for c_idx, value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = value or ""

    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.style = doc.styles["Normal"]
                pf = paragraph.paragraph_format
                pf.left_indent = Cm(0)
                pf.first_line_indent = Cm(0)
                pf.line_spacing = 1.0
                pf.space_before = Pt(0)
                pf.space_after = Pt(0)

    after = doc.add_paragraph("", style="Normal")
    af = after.paragraph_format
    af.space_before = Pt(6)
    af.space_after = Pt(0)


def _append_figure_block(doc: Document, block: FigureBlock) -> None:
    doc.add_paragraph("")

    caption_paragraph = doc.add_paragraph(block.caption or "", style="Normal")
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = caption_paragraph.paragraph_format
    pf.left_indent = Cm(0)
    pf.first_line_indent = Cm(0)
    pf.line_spacing = 1.5
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)


def _append_references_block(doc: Document, block: ReferencesBlock) -> None:
    if not block.items:
        return

    for idx, item in enumerate(block.items, start=1):
        if not item:
            continue
        paragraph = doc.add_paragraph(f"{idx}) {item}", style="Normal")
        pf = paragraph.paragraph_format
        pf.left_indent = Cm(1.25)
        pf.first_line_indent = Cm(0)
        pf.line_spacing = 1.5
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def _append_appendix_block(doc: Document, block: AppendixBlock) -> None:
    doc.add_page_break()

    title_text = f"ПРИЛОЖЕНИЕ {block.label}"
    title_paragraph = doc.add_paragraph(title_text, style="Heading 1")
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if block.title:
        subtitle_paragraph = doc.add_paragraph(block.title, style="Heading 2")
        subtitle_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _render_block(doc: Document, block: ReportBlock) -> None:
    if isinstance(block, SectionBlock):
        _append_section_block(doc, block)
        for child in block.children:
            _render_block(doc, child)
    elif isinstance(block, SubsectionBlock):
        _append_subsection_block(doc, block)
        for child in block.children:
            _render_block(doc, child)
    elif isinstance(block, TextBlock):
        _append_text_block(doc, block)
    elif isinstance(block, ListBlock):
        _append_list_block(doc, block)
    elif isinstance(block, TableBlock):
        _append_table_block(doc, block)
    elif isinstance(block, FigureBlock):
        _append_figure_block(doc, block)
    elif isinstance(block, ReferencesBlock):
        _append_references_block(doc, block)
    elif isinstance(block, AppendixBlock):
        _append_appendix_block(doc, block)
        for child in block.children:
            _render_block(doc, child)


def _append_report_blocks(doc: Document, report: Report) -> None:
    """
    Добавляет в документ основную часть отчёта на основе структуры блоков.
    """
    for block in report.blocks:
        _render_block(doc, block)


def build_docx(
    report: Report,
    preset_id: str = "misis_v1",
    title_template: bytes | None = None,
) -> bytes:
    """
    Строит DOCX-документ по структуре отчёта.

    - Если передан title_template, используется он как титульный лист:
      плейсхолдеры заменяются на значения из report.meta.
    - Если шаблон не передан, создаётся базовый титульный лист-заглушка.
    - Далее добавляется основная часть отчёта согласно структуре блоков.
    """
    preset = get_preset(preset_id)
    if preset is None:
        raise ValueError(f"Unknown formatting preset: {preset_id!r}")

    if title_template is not None:
        doc = Document(BytesIO(title_template))
        placeholders = _build_title_placeholders(report.meta)
        _replace_placeholders_in_document(doc, placeholders)
    else:
        doc = Document()
        _apply_page_settings_for_misis(doc)
        _apply_base_text_style_for_misis(doc)
        _apply_heading_styles_for_misis(doc)
        ensure_multilevel_heading_numbering(doc)
        _add_simple_title_page(doc, report.meta)

    if title_template is not None:
        _apply_page_settings_for_misis(doc)
        _apply_base_text_style_for_misis(doc)
        _apply_heading_styles_for_misis(doc)
        ensure_multilevel_heading_numbering(doc)

    doc.add_page_break()
    _append_report_blocks(doc, report)

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
