"""High-level ECU communication for IAW 5AM.

Provides connect, identify, read firmware, write firmware, DTC operations.
Built on top of the kline.py transport layer.
"""
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path

from .kline import (
    KLineConnection, BAUD_INIT, BAUD_READ, BAUD_WRITE,
    ECU_ADDR, TESTER_ADDR, TESTER_ADDR_AUTH,
    build_message, build_raw_message, parse_response,
    calc_security_key, encrypt_firmware, decrypt_firmware,
    checksum8,
)
from .binary_parser import IAW5AM_BIN_SIZE, calculate_checksum


@dataclass
class ECUInfo:
    """Information read from ECU identification."""
    software_id: str = ""
    hardware_id: str = ""
    homologation: str = ""
    drawing: str = ""
    raw_data: bytes = b""


@dataclass
class DTC:
    """Diagnostic Trouble Code."""
    code: int
    status: int

    @property
    def code_hex(self) -> str:
        return f"0x{self.code:04X}"

    def __str__(self) -> str:
        return f"DTC {self.code_hex} (status: 0x{self.status:02X})"


class ECUConnection:
    """High-level IAW 5AM ECU communication."""

    def __init__(self, port: str):
        self.port = port
        self.kline = KLineConnection(port)
        self.connected = False
        self.authenticated = False
        self.ecu_info: ECUInfo | None = None

    def connect(self) -> ECUInfo:
        """Connect to ECU: fast init → start communication → start diagnostic session → identify."""
        self.kline.open(BAUD_INIT)

        # Fast init
        self.kline.fast_init()
        time.sleep(0.05)

        # StartCommunication
        msg = build_raw_message([0x81, ECU_ADDR, TESTER_ADDR, 0x81])
        resp = self.kline.send_and_receive(msg, timeout=2.0)
        if not resp:
            raise ConnectionError("No response from ECU — check wiring and ignition")

        parsed = parse_response(resp)
        if parsed is None:
            raise ConnectionError(f"Invalid response: {resp.hex()}")

        # StartDiagnosticSession
        msg = build_raw_message([0x82, ECU_ADDR, TESTER_ADDR, 0x10, 0x85])
        resp = self.kline.send_and_receive(msg)

        # ReadECUIdentification
        msg = build_raw_message([0x82, ECU_ADDR, TESTER_ADDR, 0x1A, 0x80])
        resp = self.kline.send_and_receive(msg, timeout=2.0)

        self.ecu_info = self._parse_ecu_info(resp)
        self.connected = True
        return self.ecu_info

    def _parse_ecu_info(self, resp: bytes) -> ECUInfo:
        """Parse ReadECUIdentification response."""
        parsed = parse_response(resp)
        if parsed is None:
            return ECUInfo()

        _, payload = parsed
        # Extract text fields from response payload
        raw_text = payload.decode('ascii', errors='replace')
        return ECUInfo(
            raw_data=payload,
            software_id=raw_text[:12].strip() if len(raw_text) >= 12 else "",
            hardware_id="",
            homologation="",
        )

    def login(self) -> bool:
        """Perform SecurityAccess authentication (seed-key)."""
        # Request seed
        msg = build_raw_message([0x82, ECU_ADDR, TESTER_ADDR_AUTH, 0x27, 0x01])
        resp = self.kline.send_and_receive(msg, timeout=2.0)

        parsed = parse_response(resp)
        if parsed is None:
            raise ConnectionError("Security access seed request failed")

        svc_id, payload = parsed
        if svc_id != 0x67 or len(payload) < 5:
            raise ConnectionError(f"Unexpected seed response: 0x{svc_id:02X}")

        # Extract 4-byte seed (skip subfunction byte)
        seed = struct.unpack('<I', payload[1:5])[0]

        # Wait for ECU to be ready
        time.sleep(1.0)

        # Calculate and send key
        key = calc_security_key(seed)
        key_bytes = struct.pack('>I', key)  # big-endian for transmission

        msg = build_raw_message([
            0x86, ECU_ADDR, TESTER_ADDR_AUTH, 0x27, 0x02,
            key_bytes[0], key_bytes[1], key_bytes[2], key_bytes[3]
        ])
        resp = self.kline.send_and_receive(msg, timeout=2.0)

        parsed = parse_response(resp)
        if parsed is None:
            raise ConnectionError("Security access key response failed")

        svc_id, _ = parsed
        if svc_id == 0x67:
            self.authenticated = True
            return True
        return False

    def read_firmware(self, progress_callback=None) -> bytes:
        """Read full 320KB firmware from ECU.

        Returns decrypted firmware bytes.
        Requires: connected + authenticated.
        """
        if not self.connected:
            raise ConnectionError("Not connected to ECU")
        if not self.authenticated:
            self.login()

        # Switch to read baud rate
        self.kline.set_baudrate(BAUD_READ)
        time.sleep(0.1)

        # Read 20 blocks (0x00, 0x01, 0x06-0x12)
        blocks = [0x00, 0x01] + list(range(0x06, 0x13))
        firmware = bytearray(IAW5AM_BIN_SIZE)
        block_size = 0x4000  # 16KB per block

        for block_idx, block_num in enumerate(blocks):
            if progress_callback:
                progress_callback(block_idx, len(blocks), f"Block 0x{block_num:02X}")

            # Request block
            msg = build_raw_message([
                0x87, ECU_ADDR, TESTER_ADDR_AUTH,
                0x36, 0x11, 0x00, 0xFE, 0x02, 0x01, block_num
            ])
            self.kline.send(msg)

            # Read sub-chunks (32 bytes each)
            block_data = bytearray()
            while len(block_data) < block_size:
                resp = self.kline.receive(timeout=2.0)
                if not resp:
                    raise ConnectionError(f"Timeout reading block 0x{block_num:02X}")
                parsed = parse_response(resp)
                if parsed is None:
                    continue
                _, chunk = parsed
                block_data.extend(chunk)

            # Decrypt and place in firmware
            decrypted = decrypt_firmware(bytes(block_data[:block_size]))
            offset = block_idx * block_size
            firmware[offset:offset + block_size] = decrypted

        # Fill blocks 0x02-0x05 with 0xFF (not readable, always 0xFF)
        for skip_block in range(2, 6):
            offset = skip_block * block_size
            firmware[offset:offset + block_size] = b'\xFF' * block_size

        if progress_callback:
            progress_callback(len(blocks), len(blocks), "Complete")

        return bytes(firmware)

    def write_firmware(self, firmware: bytes, progress_callback=None) -> bool:
        """Write 320KB firmware to ECU.

        SAFETY: The caller MUST validate the firmware before calling this.
        Requires: connected + authenticated.
        """
        if len(firmware) != IAW5AM_BIN_SIZE:
            raise ValueError(f"Firmware must be {IAW5AM_BIN_SIZE} bytes, got {len(firmware)}")

        if not self.connected:
            raise ConnectionError("Not connected to ECU")
        if not self.authenticated:
            self.login()

        # Switch to write baud rate
        self.kline.set_baudrate(BAUD_WRITE)
        time.sleep(0.1)

        # Set writer metadata
        msg = build_raw_message([0x83, ECU_ADDR, TESTER_ADDR, 0x3B, 0x98, 0x20])
        self.kline.send_and_receive(msg)

        # Set write date
        msg = build_raw_message([0x86, ECU_ADDR, TESTER_ADDR, 0x3B, 0x99, 0x20, 0x18, 0x01, 0x01])
        self.kline.send_and_receive(msg)

        if progress_callback:
            progress_callback(0, 100, "Erasing flash...")

        # Erase flash (0x40000-0x4FFFF) — takes ~10 seconds
        msg = build_raw_message([
            0x88, ECU_ADDR, TESTER_ADDR,
            0x31, 0x02, 0x00, 0x40, 0x00, 0x04, 0xFF, 0xFF
        ])
        self.kline.send_and_receive(msg, timeout=15.0)

        # Stop erase routine
        msg = build_raw_message([0x82, ECU_ADDR, TESTER_ADDR, 0x33, 0x02])
        self.kline.send_and_receive(msg, timeout=5.0)

        if progress_callback:
            progress_callback(10, 100, "Requesting download...")

        # Request download
        msg = build_raw_message([
            0x88, ECU_ADDR, TESTER_ADDR,
            0x34, 0x00, 0x40, 0x00, 0x33, 0x04, 0xC0, 0x00
        ])
        self.kline.send_and_receive(msg, timeout=5.0)

        # Transfer firmware in 254-byte chunks
        cal_data = firmware[0x4000:0x50000]  # Calibration area only
        encrypted = encrypt_firmware(cal_data)
        chunk_size = 254
        total_chunks = (len(encrypted) + chunk_size - 1) // chunk_size

        for i in range(0, len(encrypted), chunk_size):
            chunk = encrypted[i:i + chunk_size]
            chunk_num = i // chunk_size

            if progress_callback:
                pct = 10 + int(90 * chunk_num / total_chunks)
                progress_callback(pct, 100, f"Chunk {chunk_num}/{total_chunks}")

            # Build transfer data message
            msg_len = len(chunk) + 1  # +1 for service ID
            header = bytes([0x80 | 0x00, ECU_ADDR, TESTER_ADDR, msg_len])
            body = header + bytes([0x36]) + chunk
            msg = body + bytes([checksum8(body)])
            self.kline.send_and_receive(msg, timeout=2.0)

        if progress_callback:
            progress_callback(100, 100, "Flash complete")

        return True

    def read_dtcs(self) -> list[DTC]:
        """Read Diagnostic Trouble Codes from ECU."""
        if not self.connected:
            raise ConnectionError("Not connected to ECU")

        # ReadDTCByStatus — request all stored DTCs
        msg = build_message(0x18, bytes([0x00, 0xFF, 0x00]), source=TESTER_ADDR)
        resp = self.kline.send_and_receive(msg, timeout=2.0)

        parsed = parse_response(resp)
        if parsed is None:
            return []

        svc_id, payload = parsed
        if svc_id != 0x58:  # Positive response to ReadDTC
            return []

        # Parse DTCs: each DTC is 3 bytes (2 bytes code + 1 byte status)
        dtcs = []
        # Skip first byte (number of DTCs)
        for i in range(1, len(payload) - 2, 3):
            code = struct.unpack('>H', payload[i:i + 2])[0]
            status = payload[i + 2]
            if code != 0:
                dtcs.append(DTC(code=code, status=status))

        return dtcs

    def clear_dtcs(self) -> bool:
        """Clear all Diagnostic Trouble Codes."""
        if not self.connected:
            raise ConnectionError("Not connected to ECU")

        msg = build_message(0x14, bytes([0xFF, 0x00]), source=TESTER_ADDR)
        resp = self.kline.send_and_receive(msg, timeout=2.0)

        parsed = parse_response(resp)
        if parsed is None:
            return False
        svc_id, _ = parsed
        return svc_id == 0x54  # Positive response to ClearDTC

    def read_live_data(self, pid: int) -> int | None:
        """Read a single live data parameter by local ID.

        Common PIDs (to be confirmed on IAW 5AM):
        - 0x05: Coolant temp
        - 0x0C: Engine RPM
        - 0x0D: Vehicle speed
        - 0x11: TPS
        - 0x14: Lambda
        """
        if not self.connected:
            raise ConnectionError("Not connected to ECU")

        msg = build_message(0x21, bytes([pid]), source=TESTER_ADDR)
        resp = self.kline.send_and_receive(msg, timeout=1.0)

        parsed = parse_response(resp)
        if parsed is None:
            return None
        svc_id, payload = parsed
        if svc_id != 0x61:
            return None
        if len(payload) >= 2:
            return struct.unpack('>H', payload[:2])[0]
        if len(payload) == 1:
            return payload[0]
        return None

    def disconnect(self) -> None:
        """Disconnect from ECU."""
        self.kline.close()
        self.connected = False
        self.authenticated = False
