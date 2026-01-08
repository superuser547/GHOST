from __future__ import annotations

from datetime import date
from pathlib import Path

from app.models import Report


def build_markdown(report: Report, output_dir: Path) -> Path:
    """
    Собирает Markdown-файл с YAML front matter для указанного отчёта.

    - output_dir: каталог, где будет создан .md файл
    - returns: путь к созданному .md файлу

    На этапе D1 тело Markdown содержит только заглушку.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / "report.md"

    meta = report.meta
    lines: list[str] = ["---"]

    def add(key: str, value: object | None) -> None:
        if value is None:
            return
        if isinstance(value, date):
            value_str = value.isoformat()
        else:
            value_str = str(value)
        value_str = value_str.replace('"', '\\"')
        lines.append(f'{key}: "{value_str}"')

    add("title", meta.topic)
    add("work_type", meta.work_type.value)
    add("work_number", meta.work_number)
    add("discipline", meta.discipline)
    add("author", meta.student_full_name)
    add("group", meta.group)
    add("semester", meta.semester)
    add("direction_code", meta.direction_code)
    add("direction_name", meta.direction_name)
    add("department", meta.department)
    add("teacher", meta.teacher_full_name)
    add("submission_date", meta.submission_date)

    lines.append("---")

    body_lines = ["", "# TODO: report content will be generated in future commits.", ""]
    content = "\n".join(lines + body_lines)
    file_path.write_text(content, encoding="utf-8")

    return file_path
