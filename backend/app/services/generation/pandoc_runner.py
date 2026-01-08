from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional, Sequence


class PandocError(RuntimeError):
    """Raised when a pandoc conversion fails or pandoc is not available."""


def get_pandoc_bin() -> str:
    """
    Return the pandoc binary to use.

    - If the environment variable PANDOC_BIN is set, use it as-is.
    - Otherwise, return 'pandoc' (expecting it to be in PATH).
    """

    return os.getenv("PANDOC_BIN", "pandoc")


def generate_docx_from_markdown(
    md_path: Path,
    output_path: Path,
    reference_doc_path: Optional[Path] = None,
    extra_args: Optional[Sequence[str]] = None,
) -> None:
    """
    Convert a Markdown file to DOCX using pandoc.

    :param md_path: Path to the input .md file.
    :param output_path: Path to the resulting .docx file.
    :param reference_doc_path: Optional path to a reference DOCX (misis_reference.docx).
    :param extra_args: Optional extra command-line arguments to pass to pandoc.
    :raises PandocError: if pandoc is not available or returns a non-zero exit code.
    """

    if not md_path.exists() or not md_path.is_file():
        raise PandocError(f"Markdown file does not exist: {md_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    pandoc_bin = get_pandoc_bin()
    cmd: list[str] = [pandoc_bin, str(md_path), "-o", str(output_path)]

    if reference_doc_path is not None:
        cmd.extend(["--reference-doc", str(reference_doc_path)])

    cmd.append("--toc")

    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise PandocError(
            f"Pandoc binary not found: {pandoc_bin}. "
            "Make sure pandoc is installed and available in PATH "
            "or set PANDOC_BIN."
        ) from exc

    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        msg_parts = [f"Pandoc failed with exit code {result.returncode}."]
        if stdout:
            msg_parts.append(f"stdout: {stdout}")
        if stderr:
            msg_parts.append(f"stderr: {stderr}")
        message = " ".join(msg_parts)
        raise PandocError(message)
