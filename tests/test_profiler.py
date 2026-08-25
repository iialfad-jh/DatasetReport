from pathlib import Path

import pandas as pd

from datareport.profiler import profile_file


def test_profile_csv_returns_shape_and_columns(tmp_path: Path) -> None:
    path = tmp_path / "people.csv"
    pd.DataFrame(
        {"name": ["Ada", "Linus", None], "age": [36, 54, 30]}
    ).to_csv(path, index=False)

    profile = profile_file(path)

    assert profile.file_name == "people.csv"
    assert profile.file_type == "csv"
    assert profile.row_count == 3
    assert profile.column_count == 2
    assert [column.name for column in profile.columns] == ["name", "age"]
    assert profile.columns[0].missing_count == 1
    assert profile.columns[0].missing_rate == 1 / 3
    assert profile.columns[0].sample_values[:2] == ["Ada", "Linus"]
    assert profile.columns[0].unique_count == 2
    assert profile.columns[0].min_length == 3
    assert profile.columns[0].max_length == 5
    assert profile.columns[1].mean == 40.0
    assert profile.columns[1].median == 36.0
    assert profile.columns[1].is_constant is False


def test_profile_csv_keeps_total_rows_when_sampling(tmp_path: Path) -> None:
    path = tmp_path / "numbers.csv"
    pd.DataFrame({"value": [1, 2, 2, 3, 4]}).to_csv(path, index=False)

    profile = profile_file(path, sample_rows=2)

    assert profile.row_count == 5
    assert profile.analyzed_row_count == 2
    assert profile.is_sampled is True
    assert profile.duplicate_row_count == 0
    assert profile.columns[0].sample_values == [1, 2]
