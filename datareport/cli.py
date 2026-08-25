"""Command-line entry point for DatasetReport."""

from pathlib import Path

import typer

from .ai import generate_ai_summary
from .profiler import profile_file
from .renderer import render_report
from .scanner import scan_folder
from .schema import DatasetReport, FileError

app = typer.Typer(add_completion=False, help="Generate a basic HTML report for a dataset folder.")


@app.command()
def main(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, readable=True, help="Dataset folder to scan."),
    out: Path = typer.Option(Path("report.html"), "--out", "-o", help="HTML report output path."),
    sample_rows: int = typer.Option(10000, "--sample-rows", min=0, help="Rows per file used for detailed analysis."),
) -> None:
    """Scan files, profile them, and render an HTML report."""

    paths = scan_folder(folder)
    profiles = []
    failed_files = []
    for path in paths:
        try:
            profiles.append(profile_file(path, sample_rows=sample_rows))
        except Exception as exc:
            failed_files.append(FileError(file_name=path.name, error=str(exc)))
    report = DatasetReport(files=profiles, failed_files=failed_files)
    report.ai_summary = generate_ai_summary(report)
    render_report(report, out)
    typer.echo(f"Report generated: {out.resolve()}")


if __name__ == "__main__":
    app()
