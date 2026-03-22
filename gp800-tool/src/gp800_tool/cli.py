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


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--schemas", type=click.Path(exists=True), default=None)
def validate(file, schemas):
    """Run pre-flash safety validation on a map file."""
    schemas_dir = _resolve_schemas(schemas)
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
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
    """Quick go/no-go assessment (GREEN/YELLOW/RED)."""
    schemas_dir = _resolve_schemas(schemas)
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
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
        click.echo(f"Detected {len(dump.regions)} calibration tables:")
        for reg in dump.regions:
            click.echo(f"  {reg.name}")
            click.echo(f"    Offset: 0x{reg.offset:05X}  Size: {reg.rows}x{reg.cols}")
            if reg.x_axis:
                click.echo(f"    X-axis: {reg.x_axis.axis_type} [{reg.x_axis.values[0]}-{reg.x_axis.values[-1]}]")
            flat = reg.flat_values()
            click.echo(f"    Values: {min(flat)}-{max(flat)} (mean {sum(flat)/len(flat):.0f})")
            # Print first 3 rows
            for r in range(min(3, reg.rows)):
                row_str = " ".join(f"{v:5d}" for v in reg.values[r])
                click.echo(f"    row[{r:2d}]: {row_str}")
            if reg.rows > 3:
                click.echo(f"    ... ({reg.rows - 3} more rows)")
            click.echo()


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


if __name__ == "__main__":
    main()
