from datetime import date

from fastapi.testclient import TestClient

from app.main import app
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


def build_valid_report_for_api() -> Report:
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Тестовый отчёт для API",
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


def test_validate_report_endpoint_with_valid_report_returns_empty_issues():
    client = TestClient(app)

    report = build_valid_report_for_api()
    response = client.post(
        "/api/v1/reports/validate", json=report.model_dump(mode="json")
    )

    assert response.status_code == 200

    data = response.json()
    assert "errors" in data
    assert "warnings" in data
    assert isinstance(data["errors"], list)
    assert isinstance(data["warnings"], list)
    assert data["errors"] == []
    assert data["warnings"] == []


def test_validate_report_endpoint_detects_basic_error():
    client = TestClient(app)

    report = build_valid_report_for_api()
    report.blocks = [
        block
        for block in report.blocks
        if not (isinstance(block, SectionBlock) and block.special_kind == "INTRO")
    ]

    response = client.post(
        "/api/v1/reports/validate", json=report.model_dump(mode="json")
    )

    assert response.status_code == 200

    data = response.json()
    error_codes = {issue["code"] for issue in data.get("errors", [])}
    assert "REQUIRED_SECTIONS_PRESENT" in error_codes
