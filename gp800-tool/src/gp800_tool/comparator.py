"""Cell-by-cell map comparison with severity ranking."""
from .models import MapFile, MapTable, ComparisonCell


def compare_map_files(file_a: MapFile, file_b: MapFile) -> list[ComparisonCell]:
    """Compare two map files cell by cell. Returns list of differing cells."""
    diffs: list[ComparisonCell] = []

    common_tables = set(file_a.tables.keys()) & set(file_b.tables.keys())

    for name in sorted(common_tables):
        table_a = file_a.tables[name]
        table_b = file_b.tables[name]
        diffs.extend(_compare_tables(name, table_a, table_b))

    return diffs


def _compare_tables(name: str, a: MapTable, b: MapTable) -> list[ComparisonCell]:
    diffs = []
    rows = min(a.rows, b.rows)
    cols = min(a.cols, b.cols)

    for r in range(rows):
        for c in range(cols):
            va = a.get_cell(r, c)
            vb = b.get_cell(r, c)
            if va != vb:
                delta = vb - va
                delta_pct = (delta / va * 100) if va != 0 else (100.0 if vb != 0 else 0)

                severity = "OK"
                if abs(delta_pct) > 15:
                    severity = "DANGER"
                elif abs(delta_pct) > 5:
                    severity = "WARNING"

                rpm = a.x_axis_values[c] if c < len(a.x_axis_values) else 0
                load = a.y_axis_values[r] if r < len(a.y_axis_values) else 0

                diffs.append(ComparisonCell(
                    map_name=name, row=r, col=c,
                    rpm=rpm, load=load,
                    value_a=va, value_b=vb,
                    delta=delta, delta_percent=delta_pct,
                    severity=severity,
                ))

    return diffs
