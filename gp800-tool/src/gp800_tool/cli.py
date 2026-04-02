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
    click.echo(f"Cal Checksum:  0x{dump.cal_checksum:04X}")
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

    # Calculate checksums
    from .binary_parser import calculate_checksum
    original_csum = calculate_checksum(base_path.read_bytes())
    patched_csum = calculate_checksum(bytes(raw))

    # Write output
    out_path = Path(output_bin)
    out_path.write_bytes(bytes(raw))
    click.echo(f"Written {out_path} ({len(raw):,} bytes, {patched_count} tables patched)")
    click.echo(f"Checksum: 0x{original_csum:04X} -> 0x{patched_csum:04X}")
    if original_csum != patched_csum:
        click.echo(click.style(
            f"  Checksum changed (expected — you modified calibration data)",
            fg="yellow"))


# --- K-Line / ECU Communication Commands ---

@main.command()
@click.argument("port", type=str)
def connect(port):
    """Connect to ECU via USB-KKL adapter and show ECU info.

    PORT is the serial port (e.g., /dev/ttyUSB0 or COM3).
    """
    from .ecucomm import ECUConnection

    click.echo(f"Connecting to {port} ...")
    ecu = ECUConnection(port)
    try:
        info = ecu.connect()
        click.echo(click.style("Connected!", fg="green"))
        click.echo(f"  Software:  {info.software_id}")
        click.echo(f"  Hardware:  {info.hardware_id}")
        click.echo(f"  Raw data:  {info.raw_data.hex()}")
    except ImportError as e:
        click.echo(click.style(f"ERROR: {e}", fg="red"))
        sys.exit(1)
    except ConnectionError as e:
        click.echo(click.style(f"Connection failed: {e}", fg="red"))
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command("read")
@click.argument("port", type=str)
@click.argument("output", type=click.Path())
def read_ecu(port, output):
    """Read full ECU firmware to a .bin file.

    PORT is the serial port. OUTPUT is the .bin file to write.
    Automatically validates the dump after reading.
    """
    from .ecucomm import ECUConnection

    def progress(current, total, msg):
        pct = int(100 * current / total) if total > 0 else 0
        click.echo(f"\r  [{pct:3d}%] {msg}".ljust(60), nl=False)

    click.echo(f"Connecting to {port} ...")
    ecu = ECUConnection(port)
    try:
        info = ecu.connect()
        click.echo(click.style(f"Connected: {info.software_id}", fg="green"))

        click.echo("Authenticating ...")
        ecu.login()
        click.echo(click.style("Authenticated", fg="green"))

        click.echo("Reading firmware ...")
        firmware = ecu.read_firmware(progress_callback=progress)
        click.echo()

        # Save to file
        out_path = Path(output)
        out_path.write_bytes(firmware)
        click.echo(f"Saved {len(firmware):,} bytes to {out_path}")

        # Validate
        from .binary_parser import calculate_checksum
        csum = calculate_checksum(firmware)
        click.echo(f"Cal Checksum: 0x{csum:04X}")

        # Quick validation
        dump = parse_binary(output)
        click.echo(f"Variant: {dump.identity.variant}")
        click.echo(f"Named tables: {len([r for r in dump.regions if not r.name.startswith('table_')])}")

    except (ImportError, ConnectionError) as e:
        click.echo(click.style(f"\nERROR: {e}", fg="red"))
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command()
@click.argument("port", type=str)
@click.argument("file", type=click.Path(exists=True))
@click.option("--schemas", type=click.Path(exists=True), default=None)
@click.option("--force", is_flag=True, help="Skip interactive confirmation")
def flash(port, file, schemas, force):
    """Flash a validated .bin file to the ECU.

    SAFETY: Runs ALL validation checks before flashing.
    Will REFUSE to flash if any BLOCKER is found.

    PORT is the serial port. FILE is the .bin to flash.
    """
    from .ecucomm import ECUConnection
    from .validator import validate_binary

    # Step 1: Validate BEFORE connecting
    click.echo("Step 1: Pre-flash validation ...")
    schemas_dir = _resolve_schemas(schemas)
    ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
    dump = parse_binary(file)
    results = validate_binary(dump, ranges)

    blockers = [r for r in results if r.severity == "BLOCKER"]
    warnings = [r for r in results if r.severity == "WARNING"]

    if blockers:
        click.echo(click.style(f"\n  BLOCKED: {len(blockers)} safety violation(s):", fg="red", bold=True))
        for r in blockers:
            click.echo(click.style(f"    {r.message}", fg="red"))
        click.echo(click.style("\n  FLASH REFUSED — fix the issues above first.", fg="red", bold=True))
        sys.exit(1)

    if warnings:
        click.echo(click.style(f"  {len(warnings)} warning(s):", fg="yellow"))
        for r in warnings[:5]:
            click.echo(click.style(f"    {r.message}", fg="yellow"))
        if len(warnings) > 5:
            click.echo(f"    ... and {len(warnings) - 5} more")

    click.echo(click.style("  Validation: PASSED", fg="green"))

    # Step 2: File info
    click.echo(f"\nStep 2: File info")
    click.echo(f"  File:     {file}")
    click.echo(f"  Variant:  {dump.identity.variant}")
    click.echo(f"  Software: {dump.identity.software_id}")
    click.echo(f"  Size:     {dump.file_size:,} bytes")
    click.echo(f"  Checksum: 0x{dump.cal_checksum:04X}")

    # Step 3: Confirmation
    if not force:
        click.echo(click.style(
            "\n  WARNING: Flashing incorrect firmware can DESTROY the engine.",
            fg="yellow", bold=True))
        click.echo("  Ensure battery is >12.0V and stable.")
        if not click.confirm("  Proceed with flash?"):
            click.echo("  Aborted.")
            return

    # Step 4: Flash
    def progress(current, total, msg):
        pct = int(100 * current / total) if total > 0 else 0
        click.echo(f"\r  [{pct:3d}%] {msg}".ljust(60), nl=False)

    click.echo(f"\nStep 3: Connecting to {port} ...")
    ecu = ECUConnection(port)
    try:
        ecu.connect()
        click.echo(click.style("  Connected", fg="green"))

        click.echo("  Authenticating ...")
        ecu.login()
        click.echo(click.style("  Authenticated", fg="green"))

        click.echo("  Flashing firmware (DO NOT disconnect power!) ...")
        firmware = Path(file).read_bytes()
        ecu.write_firmware(firmware, progress_callback=progress)
        click.echo()

        click.echo(click.style("\n  FLASH COMPLETE — Turn ignition OFF, wait 10 seconds, then restart.",
                               fg="green", bold=True))
    except (ImportError, ConnectionError) as e:
        click.echo(click.style(f"\n  FLASH ERROR: {e}", fg="red", bold=True))
        click.echo("  If flash was interrupted, the ECU may need recovery.")
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command()
@click.argument("port", type=str)
@click.option("--clear", is_flag=True, help="Clear all DTCs after reading")
def dtc(port, clear):
    """Read (and optionally clear) Diagnostic Trouble Codes.

    PORT is the serial port (e.g., /dev/ttyUSB0 or COM3).
    """
    from .ecucomm import ECUConnection

    ecu = ECUConnection(port)
    try:
        ecu.connect()
        click.echo(click.style("Connected", fg="green"))

        dtcs = ecu.read_dtcs()
        if not dtcs:
            click.echo(click.style("No DTCs stored", fg="green"))
        else:
            click.echo(f"Found {len(dtcs)} DTC(s):")
            for d in dtcs:
                click.echo(f"  {d}")

        if clear:
            if ecu.clear_dtcs():
                click.echo(click.style("DTCs cleared", fg="green"))
            else:
                click.echo(click.style("Failed to clear DTCs", fg="red"))

    except (ImportError, ConnectionError) as e:
        click.echo(click.style(f"ERROR: {e}", fg="red"))
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command()
@click.argument("port", type=str)
@click.option("--interval", "-i", default=1.0, help="Update interval in seconds")
def live(port, interval):
    """Stream live sensor data from ECU.

    PORT is the serial port. Press Ctrl+C to stop.
    """
    from .ecucomm import ECUConnection

    # Known PIDs for IAW 5AM (to be confirmed/expanded)
    pids = [
        (0x0C, "RPM", "rpm", 1),
        (0x11, "TPS", "%", 1),
        (0x05, "Coolant", "°C", 1),
        (0x14, "Lambda", "", 0.01),
    ]

    ecu = ECUConnection(port)
    try:
        ecu.connect()
        click.echo(click.style("Connected — streaming live data (Ctrl+C to stop)\n", fg="green"))

        # Print header
        header = " | ".join(f"{name:>10s}" for _, name, _, _ in pids)
        click.echo(f"  {header}")
        click.echo("  " + "-" * len(header))

        while True:
            values = []
            for pid, name, unit, scale in pids:
                raw = ecu.read_live_data(pid)
                if raw is not None:
                    val = raw * scale
                    values.append(f"{val:10.1f}")
                else:
                    values.append(f"{'---':>10s}")

            line = " | ".join(values)
            click.echo(f"\r  {line}", nl=False)
            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo("\n\nStopped.")
    except (ImportError, ConnectionError) as e:
        click.echo(click.style(f"ERROR: {e}", fg="red"))
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command("eeprom")
@click.argument("port", type=str)
@click.argument("output", type=click.Path())
@click.option("--write", "write_file", type=click.Path(exists=True), default=None,
              help="Write .eep file back to ECU EEPROM")
