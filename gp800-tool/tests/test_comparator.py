# tests/test_comparator.py
from gp800_tool.parser import parse_txt_file
from gp800_tool.comparator import compare_map_files

def test_compare_identical(sample_map_txt):
    a = parse_txt_file(sample_map_txt)
    b = parse_txt_file(sample_map_txt)
    diffs = compare_map_files(a, b)
    assert len(diffs) == 0  # no differences

def test_compare_different(sample_map_txt, dangerous_map_txt):
    a = parse_txt_file(sample_map_txt)
    b = parse_txt_file(dangerous_map_txt)
    diffs = compare_map_files(a, b)
    assert len(diffs) > 0
    danger = [d for d in diffs if d.severity == "DANGER"]
    assert len(danger) > 0  # the all-zero row and >45 ignition should flag
