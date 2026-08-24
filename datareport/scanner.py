"""Find supported dataset files in a folder."""

from pathlib import Path

SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}


def _is_ignored(path: Path) -> bool:
    """Return whether a file or one of its parent folders is hidden/temp."""

    for part in path.parts:
        if part.startswith("."):
            return True
    name = path.name
    return name.startswith("~$") or name.endswith("~") or name.startswith("~")


def scan_folder(folder: Path) -> list[Path]:
    """Recursively find CSV and Excel files under *folder*.

    Hidden paths and common editor/Excel temporary files are ignored. Results
    are sorted to make report generation deterministic.
    """

    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Dataset folder does not exist: {folder}")

    files = (
        path
        for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_SUFFIXES
        and not _is_ignored(path.relative_to(folder))
    )
    return sorted(files, key=lambda path: path.as_posix().lower())

