from pathlib import Path

from typer.testing import CliRunner

from datareport.cli import app


def test_cli_continues_when_one_file_fails(tmp_path: Path) -> None:
    (tmp_path / "valid.csv").write_text("value\n1\n", encoding="utf-8")
    (tmp_path / "broken.csv").write_bytes(b"\xff\xfe\x00")
    output = tmp_path / "report.html"

    result = CliRunner().invoke(app, [str(tmp_path), "--out", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "valid.csv" in html
    assert "broken.csv" in html
    assert "could not be processed" in html


def test_cli_renders_overview_and_quality_columns(tmp_path: Path) -> None:
    (tmp_path / "quality.csv").write_text(
        "record_id,value\na,1\nb,\nc,3\n", encoding="utf-8"
    )
    output = tmp_path / "report.html"

    result = CliRunner().invoke(app, [str(tmp_path), "--out", str(output)])

    assert result.exit_code == 0
    html = output.read_text(encoding="utf-8")
    assert "Dataset overview" in html
    assert "Missing count" in html
    assert "Missing rate" in html
    assert "Possible identifier" in html
    assert "High missing rate" in html


def test_cli_renders_duplicate_rate(tmp_path: Path) -> None:
    (tmp_path / "duplicates.csv").write_text(
        "value\na\na\nb\nb\n", encoding="utf-8"
    )
    output = tmp_path / "report.html"

    result = CliRunner().invoke(app, [str(tmp_path), "--out", str(output)])

    assert result.exit_code == 0
    html = output.read_text(encoding="utf-8")
    assert "Duplicate rows in analyzed data: 2 (50.00%)" in html
