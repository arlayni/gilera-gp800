# tests/test_exporter.py
from gp800_tool.parser import parse_txt_file
from gp800_tool.exporter import export_txt_file

def test_round_trip(sample_map_txt, tmp_path):
    """Parse -> export -> re-parse must produce identical data."""
    original = parse_txt_file(sample_map_txt)

    output_path = tmp_path / "exported.txt"
    export_txt_file(original, output_path)

    re_parsed = parse_txt_file(output_path)

    assert set(original.table_names) == set(re_parsed.table_names)

    for name in original.table_names:
        orig_table = original.tables[name]
        new_table = re_parsed.tables[name]
        assert orig_table.rows == new_table.rows
        assert orig_table.cols == new_table.cols
        for r in range(orig_table.rows):
            for c in range(orig_table.cols):
                assert abs(orig_table.get_cell(r, c) - new_table.get_cell(r, c)) < 0.001
