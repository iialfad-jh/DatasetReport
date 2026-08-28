from pathlib import Path

import pandas as pd

from datareport.profiler import profile_file
from datareport.schema import FileProfile


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


def test_profile_csv_falls_back_to_gb18030_for_chinese_data(tmp_path: Path) -> None:
    path = tmp_path / "chinese.csv"
    path.write_bytes("姓名,城市\n小明,北京\n小红,上海\n".encode("gb18030"))

    profile = profile_file(path)

    assert [column.name for column in profile.columns] == ["姓名", "城市"]
    assert profile.columns[0].sample_values == ["小明", "小红"]
    assert profile.row_count == 2


def test_profile_csv_keeps_total_rows_when_sampling(tmp_path: Path) -> None:
    path = tmp_path / "numbers.csv"
    pd.DataFrame({"value": [1, 2, 2, 3, 4]}).to_csv(path, index=False)

    profile = profile_file(path, sample_rows=2)

    assert profile.row_count == 5
    assert profile.analyzed_row_count == 2
    assert profile.is_sampled is True
    assert profile.duplicate_row_count == 0
    assert profile.columns[0].sample_values == [1, 2]


def test_profile_csv_exposes_duplicate_rate_for_analyzed_rows(tmp_path: Path) -> None:
    path = tmp_path / "duplicates.csv"
    pd.DataFrame({"value": ["a", "a", "b", "b"]}).to_csv(path, index=False)

    profile = profile_file(path)

    assert profile.duplicate_row_count == 2
    assert profile.duplicate_rate == 0.5


def test_duplicate_rate_is_zero_when_no_rows_were_analyzed() -> None:
    profile = FileProfile(
        file_name="empty.csv",
        file_type="csv",
        row_count=0,
        column_count=0,
        analyzed_row_count=0,
        duplicate_row_count=0,
    )

    assert profile.duplicate_rate == 0.0


def test_profile_csv_adds_actionable_quality_flags(tmp_path: Path) -> None:
    path = tmp_path / "quality.csv"
    pd.DataFrame(
        {
            "record_id": ["a", "b", "c", "d", "e"],
            "constant": [1, 1, 1, 1, 1],
            "mostly_missing": [None, None, None, "value", None],
            "empty": [None, None, None, None, None],
        }
    ).to_csv(path, index=False)

    profile = profile_file(path)
    flags = {column.name: column.quality_flags for column in profile.columns}

    assert flags["record_id"] == ["Possible identifier"]
    assert flags["constant"] == ["Constant value"]
    assert flags["mostly_missing"] == ["Constant value", "High missing rate"]
    assert flags["empty"] == ["Empty column"]
