from datetime import date

from app.models.report import ReportMeta, WorkType


def test_report_meta_basic_creation():
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=4,
        discipline="Технологические основы производства",
        topic="Тема практической работы №4",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    assert meta.preset == "misis_v1"
    assert meta.work_type is WorkType.PRACTICE
    assert meta.work_number == 4
    assert meta.discipline == "Технологические основы производства"
    assert meta.student_full_name.startswith("Иванов")


def test_report_meta_serialization_roundtrip():
    meta = ReportMeta(
        work_type=WorkType.LAB,
        work_number=None,
        discipline="Физика",
        topic="Лабораторная работа №2",
        student_full_name="Петров Петр Петрович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра физики",
        teacher_full_name="Иванова Анна Сергеевна",
        submission_date=date(2025, 2, 1),
    )

    data = meta.model_dump()
    meta2 = ReportMeta(**data)

    assert meta2 == meta
    assert meta2.work_type == WorkType.LAB
