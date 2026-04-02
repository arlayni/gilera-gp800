"""GP800 Tool — CLI entry point."""
import sys
from pathlib import Path

import click

from .binary_parser import parse_binary, compare_binaries, IAW5AM_BIN_SIZE
from .parser import parse_txt_file
from .validator import validate_map_file
from .comparator import compare_map_files
from .schemas import load_safe_ranges, find_schemas_dir


@click.group()
@click.version_option()
def main():
    """Gilera GP800 ECU map analysis and safety validation tool.

    Makes it harder to flash a dangerous map than a safe one.
    """
    pass


def _resolve_schemas(schemas_path: str | None) -> Path:
    if schemas_path:
        return Path(schemas_path)
    found = find_schemas_dir()
    if not found:
        click.echo("ERROR: Cannot find knowledge/schemas/ directory. Use --schemas to specify.", err=True)
        sys.exit(1)
    return found


@main.command()
@click.argument("file", type=click.Path(exists=True))
def parse(file):
    """Parse and summarize a map file."""
    map_file = parse_txt_file(file)
    click.echo(f"File: {map_file.source_path}")
    click.echo(f"Encoding: {map_file.encoding}")
    click.echo(f"SHA256: {map_file.checksum[:16]}...")
    click.echo(f"Tables found: {len(map_file.tables)}")
    click.echo()
    for name, table in map_file.tables.items():
        click.echo(f"  [{name}]")
        click.echo(f"    Size: {table.rows} x {table.cols}")
        click.echo(f"    X-axis: {table.x_axis_label} ({table.x_axis_values[0]}-{table.x_axis_values[-1]})")
        click.echo(f"    Y-axis: {table.y_axis_label} ({table.y_axis_values[0]}-{table.y_axis_values[-1]})")
        click.echo(f"    Values: {table.min_value():.1f} to {table.max_value():.1f} {table.value_unit}")
        click.echo()


def _is_bin_file(path: str) -> bool:
    return path.lower().endswith(".bin")


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--schemas", type=click.Path(exists=True), default=None)
def validate(file, schemas):
    """Run pre-flash safety validation on a map file (.txt or .bin)."""
    schemas_dir = _resolve_schemas(schemas)
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")

    if _is_bin_file(file):
        from .validator import validate_binary
        dump = parse_binary(file)
        results = validate_binary(dump, ranges)
    else:
        map_file = parse_txt_file(file)
        results = validate_map_file(map_file, ranges)

    blockers = [r for r in results if r.severity == "BLOCKER"]
    warnings = [r for r in results if r.severity == "WARNING"]
    passed = [r for r in results if r.passed]

    for r in passed:
        click.echo(click.style(f"  PASS: {r.message}", fg="green"))
    for r in warnings:
        click.echo(click.style(f"  WARN: {r.message}", fg="yellow"))
    for r in blockers:
        click.echo(click.style(f"  BLOCKER: {r.message}", fg="red", bold=True))

    click.echo()
    if blockers:
        click.echo(click.style(f"RESULT: {len(blockers)} BLOCKER(s) found — DO NOT FLASH", fg="red", bold=True))
        sys.exit(1)
    elif warnings:
        click.echo(click.style(f"RESULT: {len(warnings)} warning(s) — flash with caution", fg="yellow"))
    else:
        click.echo(click.style("RESULT: All checks passed", fg="green"))


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--schemas", type=click.Path(exists=True), default=None)
def quickcheck(file, schemas):
    """Quick go/no-go assessment (GREEN/YELLOW/RED). Works on .txt and .bin."""
    schemas_dir = _resolve_schemas(schemas)
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")

    if _is_bin_file(file):
        from .validator import validate_binary
        dump = parse_binary(file)
        results = validate_binary(dump, ranges)
    else:
        map_file = parse_txt_file(file)
        results = validate_map_file(map_file, ranges)

    blockers = [r for r in results if r.severity == "BLOCKER"]
    warnings = [r for r in results if r.severity == "WARNING"]

    if blockers:
        click.echo(click.style("RED — DO NOT FLASH", fg="red", bold=True))
        sys.exit(1)
    elif warnings:
        click.echo(click.style("YELLOW — FLASH WITH CAUTION", fg="yellow"))
    else:
        click.echo(click.style("GREEN — SAFE TO FLASH", fg="green"))


