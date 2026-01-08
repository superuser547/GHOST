from datetime import date

from app.models import (
    Report,
    ReportMeta,
    ReportBlockType,
    SectionBlock,
    TextBlock,
    WorkType,
)


def test_report_basic_creation():
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Построение технологической схемы производства",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    section = SectionBlock(title="ВВЕДЕНИЕ", special_kind="INTRO")
    text = TextBlock(text="Это пример простого текста во введении.")
    section.children.append(text)

    report = Report(
        meta=meta,
        blocks=[section],
    )

    assert report.meta.work_type is WorkType.PRACTICE
    assert len(report.blocks) == 1
    assert isinstance(report.blocks[0], SectionBlock)
    assert report.blocks[0].type is ReportBlockType.SECTION
    assert len(report.blocks[0].children) == 1
    assert isinstance(report.blocks[0].children[0], TextBlock)


def test_report_json_roundtrip():
    meta = ReportMeta(
        work_type=WorkType.LAB,
        work_number=2,
        discipline="Физика",
        topic="Изучение свободного падения тел",
        student_full_name="Петров Петр Петрович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра физики",
        teacher_full_name="Иванова Анна Сергеевна",
        submission_date=date(2025, 2, 1),
    )

    section = SectionBlock(title="1 Постановка задачи")
    text = TextBlock(text="Цель работы — изучить свободное падение.")
    section.children.append(text)

    report = Report(meta=meta, blocks=[section])

    data = report.model_dump()
    restored = Report(**data)

    assert restored.meta.discipline == "Физика"
    assert len(restored.blocks) == 1
    restored_section = restored.blocks[0]
    assert isinstance(restored_section, SectionBlock)
    assert restored_section.type is ReportBlockType.SECTION
    assert restored_section.title.startswith("1 Постановка")
    assert len(restored_section.children) == 1
    assert isinstance(restored_section.children[0], TextBlock)
    assert "Цель работы" in restored_section.children[0].text
