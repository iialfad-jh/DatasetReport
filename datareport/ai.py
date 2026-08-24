"""AI summary extension point."""

from .schema import DatasetReport


def generate_ai_summary(report: DatasetReport) -> str:
    """Return a local placeholder until an LLM integration is added."""

    file_count = len(report.files)
    total_rows = sum(profile.row_count for profile in report.files)
    return f"This report contains {file_count} file(s) and {total_rows} total row(s)."