@main.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def compare(file1, file2):
    """Compare two map files cell by cell."""
    a = parse_txt_file(file1)
    b = parse_txt_file(file2)
    diffs = compare_map_files(a, b)

    if not diffs:
        click.echo("Maps are identical.")
        return

    click.echo(f"Found {len(diffs)} differences:")
    click.echo()

    for d in sorted(diffs, key=lambda x: x.severity, reverse=True):
        color = {"DANGER": "red", "WARNING": "yellow", "OK": "white"}.get(d.severity, "white")
        click.echo(click.style(
            f"  [{d.severity}] {d.map_name} @ RPM={d.rpm} Load={d.load}: "
            f"{d.value_a} -> {d.value_b} (delta: {d.delta:+.1f}, {d.delta_percent:+.1f}%)",
            fg=color,
        ))


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--tables/--no-tables", default=True, help="Show detected tables")
@click.option("--axes/--no-axes", default=True, help="Show detected axes")
def bindump(file, tables, axes):
    """Analyze a binary (.bin) ECU dump file."""
    path = Path(file)
    data = path.read_bytes()

    if len(data) != IAW5AM_BIN_SIZE:
        click.echo(click.style(
            f"WARNING: File size {len(data)} != expected {IAW5AM_BIN_SIZE} bytes",
            fg="yellow"))

    dump = parse_binary(path)

    # Identity
    ident = dump.identity
    click.echo(f"File:          {dump.source_path}")
    click.echo(f"Size:          {dump.file_size:,} bytes")
    click.echo(f"SHA256:        {dump.checksum[:16]}...")
    click.echo(f"Platform:      {ident.platform}")
    click.echo(f"Variant:       {ident.variant}")
    click.echo(f"Software:      {ident.software_id}")
    click.echo(f"Drawing:       {ident.drawing_number}")
    click.echo(f"Hardware:      {ident.hardware_id}")
    click.echo(f"Homologation:  {ident.homologation}")
    click.echo()

    if axes and dump.axes:
        click.echo(f"Detected {len(dump.axes)} axis breakpoint arrays:")
        for ax in dump.axes:
            label = f"  {ax.axis_type:8s} @ 0x{ax.offset:05X}"
            vals_str = ", ".join(str(v) for v in ax.values[:10])
            if ax.count > 10:
                vals_str += f", ... ({ax.count} total)"
            click.echo(f"{label}: [{vals_str}]")
        click.echo()

    if tables and dump.regions:
        # Separate known (named) tables from heuristic discoveries
        named = [r for r in dump.regions if not r.name.startswith("table_")]
        heuristic = [r for r in dump.regions if r.name.startswith("table_")]

        if named:
            click.echo(f"Named calibration tables ({len(named)}):")
            for reg in named:
                type_label = f" [{reg.value_type}]" if reg.value_type else ""
                click.echo(f"  {reg.name}{type_label}")
                click.echo(f"    Offset: 0x{reg.offset:05X}  Size: {reg.rows}x{reg.cols}")
                if reg.x_axis:
                    click.echo(f"    X-axis: {reg.x_axis.axis_type} [{reg.x_axis.values[0]}-{reg.x_axis.values[-1]}] ({reg.x_axis.count} points)")
                flat = reg.flat_values()
                if flat:
                    click.echo(f"    Values: {min(flat)}-{max(flat)} (mean {sum(flat)/len(flat):.0f})")
                for r in range(min(3, reg.rows)):
                    row_str = " ".join(f"{v:5d}" for v in reg.values[r])
                    click.echo(f"    row[{r:2d}]: {row_str}")
                if reg.rows > 3:
                    click.echo(f"    ... ({reg.rows - 3} more rows)")
                click.echo()

        if heuristic:
            click.echo(f"Additional detected tables ({len(heuristic)}):")
            for reg in heuristic:
                flat = reg.flat_values()
                val_info = f"values {min(flat)}-{max(flat)}" if flat else ""
                click.echo(f"  {reg.name}  {reg.rows}x{reg.cols}  {val_info}")


