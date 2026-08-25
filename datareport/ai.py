"""AI summary extension point."""

from .schema import DatasetReport


def generate_ai_summary(report: DatasetReport) -> str:
    """Return a local placeholder until an LLM integration is added."""

    file_count = len(report.files)
    total_rows = sum(profile.row_count for profile in report.files)
    quality_columns = sum(
        column.is_empty or column.is_constant or column.missing_count > 0
        for profile in report.files
        for column in profile.columns
    )
    failed = len(report.failed_files)
    suffix = f" {failed} file(s) failed to load." if failed else ""
    return f"This report contains {file_count} file(s) and {total_rows} total row(s). {quality_columns} column(s) have basic quality flags.{suffix}"
