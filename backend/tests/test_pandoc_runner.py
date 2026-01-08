import pytest

from app.services.generation.pandoc_runner import (
    PandocError,
    generate_docx_from_markdown,
    get_pandoc_bin,
)


class FakeCompletedProcess:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_get_pandoc_bin_uses_env_if_set(monkeypatch):
    monkeypatch.setenv("PANDOC_BIN", "/custom/pandoc")
    assert get_pandoc_bin() == "/custom/pandoc"


def test_get_pandoc_bin_defaults_to_pandoc(monkeypatch):
    monkeypatch.delenv("PANDOC_BIN", raising=False)
    assert get_pandoc_bin() == "pandoc"


def test_generate_docx_from_markdown_runs_pandoc_with_expected_args(
    monkeypatch, tmp_path
):
    md_path = tmp_path / "report.md"
    md_path.write_text("# Test report\n", encoding="utf-8")

    output_path = tmp_path / "report.docx"
    reference_path = tmp_path / "misis_reference.docx"
    reference_path.write_text("", encoding="utf-8")

    called = {}

    def fake_run(cmd, check, capture_output, text):
        called["cmd"] = cmd
        called["check"] = check
        called["capture_output"] = capture_output
        called["text"] = text
        return FakeCompletedProcess(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "app.services.generation.pandoc_runner.subprocess.run", fake_run
    )

    generate_docx_from_markdown(
        md_path=md_path,
        output_path=output_path,
        reference_doc_path=reference_path,
    )

    assert "cmd" in called
    cmd = called["cmd"]

    assert cmd[0] == "pandoc"
    assert str(md_path) in cmd
    assert "-o" in cmd
    assert str(output_path) in cmd
    assert "--reference-doc" in cmd
    assert str(reference_path) in cmd
    assert "--toc" in cmd

    assert called["check"] is False
    assert called["capture_output"] is True
    assert called["text"] is True


def test_generate_docx_from_markdown_raises_if_md_missing(tmp_path):
    md_path = tmp_path / "missing.md"
    output_path = tmp_path / "report.docx"

    with pytest.raises(PandocError) as exc_info:
        generate_docx_from_markdown(
            md_path=md_path,
            output_path=output_path,
            reference_doc_path=None,
        )

    assert "does not exist" in str(exc_info.value)


def test_generate_docx_from_markdown_raises_on_nonzero_exit_code(monkeypatch, tmp_path):
    md_path = tmp_path / "report.md"
    md_path.write_text("# Test report\n", encoding="utf-8")

    output_path = tmp_path / "report.docx"

    def fake_run(cmd, check, capture_output, text):
        return FakeCompletedProcess(
            returncode=2,
            stdout="fake stdout",
            stderr="fake stderr",
        )

    monkeypatch.setattr(
        "app.services.generation.pandoc_runner.subprocess.run", fake_run
    )

    with pytest.raises(PandocError) as exc_info:
        generate_docx_from_markdown(
            md_path=md_path,
            output_path=output_path,
            reference_doc_path=None,
        )

    message = str(exc_info.value)
    assert "exit code 2" in message
    assert "fake stdout" in message
    assert "fake stderr" in message


def test_generate_docx_from_markdown_raises_if_pandoc_not_found(monkeypatch, tmp_path):
    md_path = tmp_path / "report.md"
    md_path.write_text("# Test report\n", encoding="utf-8")

    output_path = tmp_path / "report.docx"

    def fake_run(cmd, check, capture_output, text):
        raise FileNotFoundError("pandoc not found")

    monkeypatch.setattr(
        "app.services.generation.pandoc_runner.subprocess.run", fake_run
    )

    with pytest.raises(PandocError) as exc_info:
        generate_docx_from_markdown(
            md_path=md_path,
            output_path=output_path,
            reference_doc_path=None,
        )

    message = str(exc_info.value)
    assert "Pandoc binary not found" in message
