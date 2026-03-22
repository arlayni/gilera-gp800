"""Parse IAW 5AM binary (.bin) ECU dump files.

Reverse-engineered from comparing GP800 original (5AME0) and SRV850 (5AME2A)
binaries. The IAW 5AM stores calibration data as 16-bit little-endian values
in the upper portion of a 327,680-byte (320KB) flash image.
"""
import hashlib
import struct
from dataclasses import dataclass, field
from pathlib import Path

IAW5AM_BIN_SIZE = 327680  # 320KB standard flash size


@dataclass
class ECUIdentity:
    """ECU identification block extracted from binary."""
    software_id: str = ""
    drawing_number: str = ""
    hardware_id: str = ""
    homologation: str = ""
    raw_offset: int = 0

    @property
    def platform(self) -> str:
        if "5AM" in self.hardware_id:
            return "IAW 5AM"
        return "Unknown"

    @property
    def variant(self) -> str:
        """Identify which vehicle this calibration is for."""
        if self.homologation.startswith("5AME0"):
            return "Gilera GP800"
        if self.homologation.startswith("5AME2"):
            return "Aprilia SRV850"
        if self.homologation.startswith("5AME1"):
            return "Aprilia Mana 850"
        return f"Unknown ({self.homologation})"


@dataclass
class AxisBreakpoints:
    """A detected axis breakpoint array in the binary."""
    offset: int
    values: list[int]
    axis_type: str = ""  # "RPM", "TPS", "ECT", "voltage", "generic"

    @property
    def count(self) -> int:
        return len(self.values)

    @property
    def size_bytes(self) -> int:
        return self.count * 2


@dataclass
class BinaryRegion:
    """A labeled region of the binary with extracted 16-bit values."""
    offset: int
    name: str
    rows: int
    cols: int
    values: list[list[int]]
    x_axis: AxisBreakpoints | None = None
    y_axis: AxisBreakpoints | None = None
    value_type: str = ""  # "fuel_us", "degrees", "rpm", "lambda_x1000", etc.

    @property
    def size_bytes(self) -> int:
        return self.rows * self.cols * 2

    def flat_values(self) -> list[int]:
        return [v for row in self.values for v in row]


@dataclass
class BinaryDump:
    """Complete analysis of an IAW 5AM binary file."""
    source_path: str
    file_size: int
    checksum: str
    identity: ECUIdentity
    axes: list[AxisBreakpoints] = field(default_factory=list)
    regions: list[BinaryRegion] = field(default_factory=list)
    raw: bytes = field(default=b"", repr=False)


def read_u16le(data: bytes, offset: int, count: int) -> list[int]:
    """Read count 16-bit unsigned little-endian values from data."""
    return [struct.unpack_from("<H", data, offset + i * 2)[0]
            for i in range(count)]


def read_ascii(data: bytes, offset: int, length: int) -> str:
    """Read ASCII string, stripping nulls and non-printable chars."""
    raw = data[offset:offset + length]
    return "".join(chr(b) if 32 <= b < 127 else "" for b in raw).strip()


def extract_identity(data: bytes) -> ECUIdentity:
    """Extract ECU identification from the ID block (near 0x47F95)."""
    # The ID block is at a fixed location in IAW 5AM binaries
    # Search for "IAW5AM" marker to locate it
    marker = b"IAW5AM"
    idx = data.find(marker)
    if idx < 0:
        return ECUIdentity()

    # Hardware ID is at the marker itself (16 bytes padded with spaces)
    hw_id = read_ascii(data, idx, 16)

    # Homologation follows hardware (next 8 bytes)
    homolog = read_ascii(data, idx + 16, 8)

    # Software ID is 35 bytes before hardware
    sw_id = read_ascii(data, idx - 35, 12)

    # Drawing number is 21 bytes before hardware
    drawing = read_ascii(data, idx - 21, 14)

    return ECUIdentity(
        software_id=sw_id,
        drawing_number=drawing,
        hardware_id=hw_id,
        homologation=homolog,
        raw_offset=idx,
    )