@main.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def bindiff(file1, file2):
    """Compare two binary (.bin) ECU dump files."""
    a = parse_binary(file1)
    b = parse_binary(file2)

    click.echo(f"File A: {a.source_path}")
    click.echo(f"  {a.identity.variant} — {a.identity.software_id} ({a.identity.homologation})")
    click.echo(f"File B: {b.source_path}")
    click.echo(f"  {b.identity.variant} — {b.identity.software_id} ({b.identity.homologation})")
    click.echo()

    diffs = compare_binaries(a, b)
    if not diffs:
        click.echo(click.style("Files are identical.", fg="green"))
        return

    for d in diffs:
        if d["type"] == "size_mismatch":
            click.echo(click.style(
                f"Size mismatch: {d['a_size']} vs {d['b_size']} bytes",
                fg="red", bold=True))
        elif d["type"] == "byte_diff_summary":
            click.echo(f"Total bytes changed: {d['total_changed']:,}")
            click.echo(f"Regions: {d['region_count']}")
            click.echo()
            for start, end, count in d["regions"][:30]:
                size = end - start + 1
                click.echo(f"  0x{start:05X}-0x{end:05X}  ({size:6,} bytes, {count:5,} changed)")
            if len(d["regions"]) > 30:
                click.echo(f"  ... and {len(d['regions']) - 30} more regions")
        elif d["type"] == "identity_diff":
            click.echo(click.style(
                f"  {d['field']}: {d['a']} -> {d['b']}", fg="yellow"))
    click.echo()


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def bin2txt(file, output):
    """Export named tables from a binary (.bin) dump to readable .txt format."""
    dump = parse_binary(file)

    if not dump.regions:
        click.echo(click.style("No named tables found in binary.", fg="red"))
        sys.exit(1)

    named = [r for r in dump.regions if not r.name.startswith("table_")]
    if not named:
        click.echo(click.style("No named tables found (unknown variant?).", fg="red"))
        sys.exit(1)

    from .models import MapFile, MapTable

    tables = {}
    for reg in named:
        x_label = "RPM"
        x_vals = [float(v) for v in reg.x_axis.values] if reg.x_axis else [float(i) for i in range(reg.cols)]
        y_label = "Load"
        y_vals = [float(i) for i in range(reg.rows)]

        tables[reg.name] = MapTable(
            name=reg.name,
            x_axis_label=x_label,
            x_axis_values=x_vals,
            y_axis_label=y_label,
            y_axis_values=y_vals,
            data=[[float(v) for v in row] for row in reg.values],
            value_unit=reg.value_type.replace("fuel_us", "us").replace("degrees", "deg_btdc"),
        )

    mf = MapFile(source_path=str(file), tables=tables, checksum=dump.checksum)

    from .exporter import export_txt_file
    export_txt_file(mf, output)

    click.echo(f"Exported {len(tables)} tables to {output}")
    for name in tables:
        t = tables[name]
        click.echo(f"  {name}: {t.rows}x{t.cols}")


@main.command()
@click.argument("txt_file", type=click.Path(exists=True))
@click.argument("base_bin", type=click.Path(exists=True))
@click.argument("output_bin", type=click.Path())
def txt2bin(txt_file, base_bin, output_bin):
    """Write modified .txt table values back into a binary (.bin) file.

    Takes a .txt file (from bin2txt), a base .bin to patch, and writes
    the result to output_bin. The base binary is NOT modified.
    """
    from .binary_parser import KNOWN_TABLES, KNOWN_AXES, read_u16le
    import struct

    # Parse the txt file
    map_file = parse_txt_file(txt_file)

    # Read the base binary
    base_path = Path(base_bin)
    raw = bytearray(base_path.read_bytes())

    if len(raw) != IAW5AM_BIN_SIZE:
        click.echo(click.style(
            f"WARNING: Base binary size {len(raw)} != expected {IAW5AM_BIN_SIZE}",
            fg="yellow"))

    patched_count = 0
    for tdef in KNOWN_TABLES:
        if tdef["offset"] is None:
            continue

        table_name = tdef["name"]
        table = map_file.get_table(table_name)
        if table is None:
            continue

        offset = tdef["offset"]
        cols = tdef["cols"]
        rows = tdef["rows"]

        if table.rows != rows or table.cols != cols:
            click.echo(click.style(
                f"WARNING: {table_name} dimensions {table.rows}x{table.cols} "
                f"don't match expected {rows}x{cols} — skipping",
                fg="yellow"))
            continue

        # Write values back into binary
        for r in range(rows):
            for c in range(cols):
                val = int(table.data[r][c])
                byte_offset = offset + (r * cols + c) * 2
                struct.pack_into("<H", raw, byte_offset, val)

        patched_count += 1
        click.echo(f"  Patched {table_name}: {rows}x{cols}")

    if patched_count == 0:
        click.echo(click.style("No tables were patched.", fg="red"))
        sys.exit(1)

    # Write output
    out_path = Path(output_bin)
    out_path.write_bytes(bytes(raw))
    click.echo(f"Written {out_path} ({len(raw):,} bytes, {patched_count} tables patched)")


if __name__ == "__main__":
    main()
