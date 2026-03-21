"""Data models for IAW 5AM ECU map files."""
from dataclasses import dataclass, field


@dataclass
class MapTable:
    """A single 2D map table from the ECU."""
    name: str
    x_axis_label: str
    x_axis_values: list[float]
    y_axis_label: str
    y_axis_values: list[float]
    data: list[list[float]]
    value_unit: str = ""

    @property
    def rows(self) -> int:
        return len(self.data)

    @property
    def cols(self) -> int:
        return len(self.data[0]) if self.data else 0

    def get_cell(self, row: int, col: int) -> float:
        return self.data[row][col]

    def has_all_zero_row(self) -> bool:
        """Check if any row is entirely zeros (flash blocker)."""
        return any(all(v == 0 for v in row) for row in self.data)

    def has_all_max_row(self, max_val: float = 255) -> bool:
        """Check if any row is entirely at max value (flash blocker)."""
        return any(all(v >= max_val for v in row) for row in self.data)

    def min_value(self) -> float:
        return min(min(row) for row in self.data)

    def max_value(self) -> float:
        return max(max(row) for row in self.data)


@dataclass
class MapFile:
    """A complete ECU map file containing multiple tables."""
    source_path: str
    tables: dict[str, MapTable] = field(default_factory=dict)
    encoding: str = "utf-8"
    checksum: str = ""

    def get_table(self, name: str) -> MapTable | None:
        return self.tables.get(name)

    @property
    def table_names(self) -> list[str]:
        return list(self.tables.keys())


@dataclass
class ValidationResult:
    """Result of a safety validation check."""
    passed: bool
    check_name: str
    message: str
    severity: str = "INFO"  # INFO, WARNING, BLOCKER
    cell_references: list[str] = field(default_factory=list)


@dataclass
class ComparisonCell:
    """A single cell difference between two maps."""
    map_name: str
    row: int
    col: int
    rpm: float
    load: float
    value_a: float
    value_b: float
    delta: float
    delta_percent: float
    severity: str = "OK"  # OK, WARNING, DANGER
