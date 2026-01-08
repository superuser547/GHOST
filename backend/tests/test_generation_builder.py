from datetime import date
from pathlib import Path

from app.models import (
    AppendixBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    Report,
    ReportMeta,
    SectionBlock,
    SubsectionBlock,
    TableBlock,
    TextBlock,
    WorkType,
)
from app.services.generation.builder import build_markdown


def make_minimal_report() -> Report:
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Тестовый отчёт для Markdown",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    return Report(meta=meta, blocks=[])


def _read_markdown_body(md_path: Path) -> str:
    content = md_path.read_text(encoding="utf-8")
    parts = content.split("\n---\n", maxsplit=1)
    if len(parts) == 2:
        return parts[1]
    return content


def test_build_markdown_creates_md_file_with_yaml_front_matter(tmp_path):
    report = make_minimal_report()

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)

    assert md_path.exists()
    assert md_path.is_file()
    assert md_path.suffix == ".md"
    assert md_path.parent == output_dir

    content = md_path.read_text(encoding="utf-8")

    assert content.startswith("---")
    assert "\n---\n" in content

    assert "title:" in content
    assert "author:" in content or "student:" in content
    assert "discipline:" in content
    assert "work_type:" in content
    assert "group:" in content
    assert "submission_date:" in content

    body = _read_markdown_body(md_path)
    body_lines = [line for line in body.splitlines() if line.strip()]
    assert isinstance(body_lines, list)


def make_structured_report() -> Report:
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Структурный отчёт для Markdown",
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
    intro.children.append(TextBlock(text="Текст введения."))

    theory = SectionBlock(title="1 Теоретические сведения")
    subsection = SubsectionBlock(title="1.1 Основные понятия", level=2)
    subsection.children.append(TextBlock(text="Текст подраздела 1.1."))
    theory.children.append(subsection)

    conclusion = SectionBlock(title="ЗАКЛЮЧЕНИЕ", special_kind="CONCLUSION")
    conclusion.children.append(TextBlock(text="Текст заключения."))

    return Report(meta=meta, blocks=[intro, theory, conclusion])


def test_build_markdown_renders_sections_subsections_and_text(tmp_path):
    report = make_structured_report()

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)

    body = _read_markdown_body(md_path)

    assert "# ВВЕДЕНИЕ" in body
    assert "# 1 Теоретические сведения" in body
    assert "# ЗАКЛЮЧЕНИЕ" in body
    assert "## 1.1 Основные понятия" in body

    assert "Текст введения." in body
    assert "Текст подраздела 1.1." in body
    assert "Текст заключения." in body

    idx_intro = body.index("# ВВЕДЕНИЕ")
    idx_theory = body.index("# 1 Теоретические сведения")
    idx_conclusion = body.index("# ЗАКЛЮЧЕНИЕ")

    assert idx_intro < idx_theory < idx_conclusion

    idx_subsection = body.index("## 1.1 Основные понятия")
    assert idx_theory < idx_subsection < idx_conclusion


def test_build_markdown_renders_bullet_and_numbered_lists(tmp_path):
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Отчёт со списками",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    section = SectionBlock(title="СПИСКИ")
    section.children.append(
        ListBlock(list_type="bulleted", items=["Пункт 1", "Пункт 2"])
    )
    section.children.append(ListBlock(list_type="numbered", items=["Первый", "Второй"]))

    report = Report(meta=meta, blocks=[section])

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)
    body = _read_markdown_body(md_path)

    assert "- Пункт 1" in body
    assert "- Пункт 2" in body
    assert "1. Первый" in body
    assert "2. Второй" in body

    idx_header = body.index("# СПИСКИ")
    idx_bullet = body.index("- Пункт 1")
    idx_numbered = body.index("1. Первый")

    assert idx_header < idx_bullet < idx_numbered


def test_build_markdown_renders_table_as_pipe_table(tmp_path):
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Отчёт с таблицей",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    section = SectionBlock(title="ТАБЛИЦА")
    table = TableBlock(
        caption="Таблица 1 – Пример данных",
        rows=[
            ["Колонка 1", "Колонка 2"],
            ["1", "2"],
            ["3", "4"],
        ],
    )
    section.children.append(table)

    report = Report(meta=meta, blocks=[section])

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)
    body = _read_markdown_body(md_path)

    assert "| Колонка 1 | Колонка 2 |" in body
    assert "| --- | --- |" in body
    assert "| 1 | 2 |" in body


def test_build_markdown_renders_figure_as_image(tmp_path):
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Отчёт с рисунком",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    section = SectionBlock(title="РИСУНОК")
    figure = FigureBlock(caption="Рисунок 1 – Схема установки", file_name="figure1.png")
    section.children.append(figure)

    report = Report(meta=meta, blocks=[section])

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)
    body = _read_markdown_body(md_path)

    assert "![Рисунок 1 – Схема установки](figure1.png)" in body


def test_build_markdown_renders_references_heading_and_list(tmp_path):
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Отчёт со списком источников",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петр Петрович",
        submission_date=date(2025, 3, 15),
    )

    refs = ReferencesBlock(
        items=[
            "ГОСТ 7.0.5-2008. Библиографическая ссылка.",
            "Методические указания НИТУ МИСИС по оформлению отчётов.",
        ]
    )

    report = Report(meta=meta, blocks=[refs])

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)
    body = _read_markdown_body(md_path)

    assert "# Список использованных источников" in body
    assert "1. ГОСТ 7.0.5-2008. Библиографическая ссылка." in body
    assert "2. Методические указания НИТУ МИСИС по оформлению отчётов." in body


def test_build_markdown_renders_appendix_heading_and_content(tmp_path):
    meta = ReportMeta(
        work_type=WorkType.PRACTICE,
        work_number=1,
        discipline="Технологические основы производства",
        topic="Отчёт с приложением",
        student_full_name="Иванов Иван Иванович",
        group="ББИ-24-3",
        semester="2",
        direction_code="38.03.05",
        direction_name="Бизнес-информатика",
        department="Кафедра бизнес-информатики",
        teacher_full_name="Петров Петрович",
        submission_date=date(2025, 3, 15),
    )

    appendix = AppendixBlock(
        label="А",
        title="Дополнительные материалы",
        children=[TextBlock(text="Текст приложения А.")],
    )

    report = Report(meta=meta, blocks=[appendix])

    output_dir = tmp_path / "output"
    md_path = build_markdown(report, output_dir)
    body = _read_markdown_body(md_path)

    assert "# ПРИЛОЖЕНИЕ А. Дополнительные материалы" in body
    assert "Текст приложения А." in body

    idx_heading = body.index("# ПРИЛОЖЕНИЕ А. Дополнительные материалы")
    idx_text = body.index("Текст приложения А.")
    assert idx_heading < idx_text