def eeprom(port, output, write_file):
    """Read or write the ECU EEPROM (2KB — CO trim, TPS, immobilizer, VIN).

    Read:  gp800-tool eeprom /dev/ttyUSB0 backup.eep
    Write: gp800-tool eeprom /dev/ttyUSB0 backup.eep --write modified.eep

    WARNING: Incorrect EEPROM writes can lock out the immobilizer.
    Always read and backup BEFORE writing.
    """
    from .ecucomm import ECUConnection

    def progress(current, total, msg):
        pct = int(100 * current / total) if total > 0 else 0
        click.echo(f"\r  [{pct:3d}%] {msg}".ljust(60), nl=False)

    ecu = ECUConnection(port)
    try:
        ecu.connect()
        click.echo(click.style("Connected", fg="green"))
        ecu.login()
        click.echo(click.style("Authenticated", fg="green"))

        if write_file:
            # Safety: always read first
            click.echo("Reading current EEPROM (backup) ...")
            current = ecu.read_eeprom(progress_callback=progress)
            click.echo()
            Path(output).write_bytes(current)
            click.echo(f"Backup saved to {output} ({len(current)} bytes)")

            # Now write
            new_data = Path(write_file).read_bytes()
            if len(new_data) != 2048:
                click.echo(click.style(f"ERROR: EEPROM file must be 2048 bytes, got {len(new_data)}", fg="red"))
                sys.exit(1)

            # Show what changed
            diffs = sum(1 for a, b in zip(current, new_data) if a != b)
            click.echo(f"Changes: {diffs} bytes differ")

            if diffs == 0:
                click.echo("No changes — skipping write.")
                return

            click.echo(click.style(
                "WARNING: EEPROM contains immobilizer data. Incorrect writes can lock you out.",
                fg="yellow", bold=True))
            if not click.confirm("Proceed with EEPROM write?"):
                click.echo("Aborted.")
                return

            click.echo("Writing EEPROM ...")
            ecu.write_eeprom(new_data, progress_callback=progress)
            click.echo()
            click.echo(click.style("EEPROM write complete", fg="green"))
        else:
            # Read only
            click.echo("Reading EEPROM ...")
            data = ecu.read_eeprom(progress_callback=progress)
            click.echo()
            Path(output).write_bytes(data)
            click.echo(f"Saved {len(data)} bytes to {output}")

            # Show useful info
            click.echo(f"  Hex dump (first 64 bytes):")
            for i in range(0, min(64, len(data)), 16):
                hex_str = " ".join(f"{b:02X}" for b in data[i:i+16])
                ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+16])
                click.echo(f"    {i:04X}: {hex_str}  {ascii_str}")

    except (ImportError, ConnectionError) as e:
        click.echo(click.style(f"\nERROR: {e}", fg="red"))
        sys.exit(1)
    finally:
        ecu.disconnect()


