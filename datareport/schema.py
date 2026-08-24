"""Pydantic models used throughout DatasetReport."""

from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    """Basic statistics for one column."""

    name: str
    dtype: str
    missing_count: int = Field(ge=0)
    missing_rate: float = Field(ge=0, le=1)
    sample_values: list[object] = Field(default_factory=list)


class FileProfile(BaseModel):
    """Basic statistics for one supported dataset file."""

    file_name: str
    file_type: str
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    columns: list[ColumnProfile] = Field(default_factory=list)


class DatasetReport(BaseModel):
    """The complete report passed to the renderer."""

    title: str = "Dataset Report"
    files: list[FileProfile] = Field(default_factory=list)
    ai_summary: str = ""

