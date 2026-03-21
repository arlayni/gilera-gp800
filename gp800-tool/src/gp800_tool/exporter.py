"""Export map files in IAW5xWriter-compatible .txt format."""
from pathlib import Path
from .models import MapFile


def export_txt_file(map_file: MapFile, output_path: Path | str) -> None:
    """Export a MapFile to .txt format compatible with IAW5xWriter."""
    lines = []

    for name, table in map_file.tables.items():
        lines.append(f"[{name}]")
        lines.append(f"{table.x_axis_label}: {', '.join(str(int(v)) if v == int(v) else str(v) for v in table.x_axis_values)}")
        lines.append(f"{table.y_axis_label}: {', '.join(str(int(v)) if v == int(v) else str(v) for v in table.y_axis_values)}")

        for row in table.data:
            lines.append(", ".join(f"{v:.1f}" if v != int(v) else str(int(v)) for v in row))

        lines.append("")  # blank line between tables

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
