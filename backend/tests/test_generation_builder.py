from datetime import date

from app.models import (
    Report,
    ReportMeta,
    SectionBlock,
    SubsectionBlock,
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

    parts = content.split("\n---\n", maxsplit=1)
    assert len(parts) == 2
    body = parts[1]
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

    content = md_path.read_text(encoding="utf-8")

    parts = content.split("\n---\n", maxsplit=1)
    assert len(parts) == 2
    body = parts[1]

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
