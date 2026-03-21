"""GP800 Tool — CLI entry point."""
import sys
from pathlib import Path

import click

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


if __name__ == "__main__":
    main()
