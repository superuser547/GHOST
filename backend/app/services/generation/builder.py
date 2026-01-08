from __future__ import annotations

from datetime import date
from pathlib import Path

from app.models import (
    AppendixBlock,
    BaseBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    Report,
    SectionBlock,
    SubsectionBlock,
    TableBlock,
    TextBlock,
)


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
        elif isinstance(block, ListBlock):
            if not block.items:
                continue

            ensure_blank_line()

            if block.list_type == "bulleted":
                for item in block.items:
                    lines.append(f"- {item}")
            else:
                for idx, item in enumerate(block.items, start=1):
                    lines.append(f"{idx}. {item}")
        elif isinstance(block, TableBlock):
            if not block.rows or not block.rows[0]:
                continue

            ensure_blank_line()

            header_cells = [cell or "" for cell in block.rows[0]]
            header_line = "| " + " | ".join(header_cells) + " |"
            lines.append(header_line)

            separator_cells = ["---"] * len(header_cells)
            separator_line = "| " + " | ".join(separator_cells) + " |"
            lines.append(separator_line)

            for row in block.rows[1:]:
                row_cells = [cell or "" for cell in row]
                if len(row_cells) < len(header_cells):
                    row_cells.extend([""] * (len(header_cells) - len(row_cells)))
                line = "| " + " | ".join(row_cells) + " |"
                lines.append(line)
        elif isinstance(block, FigureBlock):
            if not block.file_name:
                continue

            ensure_blank_line()

            caption = block.caption or ""
            path = block.file_name
            lines.append(f"![{caption}]({path})")
        elif isinstance(block, ReferencesBlock):
            if not block.items:
                continue

            ensure_blank_line()

            heading_prefix = "#" * heading_level
            lines.append(f"{heading_prefix} Список использованных источников")
            for idx, item in enumerate(block.items, start=1):
                lines.append(f"{idx}. {item}")
        elif isinstance(block, AppendixBlock):
            ensure_blank_line()

            heading_prefix = "#" * heading_level
            heading_text = f"ПРИЛОЖЕНИЕ {block.label}"
            if block.title:
                heading_text += f". {block.title}"
            lines.append(f"{heading_prefix} {heading_text}")

            child_lines = _render_blocks(block.children, heading_level + 1)
            if child_lines:
                lines.append("")
                lines.extend(child_lines)
        else:
            continue

    return lines


def build_markdown(report: Report, output_dir: Path) -> Path:
    """
    Собирает Markdown-файл с YAML front matter для указанного отчёта.

    - output_dir: каталог, где будет создан .md файл
    - returns: путь к созданному .md файлу

    Тело Markdown формируется из блоков отчёта.
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