@main.command()
@click.argument("port", type=str)
@click.argument("output", type=click.Path())
@click.option("--duration", "-d", default=60, help="Capture duration in seconds")
def sniff(port, output, duration):
    """Capture K-Line traffic for protocol reverse-engineering.

    Run IAWDiag/JPDiag on the same serial port BEFORE starting this,
    or use a Y-splitter cable to passively monitor traffic.

    Logs all bytes with timestamps to OUTPUT file for analysis.
    """
    import time as _time

    try:
        import serial as _serial
    except ImportError:
        click.echo(click.style("ERROR: pyserial required. pip install pyserial", fg="red"))
        sys.exit(1)

    click.echo(f"Opening {port} at 10400 baud (passive monitor) ...")
    click.echo(f"Capture duration: {duration}s — press Ctrl+C to stop early")
    click.echo()

    ser = _serial.Serial(port, 10400, timeout=0.1)
    start = _time.time()
    packets = []

    try:
        while _time.time() - start < duration:
            data = ser.read(256)
            if data:
                ts = _time.time() - start
                packets.append((ts, data))
                hex_str = data.hex()
                click.echo(f"  [{ts:7.3f}s] ({len(data):3d}b) {hex_str[:80]}")
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

    # Write capture file
    with open(output, "w") as f:
        f.write("# K-Line capture\n")
        f.write(f"# Port: {port}\n")
        f.write(f"# Duration: {_time.time() - start:.1f}s\n")
        f.write(f"# Packets: {len(packets)}\n\n")
        for ts, data in packets:
            f.write(f"{ts:.6f} {data.hex()}\n")

    click.echo(f"\nCaptured {len(packets)} packets to {output}")
    click.echo("Analyze with: grep '31' capture.txt  (find RoutineControl commands)")


if __name__ == "__main__":
    main()
