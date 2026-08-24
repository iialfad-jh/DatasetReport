from pathlib import Path

from datareport.scanner import scan_folder


def test_scan_folder_only_supported_non_hidden_files(tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("a\n1\n", encoding="utf-8")
    (tmp_path / "book.xlsx").write_text("placeholder", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / ".hidden.csv").write_text("ignore", encoding="utf-8")
    (tmp_path / "~$book.xlsx").write_text("ignore", encoding="utf-8")
    hidden_dir = tmp_path / ".cache"
    hidden_dir.mkdir()
    (hidden_dir / "nested.csv").write_text("ignore", encoding="utf-8")

    assert scan_folder(tmp_path) == [tmp_path / "book.xlsx", tmp_path / "data.csv"]

