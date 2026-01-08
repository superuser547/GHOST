from __future__ import annotations

from datetime import date
from pathlib import Path

from app.models import BaseBlock, Report, SectionBlock, SubsectionBlock, TextBlock


def _render_blocks(blocks: list[BaseBlock], heading_level: int) -> list[str]:
    """
    Рендерит список блоков отчёта в строки Markdown.

    :param blocks: упорядоченный список блоков
    :param heading_level: текущий уровень заголовка
        для секций/подсекций (1 -> '#', 2 -> '##')
    :return: список строк Markdown без завершающих переводов строк
    """

    lines: list[str] = []

    def ensure_blank_line() -> None:
        if lines and lines[-1] != "":
            lines.append("")

    for block in blocks:
        if isinstance(block, SectionBlock):
            ensure_blank_line()
            lines.append("#" * heading_level + " " + block.title)
            child_lines = _render_blocks(block.children, heading_level + 1)
            if child_lines:
                lines.append("")
                lines.extend(child_lines)
        elif isinstance(block, SubsectionBlock):
            ensure_blank_line()
            lines.append("#" * heading_level + " " + block.title)
            child_lines = _render_blocks(block.children, heading_level + 1)
            if child_lines:
                lines.append("")
                lines.extend(child_lines)
        elif isinstance(block, TextBlock):
            ensure_blank_line()
            paragraphs = [p.strip() for p in block.text.split("\n\n") if p.strip()]
            for idx, paragraph in enumerate(paragraphs):
                if idx > 0:
                    lines.append("")
                lines.append(paragraph)
        else:
            continue

    return lines


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

    body_lines = _render_blocks(report.blocks, heading_level=1)
    if body_lines:
        lines.append("")
        lines.extend(body_lines)

    content = "\n".join(lines) + "\n"
    file_path.write_text(content, encoding="utf-8")

    return file_path