def find_monotonic_axes(data: bytes, start: int, end: int,
                        min_len: int = 8) -> list[AxisBreakpoints]:
    """Find monotonically increasing sequences of 16-bit LE values.

    Returns de-duplicated axes (only the longest starting at each offset).
    """
    axes: list[AxisBreakpoints] = []
    skip_until = 0

    for offset in range(start, end - min_len * 2, 2):
        if offset < skip_until:
            continue

        max_count = min(32, (end - offset) // 2)
        if max_count < min_len:
            break

        vals = read_u16le(data, offset, max_count)
        mono_len = 1
        for i in range(len(vals) - 1):
            if vals[i] < vals[i + 1]:
                mono_len += 1
            else:
                break

        if mono_len < min_len:
            continue

        seq = vals[:mono_len]

        # Classify axis type
        axis_type = _classify_axis(seq)
        if not axis_type:
            continue

        axes.append(AxisBreakpoints(
            offset=offset,
            values=seq,
            axis_type=axis_type,
        ))
        skip_until = offset + mono_len * 2

    return axes


def _classify_axis(values: list[int]) -> str:
    """Classify an axis based on its value range and pattern."""
    lo, hi = values[0], values[-1]

    # RPM: 500-10000, typical breakpoints
    if 400 <= lo <= 1500 and 3000 <= hi <= 10000:
        return "RPM"

    # TPS/load: 0-100 or 0-200 (percentage, sometimes x10)
    if lo == 0 and 50 <= hi <= 200:
        return "TPS"

    # Temperature: -50 to +120 (signed)
    if lo == 0 and 80 <= hi <= 130:
        return "ECT"

    # Voltage: common for injector dead-time (80-160 = 8.0-16.0V x10)
    if 60 <= lo <= 100 and 140 <= hi <= 180:
        return "voltage"

    return ""


def find_tables_near_axes(data: bytes, axes: list[AxisBreakpoints],
                          search_range: int = 2048) -> list[BinaryRegion]:
    """For each RPM axis, look for table data nearby.

    IAW 5AM stores tables as rows × cols of 16-bit LE values,
    with the axis breakpoints stored separately (often before the data).
    """
    regions: list[BinaryRegion] = []
    seen_offsets: set[int] = set()

    rpm_axes = [a for a in axes if a.axis_type == "RPM"]
    tps_axes = [a for a in axes if a.axis_type == "TPS"]

    for rpm_ax in rpm_axes:
        ncols = rpm_ax.count
        # Look for table data after the axis
        for probe_offset in range(rpm_ax.offset + rpm_ax.size_bytes,
                                  rpm_ax.offset + rpm_ax.size_bytes + search_range,
                                  2):
            if probe_offset in seen_offsets or probe_offset + ncols * 2 > len(data):
                continue

            # Try reading rows until we hit a non-table pattern
            rows_data: list[list[int]] = []
            for r in range(32):  # max 32 rows
                row_offset = probe_offset + r * ncols * 2
                if row_offset + ncols * 2 > len(data):
                    break
                row = read_u16le(data, row_offset, ncols)

                # Stop if row looks like an axis or marker
                if all(row[i] < row[i + 1] for i in range(len(row) - 1)):
                    if _classify_axis(row):
                        break

                # Stop if all zeros (padding)
                if all(v == 0 for v in row) and r > 0:
                    break

                rows_data.append(row)

            if len(rows_data) >= 4:
                region = BinaryRegion(
                    offset=probe_offset,
                    name=f"table_{rpm_ax.offset:05X}_{probe_offset:05X}",
                    rows=len(rows_data),
                    cols=ncols,
                    values=rows_data,
                    x_axis=rpm_ax,
                )
                regions.append(region)
                for r in range(len(rows_data)):
                    for c in range(ncols):
                        seen_offsets.add(probe_offset + r * ncols * 2 + c * 2)
                break  # found the table for this axis

    return regions


def find_idle_rpm_table(data: bytes, start: int = 0x4DE00,
                        end: int = 0x4E100) -> BinaryRegion | None:
    """Find the idle RPM target table.

    This table is distinctive: rows of values in the 700-1100 RPM range,
    where each row represents a different temperature/condition.
    """
    for offset in range(start, end, 2):
        # Try 12 columns (common for temperature-indexed tables)
        for ncols in [10, 11, 12, 14, 16]:
            rows_data: list[list[int]] = []
            for r in range(32):
                row_offset = offset + r * ncols * 2
                if row_offset + ncols * 2 > len(data):
                    break
                row = read_u16le(data, row_offset, ncols)
                # Idle RPM values should be 600-1500
                if all(500 <= v <= 1500 for v in row):
                    rows_data.append(row)
                else:
                    break

            if len(rows_data) >= 8:
                return BinaryRegion(
                    offset=offset,
                    name="idle_rpm_target",
                    rows=len(rows_data),
                    cols=ncols,
                    values=rows_data,
                    value_type="rpm",
                )
    return None


def scan_calibration_area(data: bytes) -> tuple[list[AxisBreakpoints], list[BinaryRegion]]:
    """Scan the calibration area (upper portion) for tables and axes."""
    # Calibration data lives roughly in 0x48000-0x50000
    cal_start = 0x48000
    cal_end = min(0x50000, len(data))

    axes = find_monotonic_axes(data, cal_start, cal_end, min_len=8)
    tables = find_tables_near_axes(data, axes)

    # Find idle RPM table
    idle = find_idle_rpm_table(data)
    if idle:
        tables.append(idle)

    return axes, tables


def parse_binary(path: Path | str) -> BinaryDump:
    """Parse an IAW 5AM binary (.bin) file.

    Returns structured analysis including ECU identity, axis breakpoints,
    and detected calibration tables.
    """
    path = Path(path)
    raw = path.read_bytes()

    checksum = hashlib.sha256(raw).hexdigest()
    identity = extract_identity(raw)
    axes, tables = scan_calibration_area(raw)

    return BinaryDump(
        source_path=str(path),
        file_size=len(raw),
        checksum=checksum,
        identity=identity,
        axes=axes,
        regions=tables,
        raw=raw,
    )


def compare_binaries(a: BinaryDump, b: BinaryDump) -> list[dict]:
    """Compare two binary dumps and report differences in calibration regions."""
    diffs: list[dict] = []

    if len(a.raw) != len(b.raw):
        diffs.append({
            "type": "size_mismatch",
            "a_size": len(a.raw),
            "b_size": len(b.raw),
        })
        return diffs

    # Byte-level diff with region clustering
    changed_bytes = [(i, a.raw[i], b.raw[i])
                     for i in range(len(a.raw))
                     if a.raw[i] != b.raw[i]]

    if not changed_bytes:
        return diffs

    # Cluster into regions
    regions: list[tuple[int, int, int]] = []  # (start, end, count)
    start = changed_bytes[0][0]
    end = start
    count = 1
    for offset, _, _ in changed_bytes[1:]:
        if offset - end <= 32:
            end = offset
            count += 1
        else:
            regions.append((start, end, count))
            start = offset
            end = offset
            count = 1
    regions.append((start, end, count))

    diffs.append({
        "type": "byte_diff_summary",
        "total_changed": len(changed_bytes),
        "region_count": len(regions),
        "regions": [(s, e, c) for s, e, c in regions],
    })

    # Compare identity
    if a.identity.software_id != b.identity.software_id:
        diffs.append({
            "type": "identity_diff",
            "field": "software_id",
            "a": a.identity.software_id,
            "b": b.identity.software_id,
        })
    if a.identity.homologation != b.identity.homologation:
        diffs.append({
            "type": "identity_diff",
            "field": "homologation",
            "a": a.identity.homologation,
            "b": b.identity.homologation,
        })

    return diffs
