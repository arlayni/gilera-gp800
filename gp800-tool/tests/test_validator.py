# tests/test_validator.py
from gp800_tool.parser import parse_txt_file
from gp800_tool.validator import validate_map_file
from gp800_tool.schemas import load_safe_ranges

def test_safe_map_passes(sample_map_txt, schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    map_file = parse_txt_file(sample_map_txt)
    results = validate_map_file(map_file, ranges)
    blockers = [r for r in results if r.severity == "BLOCKER"]
    assert len(blockers) == 0

def test_dangerous_map_has_blockers(dangerous_map_txt, schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    map_file = parse_txt_file(dangerous_map_txt)
    results = validate_map_file(map_file, ranges)
    blockers = [r for r in results if r.severity == "BLOCKER"]
    assert len(blockers) >= 1  # all-zero row and ignition >45

def test_all_zero_row_detected(dangerous_map_txt, schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    map_file = parse_txt_file(dangerous_map_txt)
    results = validate_map_file(map_file, ranges)
    zero_row = [r for r in results if "all-zero" in r.message.lower()]
    assert len(zero_row) >= 1

def test_ignition_over_max_detected(dangerous_map_txt, schemas_dir):
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    map_file = parse_txt_file(dangerous_map_txt)
    results = validate_map_file(map_file, ranges)
    over_max = [r for r in results if "ignition" in r.message.lower() and r.severity == "BLOCKER"]
    assert len(over_max) >= 1
