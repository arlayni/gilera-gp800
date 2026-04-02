"""Tests for models, schema loader, and .txt map file parser."""
from gp800_tool.models import MapTable, MapFile
from gp800_tool.schemas import load_safe_ranges, get_hard_limit
from gp800_tool.parser import parse_txt_file


# ---------------------------------------------------------------------------
# MapTable and MapFile model tests (Task 2)
# ---------------------------------------------------------------------------

def test_map_table_creation():
    table = MapTable(
        name="Fuel Map - Cylinder 1 (Front)",
        x_axis_label="RPM",
        x_axis_values=[1000, 2000, 3000],
        y_axis_label="TPS%",
        y_axis_values=[0, 50, 100],
        data=[[3.2, 3.5, 3.8], [4.5, 5.2, 6.0], [5.0, 5.8, 7.0]],
        value_unit="ms",
    )
    assert table.rows == 3
    assert table.cols == 3
    assert table.get_cell(0, 0) == 3.2
    assert table.get_cell(2, 2) == 7.0


def test_map_table_has_all_zero_row():
    table = MapTable(
        name="Test",
        x_axis_label="RPM",
        x_axis_values=[1000, 2000],
        y_axis_label="TPS%",
        y_axis_values=[0, 100],
        data=[[0, 0], [3.5, 4.0]],
        value_unit="ms",
    )
    assert table.has_all_zero_row() is True


def test_map_table_no_zero_row():
    table = MapTable(
        name="Test",
        x_axis_label="RPM",
        x_axis_values=[1000, 2000],
        y_axis_label="TPS%",
        y_axis_values=[0, 100],
        data=[[1.0, 2.0], [3.5, 4.0]],
        value_unit="ms",
    )
    assert table.has_all_zero_row() is False


def test_map_file_creation():
    mf = MapFile(source_path="test.txt", tables={})
    assert mf.source_path == "test.txt"
    assert len(mf.tables) == 0


# ---------------------------------------------------------------------------
# Schema loader tests (Task 3)
# ---------------------------------------------------------------------------

def test_load_safe_ranges(schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    assert "ignition_advance" in ranges["parameters"]
    assert ranges["parameters"]["ignition_advance"]["hard_limits"]["max"] == 45


def test_get_hard_limit(schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    assert get_hard_limit(ranges, "rev_limiter", "max") == 9500
    assert get_hard_limit(ranges, "idle_rpm", "min") == 600


# ---------------------------------------------------------------------------
# Parser tests (Task 4)
# ---------------------------------------------------------------------------

def test_parse_txt_file(sample_map_txt):
    result = parse_txt_file(sample_map_txt)
    assert len(result.tables) == 2
    assert "Fuel Map Front" in result.tables
    assert "Ignition Map Front" in result.tables


def test_parse_fuel_map_dimensions(sample_map_txt):
    result = parse_txt_file(sample_map_txt)
    fuel = result.tables["Fuel Map Front"]
    assert fuel.cols == 7  # 7 RPM breakpoints
    assert fuel.rows == 8  # 8 TPS breakpoints


def test_parse_fuel_map_values(sample_map_txt):
    result = parse_txt_file(sample_map_txt)
    fuel = result.tables["Fuel Map Front"]
    assert fuel.get_cell(0, 0) == 80  # first data cell
    assert fuel.x_axis_values[0] == 1000  # first RPM
    assert fuel.y_axis_values[-1] == 100  # last TPS


def test_parse_handles_comma_decimals(tmp_path):
    """Test that comma decimal separators are normalized."""
    content = """[Test Map]
RPM: 1000, 2000
TPS%: 0, 100
3,2, 3,5
4,8, 5,5
"""
    p = tmp_path / "comma.txt"
    p.write_text(content)
    result = parse_txt_file(p)
    table = result.tables["Test Map"]
    assert table.get_cell(0, 0) == 3.2
