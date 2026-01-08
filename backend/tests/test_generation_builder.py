from datetime import date

from app.models import Report, ReportMeta, WorkType
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
    assert "\n---\n" in content or content.rstrip().endswith("---")

    assert "title:" in content
    assert "author:" in content or "student:" in content
    assert "discipline:" in content
    assert "work_type:" in content
    assert "group:" in content
    assert "submission_date:" in content

    parts = content.split("---")
    assert len(parts) >= 3
    body_part = parts[-1]
    assert "TODO" in body_part or "#" in body_part
