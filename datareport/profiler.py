"""Create basic pandas-based profiles for supported files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .schema import ColumnProfile, FileProfile


def _read_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _sample_value(value: Any) -> object:
    """Convert pandas/numpy values into values safe for JSON/template use."""

    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def profile_file(path: Path, sample_rows: int = 10000) -> FileProfile:
    """Profile a CSV or Excel file using basic shape and missing-value stats."""

    if sample_rows < 0:
        raise ValueError("sample_rows must be non-negative")
    path = Path(path)
    dataframe = _read_dataframe(path)
    row_count, column_count = dataframe.shape

    columns: list[ColumnProfile] = []
    denominator = row_count or 1
    for name in dataframe.columns:
        series = dataframe[name]
        missing_count = int(series.isna().sum())
        values = [_sample_value(value) for value in series.head(sample_rows).tolist()]
        columns.append(
            ColumnProfile(
                name=str(name),
                dtype=str(series.dtype),
                missing_count=missing_count,
                missing_rate=missing_count / denominator if row_count else 0.0,
                sample_values=values[:5],
            )
        )

    return FileProfile(
        file_name=path.name,
        file_type=path.suffix.lower().lstrip("."),
        row_count=int(row_count),
        column_count=int(column_count),
        columns=columns,
    )
