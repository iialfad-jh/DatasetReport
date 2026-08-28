"""Pydantic models used throughout DatasetReport."""

from typing import Any

from pydantic import BaseModel, Field


class ValueCount(BaseModel):
    """A value and its frequency in the analyzed rows."""

    value: Any
    count: int = Field(ge=0)


class ColumnProfile(BaseModel):
    """Basic statistics and quality signals for one column."""

    name: str
    dtype: str
    missing_count: int = Field(ge=0)
    missing_rate: float = Field(ge=0, le=1)
    analyzed_count: int = Field(ge=0)
    unique_count: int = Field(ge=0)
    unique_rate: float = Field(ge=0, le=1)
    top_values: list[ValueCount] = Field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    min_length: int | None = Field(default=None, ge=0)
    max_length: int | None = Field(default=None, ge=0)
    mean_length: float | None = Field(default=None, ge=0)
    is_empty: bool = False
    is_constant: bool = False
    quality_flags: list[str] = Field(default_factory=list)
    sample_values: list[object] = Field(default_factory=list)


class FileProfile(BaseModel):
    """Basic statistics for one supported dataset file."""

    file_name: str
    file_type: str
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    analyzed_row_count: int = Field(ge=0)
    is_sampled: bool = False
    duplicate_row_count: int = Field(ge=0)
    columns: list[ColumnProfile] = Field(default_factory=list)

    @property
    def duplicate_rate(self) -> float:
        """Return the duplicate-row share within the analyzed rows."""

        if self.analyzed_row_count == 0:
            return 0.0
        return self.duplicate_row_count / self.analyzed_row_count


class FileError(BaseModel):
    """A file that could not be read or profiled."""

    file_name: str
    error: str


class DatasetReport(BaseModel):
    """The complete report passed to the renderer."""

    title: str = "Dataset Report"
    files: list[FileProfile] = Field(default_factory=list)
    failed_files: list[FileError] = Field(default_factory=list)
    ai_summary: str = ""

    @property
    def total_rows(self) -> int:
        """Return the combined row count of successfully profiled files."""

        return sum(profile.row_count for profile in self.files)

    @property
    def total_columns(self) -> int:
        """Return the combined column count of successfully profiled files."""

        return sum(profile.column_count for profile in self.files)

    @property
    def quality_column_count(self) -> int:
        """Return how many columns have one or more quality flags."""

        return sum(bool(column.quality_flags) for profile in self.files for column in profile.columns)
