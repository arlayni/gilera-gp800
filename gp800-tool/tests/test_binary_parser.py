"""Tests for binary_parser module."""
import struct
from pathlib import Path

import pytest

from gp800_tool.binary_parser import (
    IAW5AM_BIN_SIZE,
    extract_identity,
    find_idle_rpm_table,
    find_monotonic_axes,
    parse_binary,
    read_u16le,
    compare_binaries,
)


# --- helpers ---

def make_bin(size: int = IAW5AM_BIN_SIZE) -> bytearray:
    """Create a minimal IAW 5AM binary with ID block."""
    data = bytearray(size)
    # Write ID block at standard location (0x47FB8)
    hw = b"IAW5AMHW610    \x00"
    data[0x47FB8:0x47FB8 + len(hw)] = hw
    # Homologation after hardware
    hom = b"5AME0 \x00\x00"
    data[0x47FC8:0x47FC8 + len(hom)] = hom
    # Software ID (35 bytes before hardware)
    sw = b"3225AGA41  \x00"
    data[0x47FB8 - 35:0x47FB8 - 35 + len(sw)] = sw
    # Drawing number (21 bytes before hardware)
    drw = b"3584806      \x00"
    data[0x47FB8 - 21:0x47FB8 - 21 + len(drw)] = drw
    return data


def write_u16le(data: bytearray, offset: int, values: list[int]) -> None:
    for i, v in enumerate(values):
        struct.pack_into("<H", data, offset + i * 2, v)


# --- read_u16le ---

def test_read_u16le():
    data = struct.pack("<HHH", 1000, 2000, 3000)
    assert read_u16le(data, 0, 3) == [1000, 2000, 3000]


def test_read_u16le_offset():
    data = b"\x00\x00" + struct.pack("<HH", 500, 750)
    assert read_u16le(data, 2, 2) == [500, 750]


# --- extract_identity ---

def test_extract_identity():
    data = make_bin()
    ident = extract_identity(bytes(data))
    assert ident.hardware_id == "IAW5AMHW610"
    assert ident.homologation == "5AME0"
    assert ident.platform == "IAW 5AM"
    assert ident.variant == "Gilera GP800"


def test_extract_identity_srv850():
    data = make_bin()
    # Override homologation to SRV850
    hom = b"5AME2A\x00\x00"
    data[0x47FC8:0x47FC8 + len(hom)] = hom
    ident = extract_identity(bytes(data))
    assert ident.variant == "Aprilia SRV850"


def test_extract_identity_missing_marker():
    data = bytearray(IAW5AM_BIN_SIZE)
    ident = extract_identity(bytes(data))
    assert ident.hardware_id == ""
    assert ident.platform == "Unknown"


# --- find_monotonic_axes ---

def test_find_monotonic_rpm_axis():
    data = bytearray(0x50000)
    rpm = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000]
    write_u16le(data, 0x49A80, rpm)
    axes = find_monotonic_axes(bytes(data), 0x49A70, 0x49B00, min_len=8)
    assert len(axes) >= 1
    rpm_axes = [a for a in axes if a.axis_type == "RPM"]
    assert len(rpm_axes) >= 1
    assert rpm_axes[0].values == rpm


def test_find_monotonic_tps_axis():
    data = bytearray(0x50000)
    tps = [0, 10, 20, 30, 40, 50, 60, 80, 100]
    write_u16le(data, 0x4C000, tps)
    axes = find_monotonic_axes(bytes(data), 0x4BFF0, 0x4C100, min_len=6)
    tps_axes = [a for a in axes if a.axis_type == "TPS"]
    assert len(tps_axes) >= 1


# --- find_idle_rpm_table ---

def test_find_idle_rpm_table():
    data = bytearray(0x50000)
    # Write idle RPM-like data at a known offset
    offset = 0x4DE00
    for r in range(12):
        row = [700 + r * 20 + c * 5 for c in range(12)]
        write_u16le(data, offset + r * 24, row)
    idle = find_idle_rpm_table(bytes(data), start=0x4DD00, end=0x4E000)
    assert idle is not None
    assert idle.name == "idle_rpm_target"
    assert idle.rows >= 8


# --- parse_binary ---

def test_parse_binary_size_check(tmp_path):
    bin_file = tmp_path / "test.bin"
    data = make_bin()
    bin_file.write_bytes(bytes(data))
    dump = parse_binary(bin_file)
    assert dump.file_size == IAW5AM_BIN_SIZE
    assert dump.identity.platform == "IAW 5AM"
    assert dump.checksum  # non-empty


# --- compare_binaries ---

def test_compare_identical(tmp_path):
    data = make_bin()
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(bytes(data))
    f2.write_bytes(bytes(data))
    a = parse_binary(f1)
    b = parse_binary(f2)
    diffs = compare_binaries(a, b)
    assert diffs == []


def test_compare_different(tmp_path):
    data_a = make_bin()
    data_b = make_bin()
    data_b[0x49000] = 0xFF  # change one byte
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(bytes(data_a))
    f2.write_bytes(bytes(data_b))
    a = parse_binary(f1)
    b = parse_binary(f2)
    diffs = compare_binaries(a, b)
    assert len(diffs) >= 1
    byte_diff = [d for d in diffs if d["type"] == "byte_diff_summary"]
    assert byte_diff[0]["total_changed"] == 1


def test_compare_size_mismatch(tmp_path):
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(bytes(make_bin()))
    f2.write_bytes(bytes(make_bin(IAW5AM_BIN_SIZE - 100)))
    a = parse_binary(f1)
    b = parse_binary(f2)
    diffs = compare_binaries(a, b)
    assert any(d["type"] == "size_mismatch" for d in diffs)


# --- integration: real files if available ---

ORIG_BIN = Path(__file__).parent.parent.parent / "map-files" / "original" / "Gilera_GP800_original.bin"
VANDAAG_BIN = Path(__file__).parent.parent.parent / "map-files" / "working" / "vandaaggp800.bin"


@pytest.mark.skipif(not ORIG_BIN.exists(), reason="Original binary not available")
def test_parse_real_original():
    dump = parse_binary(ORIG_BIN)
    assert dump.file_size == IAW5AM_BIN_SIZE
    assert dump.identity.variant == "Gilera GP800"
    assert dump.identity.hardware_id == "IAW5AMHW610"
    assert dump.identity.homologation.startswith("5AME0")
    assert len(dump.axes) > 10
    assert len(dump.regions) >= 3  # fuel_injection, fuel_injection_rear, idle_rpm_target


@pytest.mark.skipif(not VANDAAG_BIN.exists(), reason="Vandaag binary not available")
def test_parse_real_vandaag():
    dump = parse_binary(VANDAAG_BIN)
    assert dump.file_size == IAW5AM_BIN_SIZE
    assert dump.identity.variant == "Aprilia SRV850"
    assert dump.identity.homologation.startswith("5AME2")


@pytest.mark.skipif(not (ORIG_BIN.exists() and VANDAAG_BIN.exists()),
                    reason="Binary files not available")
def test_compare_real_binaries():
    a = parse_binary(ORIG_BIN)
    b = parse_binary(VANDAAG_BIN)
    diffs = compare_binaries(a, b)
    assert len(diffs) >= 2  # byte_diff_summary + identity diffs
    byte_diff = [d for d in diffs if d["type"] == "byte_diff_summary"]
    assert byte_diff[0]["total_changed"] > 100000  # massive difference expected
