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

    in_table_block = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # [Table] block header (IAW5xReader/Writer format)
        if stripped == "[Table]":
            save_current_table()
            in_table_block = True
            current_name = None
            x_axis_label = ""
            x_axis_values = []
            y_axis_label = ""
            y_axis_values = []
            data_rows = []
            continue

        # Name=, Rows=, Cols= inside a [Table] block
        if in_table_block and "=" in stripped and not data_rows:
            key, val = stripped.split("=", 1)
            key = key.strip()
            if key == "Name":
                current_name = val.strip()
            # Rows= and Cols= are informational; we derive from actual data
            continue

        # Map header: [Map Name] (simple format)
        if stripped.startswith("[") and stripped.endswith("]"):
            save_current_table()
            in_table_block = False
            current_name = stripped[1:-1].strip()
            x_axis_label = ""
            x_axis_values = []
            y_axis_label = ""
            y_axis_values = []
            data_rows = []
            continue

        # Axis definition: Label: val1, val2, ...
        if ":" in stripped and "|" not in stripped and current_name and not data_rows:
            label, values_str = stripped.split(":", 1)
            values = [float(v.strip()) for v in values_str.split(",") if v.strip()]
            if not x_axis_values:
                x_axis_label = label.strip()
                x_axis_values = values
            else:
                y_axis_label = label.strip()
                y_axis_values = values
            continue

        # Pipe-separated data row (IAW5xReader/Writer format)
        if current_name and "|" in stripped:
            parts = [s.strip() for s in stripped.split("|")]
            parts = [p for p in parts if p]  # remove empty from leading/trailing pipes
            if not parts:
                continue

            # Try parsing all parts as numbers (strip % suffix)
            numeric_parts = []
            has_label = False
            for i, p in enumerate(parts):
                clean = p.rstrip("%").strip()
                try:
                    numeric_parts.append(float(clean))
                except ValueError:
                    if i == 0:
                        has_label = True
                    else:
                        numeric_parts = []
                        break

            if has_label and not x_axis_values:
                # Header row like "RPM | 1000 | 2000 | ..."
                x_axis_label = parts[0].strip()
                x_axis_values = numeric_parts
                continue

            if has_label and x_axis_values:
                # Data row with non-numeric label: "Label | 80 | 85 | ..."
                y_val_str = parts[0].rstrip("%").strip()
                try:
                    y_axis_values.append(float(y_val_str))
                except ValueError:
                    y_axis_values.append(0.0)
                data_rows.append(numeric_parts)
                continue

            if numeric_parts and not has_label:
                if not x_axis_values:
                    x_axis_label = "X"
                    x_axis_values = numeric_parts
                elif len(numeric_parts) == len(x_axis_values) + 1:
                    # Row has y-axis label + data: "0 | 80 | 85 | ..."
                    y_axis_values.append(numeric_parts[0])
                    data_rows.append(numeric_parts[1:])
                elif len(numeric_parts) == len(x_axis_values):
                    data_rows.append(numeric_parts)
                else:
                    data_rows.append(numeric_parts)
                continue

            continue

        # Comma or space separated data row (simple format)
        if current_name:
            try:
                parts = [s.strip() for s in stripped.split(",") if s.strip()]
                if not parts:
                    parts = stripped.split()
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
