"""Create pandas-based profiles for supported files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .schema import ColumnProfile, FileProfile, ValueCount


def _read_sample(path: Path, sample_rows: int) -> tuple[pd.DataFrame, int]:
    """Read at most *sample_rows* for analysis while counting all CSV rows."""

    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        dataframe = pd.read_excel(path)
        return dataframe.head(sample_rows), len(dataframe)
    if suffix != ".csv":
        raise ValueError(f"Unsupported file type: {path.suffix}")

    chunks: list[pd.DataFrame] = []
    row_count = 0
    analyzed_rows = 0
    chunk_size = max(1000, min(sample_rows or 1000, 10000))
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        row_count += len(chunk)
        if analyzed_rows < sample_rows:
            remaining = sample_rows - analyzed_rows
            selected = chunk.head(remaining)
            chunks.append(selected)
            analyzed_rows += len(selected)
    if chunks:
        return pd.concat(chunks, ignore_index=True), row_count
    return pd.read_csv(path, nrows=0), row_count


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


def _numeric_value(value: Any) -> float | None:
    value = _sample_value(value)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _column_profile(name: Any, series: pd.Series) -> ColumnProfile:
    analyzed_count = len(series)
    missing_count = int(series.isna().sum())
    non_missing = series.dropna()
    unique_count = int(non_missing.nunique())
    denominator = analyzed_count or 1
    top_values = [
        ValueCount(value=_sample_value(value), count=int(count))
        for value, count in non_missing.value_counts(dropna=False).head(5).items()
    ]
    profile = ColumnProfile(
        name=str(name),
        dtype=str(series.dtype),
        analyzed_count=analyzed_count,
        missing_count=missing_count,
        missing_rate=missing_count / denominator if analyzed_count else 0.0,
        unique_count=unique_count,
        unique_rate=unique_count / denominator if analyzed_count else 0.0,
        top_values=top_values,
        is_empty=non_missing.empty,
        is_constant=unique_count <= 1 and not non_missing.empty,
        sample_values=[_sample_value(value) for value in series.head(5).tolist()],
    )

    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(non_missing, errors="coerce").dropna()
        if not numeric.empty:
            profile.min_value = _numeric_value(numeric.min())
            profile.max_value = _numeric_value(numeric.max())
            profile.mean = _numeric_value(numeric.mean())
            profile.median = _numeric_value(numeric.median())
            profile.std = _numeric_value(numeric.std(ddof=0))
    elif pd.api.types.is_string_dtype(series) or series.dtype == object:
        lengths = non_missing.astype(str).str.len()
        if not lengths.empty:
            profile.min_length = int(lengths.min())
            profile.max_length = int(lengths.max())
            profile.mean_length = float(lengths.mean())
    return profile


def profile_file(path: Path, sample_rows: int = 10000) -> FileProfile:
    """Profile a file, limiting detailed analysis to the first *sample_rows*."""

    if sample_rows < 0:
        raise ValueError("sample_rows must be non-negative")
    path = Path(path)
    dataframe, row_count = _read_sample(path, sample_rows)
    columns = [_column_profile(name, dataframe[name]) for name in dataframe.columns]

    return FileProfile(
        file_name=path.name,
        file_type=path.suffix.lower().lstrip("."),
        row_count=int(row_count),
        column_count=int(len(dataframe.columns)),
        analyzed_row_count=int(len(dataframe)),
        is_sampled=row_count > len(dataframe),
        duplicate_row_count=int(dataframe.duplicated().sum()),
        columns=columns,
    )
