"""Command-line entry point for DatasetReport."""

from pathlib import Path

import typer

from .ai import generate_ai_summary
from .profiler import profile_file
from .renderer import render_report
from .scanner import scan_folder
from .schema import DatasetReport

app = typer.Typer(add_completion=False, help="Generate a basic HTML report for a dataset folder.")


@app.command()
def main(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, readable=True, help="Dataset folder to scan."),
    out: Path = typer.Option(Path("report.html"), "--out", "-o", help="HTML report output path."),
) -> None:
    """Scan files, profile them, and render an HTML report."""

    paths = scan_folder(folder)
    profiles = [profile_file(path) for path in paths]
    report = DatasetReport(files=profiles)
    report.ai_summary = generate_ai_summary(report)
    render_report(report, out)
    typer.echo(f"Report generated: {out.resolve()}")


if __name__ == "__main__":
    app()

