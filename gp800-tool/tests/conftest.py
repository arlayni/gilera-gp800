"""Shared pytest fixtures for gp800-tool tests."""
import pathlib
import pytest

# ---------------------------------------------------------------------------
# Sample map text — valid, safe values
# Two tables: fuel map (7 RPM cols x 8 TPS rows) and ignition map (7x8).
# Fuel values are in the mid-range (raw 8-bit, 80-160).
# Ignition advances are in the safe range (0–40 deg BTDC).
# ---------------------------------------------------------------------------
SAMPLE_MAP_TXT = """\
[Table]
Name=Fuel Map Front
Rows=8
Cols=7
  RPM  | 1000 | 2000 | 3000 | 4000 | 5000 | 6000 | 7000
  0%   |   80 |   85 |   90 |   95 |  100 |  105 |  110
 10%   |   90 |   95 |  100 |  105 |  110 |  115 |  120
 20%   |  100 |  105 |  110 |  115 |  120 |  125 |  130
 30%   |  110 |  115 |  120 |  125 |  130 |  135 |  140
 40%   |  115 |  120 |  125 |  130 |  135 |  140 |  145
 60%   |  120 |  125 |  130 |  135 |  140 |  145 |  150
 80%   |  130 |  135 |  140 |  145 |  150 |  155 |  160
100%   |  140 |  145 |  150 |  155 |  160 |  160 |  160

[Table]
Name=Ignition Map Front
Rows=8
Cols=7
  RPM  | 1000 | 2000 | 3000 | 4000 | 5000 | 6000 | 7000
  0%   |    5 |    8 |   10 |   12 |   15 |   18 |   20
 10%   |    8 |   10 |   12 |   15 |   18 |   20 |   22
 20%   |   10 |   12 |   15 |   18 |   20 |   22 |   25
 30%   |   12 |   15 |   18 |   20 |   22 |   25 |   28
 40%   |   15 |   18 |   20 |   22 |   25 |   28 |   30
 60%   |   18 |   20 |   22 |   25 |   28 |   30 |   32
 80%   |   20 |   22 |   25 |   28 |   30 |   32 |   35
100%   |   22 |   25 |   28 |   30 |   32 |   35 |   38
"""

# ---------------------------------------------------------------------------
# Sample map text — dangerous values
# Fuel map: row at 10% TPS is all-zero (flash_blocker: all_zero_row).
# Ignition map: top-load rows have values >45 deg (flash_blocker: above_max).
# ---------------------------------------------------------------------------
SAMPLE_MAP_TXT_DANGEROUS = """\
[Table]
Name=Fuel Map Front
Rows=8
Cols=7
  RPM  | 1000 | 2000 | 3000 | 4000 | 5000 | 6000 | 7000
  0%   |   80 |   85 |   90 |   95 |  100 |  105 |  110
 10%   |    0 |    0 |    0 |    0 |    0 |    0 |    0
 20%   |  100 |  105 |  110 |  115 |  120 |  125 |  130
 30%   |  110 |  115 |  120 |  125 |  130 |  135 |  140
 40%   |  115 |  120 |  125 |  130 |  135 |  140 |  145
 60%   |  120 |  125 |  130 |  135 |  140 |  145 |  150
 80%   |  130 |  135 |  140 |  145 |  150 |  155 |  160
100%   |  140 |  145 |  150 |  155 |  160 |  160 |  160

[Table]
Name=Ignition Map Front
Rows=8
Cols=7
  RPM  | 1000 | 2000 | 3000 | 4000 | 5000 | 6000 | 7000
  0%   |    5 |    8 |   10 |   12 |   15 |   18 |   20
 10%   |    8 |   10 |   12 |   15 |   18 |   20 |   22
 20%   |   10 |   12 |   15 |   18 |   20 |   22 |   25
 30%   |   12 |   15 |   18 |   20 |   22 |   25 |   28
 40%   |   15 |   18 |   20 |   22 |   25 |   28 |   30
 60%   |   18 |   20 |   22 |   25 |   28 |   30 |   32
 80%   |   40 |   42 |   44 |   46 |   48 |   50 |   52
100%   |   44 |   46 |   48 |   50 |   52 |   54 |   56
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_map_txt(tmp_path: pathlib.Path) -> pathlib.Path:
    """Write SAMPLE_MAP_TXT to a temp file and return its path."""
    p = tmp_path / "sample_map.txt"
    p.write_text(SAMPLE_MAP_TXT, encoding="utf-8")
    return p


@pytest.fixture
def dangerous_map_txt(tmp_path: pathlib.Path) -> pathlib.Path:
    """Write SAMPLE_MAP_TXT_DANGEROUS to a temp file and return its path."""
    p = tmp_path / "dangerous_map.txt"
    p.write_text(SAMPLE_MAP_TXT_DANGEROUS, encoding="utf-8")
    return p


@pytest.fixture
def schemas_dir() -> pathlib.Path:
    """Return the path to the real knowledge/schemas/ directory."""
    # tests/ lives at gp800-tool/tests/; schemas are two levels up then into knowledge/schemas/
    tests_dir = pathlib.Path(__file__).parent
    schemas = (tests_dir / ".." / ".." / "knowledge" / "schemas").resolve()
    assert schemas.is_dir(), f"schemas dir not found at {schemas}"
    return schemas
