from __future__ import annotations

from datetime import date
from io import BytesIO

from docx import Document

from app.models import Report, ReportMeta, SectionBlock, TextBlock, WorkType
from app.services.docx import build_docx


def test_build_docx_with_minimal_report_returns_valid_docx():
    meta = ReportMeta(
        preset="misis_v1",
        work_type=WorkType.PRACTICE,
        work_number=1,
        work_type_custom=None,
        discipline="Информатика",
        topic="Первая практическая работа",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра информатики",
        teacher_full_name="Петров Пётр Петрович",
        submission_date=date(2025, 5, 20),
    )

    blocks = [
        SectionBlock(title="Введение"),
        TextBlock(text="Текст введения."),
    ]

    report = Report(meta=meta, blocks=blocks)

    data = build_docx(report)
    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 0

    doc = Document(BytesIO(data))
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "Первая практическая работа" in full_text
    assert "Текст введения." in full_text


def test_build_docx_replaces_title_placeholders_from_template():
    template_doc = Document()
    template_doc.add_paragraph("Студент: {{STUDENT_NAME}}")
    template_doc.add_paragraph("Группа: {{GROUP}}")

    buffer = BytesIO()
    template_doc.save(buffer)
    template_bytes = buffer.getvalue()

    meta = ReportMeta(
        preset="misis_v1",
        work_type=WorkType.PRACTICE,
        work_number=1,
        work_type_custom=None,
        discipline="Информатика",
        topic="Первая практическая работа",
        student_full_name="Сидоров Сидор Сидорович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра информатики",
        teacher_full_name="Петров Пётр Петрович",
        submission_date=date(2025, 5, 20),
    )

    report = Report(meta=meta, blocks=[])

    output_bytes = build_docx(
        report,
        preset_id="misis_v1",
        title_template=template_bytes,
    )
    doc = Document(BytesIO(output_bytes))

    texts = "\n".join(p.text for p in doc.paragraphs)
    assert "{{STUDENT_NAME}}" not in texts
    assert "{{GROUP}}" not in texts
    assert "Сидоров Сидор Сидорович" in texts
    assert "ББИ-24-3" in texts
