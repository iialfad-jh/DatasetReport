"""Render DatasetReport models as HTML using Jinja2."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schema import DatasetReport

TEMPLATE_DIR = Path(__file__).parent / "templates"


def render_report(report: DatasetReport, out_path: Path) -> None:
    """Render *report* to *out_path*, creating its parent directory if needed."""

    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = environment.get_template("report.html.j2")
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.render(report=report), encoding="utf-8")

