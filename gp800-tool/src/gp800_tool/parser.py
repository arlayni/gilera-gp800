"""Parse IAW5xReader/Writer .txt export files."""
import hashlib
import re
from pathlib import Path

from .models import MapTable, MapFile


def detect_decimal_separator(text: str) -> str:
    """Detect if file uses comma or period as decimal separator.

    Heuristic: if we see patterns like '3,2' (digit-comma-digit with no space),
    it's likely a comma decimal. If '3.2', it's period.
    """
    comma_decimals = len(re.findall(r'\d,\d', text))
    period_decimals = len(re.findall(r'\d\.\d', text))
    return "," if comma_decimals > period_decimals else "."


def normalize_decimals(text: str) -> str:
    """Normalize comma decimal separators to periods."""
    if detect_decimal_separator(text) == ",":
        # Replace comma decimals: '3,2' -> '3.2'
        # But preserve commas used as value separators (followed by space)
        text = re.sub(r'(\d),(\d)', r'\1.\2', text)
    return text


def detect_encoding(path: Path) -> str:
    """Detect file encoding (UTF-8 or Windows-1252)."""
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "windows-1252"


def parse_txt_file(path: Path | str) -> MapFile:
    """Parse an IAW5xReader/Writer .txt export file.

    Expected format:
    [Map Name]
    AxisLabel: value1, value2, ...
    AxisLabel: value1, value2, ...
    data_row_1
    data_row_2
    ...
    """
    path = Path(path)
    encoding = detect_encoding(path)
    text = path.read_text(encoding=encoding)
    text = normalize_decimals(text)

    # Compute file hash
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    tables: dict[str, MapTable] = {}
    current_name = None
    x_axis_label = ""
    x_axis_values: list[float] = []
    y_axis_label = ""
    y_axis_values: list[float] = []
    data_rows: list[list[float]] = []

    def save_current_table():
        nonlocal current_name, x_axis_values, y_axis_values, data_rows
        if current_name and data_rows:
            tables[current_name] = MapTable(
                name=current_name,
                x_axis_label=x_axis_label,
                x_axis_values=x_axis_values,
                y_axis_label=y_axis_label,
                y_axis_values=y_axis_values,
                data=data_rows,
                value_unit=_guess_unit(current_name),
            )

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Map header: [Map Name]
        if line.startswith("[") and line.endswith("]"):
            save_current_table()
            current_name = line[1:-1].strip()
            x_axis_values = []
            y_axis_values = []
            data_rows = []
            continue

        # Axis definition: Label: val1, val2, ...
        if ":" in line and current_name and not data_rows:
            label, values_str = line.split(":", 1)
            values = [float(v.strip()) for v in values_str.split(",") if v.strip()]
            if not x_axis_values:
                x_axis_label = label.strip()
                x_axis_values = values
            else:
                y_axis_label = label.strip()
                y_axis_values = values
            continue

        # Data row: comma or space separated numbers
        if current_name:
            try:
                parts = [s.strip() for s in line.split(",") if s.strip()]
                if not parts:
                    parts = line.split()
                row = [float(v) for v in parts]
                if row:
                    data_rows.append(row)
            except ValueError:
                continue  # skip unparseable lines

    save_current_table()

    return MapFile(
        source_path=str(path),
        tables=tables,
        encoding=encoding,
        checksum=file_hash,
    )


def _guess_unit(map_name: str) -> str:
    """Guess the value unit from the map name."""
    name_lower = map_name.lower()
    if "fuel" in name_lower:
        return "ms"
    if "ignition" in name_lower or "timing" in name_lower:
        return "deg_btdc"
    if "lambda" in name_lower:
        return "lambda"
    if "rpm" in name_lower or "idle" in name_lower:
        return "rpm"
    return ""
