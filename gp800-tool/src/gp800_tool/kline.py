"""K-Line (ISO 9141-2 / KWP2000) communication layer for IAW 5AM ECUs.

Protocol implementation based on denandz/5am_util (GitHub/Codeberg).
Requires a USB-KKL adapter with genuine FTDI chip.

Physical layer:
- Initial baud: 10400 bps, 8N1
- Read baud: 64200 bps (after login)
- Write baud: 38400 bps (after login)
- Half-duplex single K-Line wire
"""
import struct
import time
from dataclasses import dataclass

try:
    import serial
except ImportError:
    serial = None  # Handled at connect time

# --- Constants ---
BAUD_INIT = 10400
BAUD_READ = 64200
BAUD_WRITE = 38400

ECU_ADDR = 0x10
TESTER_ADDR = 0xF1
TESTER_ADDR_AUTH = 0x01

# KWP2000 Service IDs
SVC_START_COMM = 0x81
SVC_START_DIAG = 0x10
SVC_READ_ECU_ID = 0x1A
SVC_SECURITY_ACCESS = 0x27
SVC_WRITE_DATA = 0x3B
SVC_START_ROUTINE = 0x31
SVC_STOP_ROUTINE = 0x33
SVC_REQUEST_DOWNLOAD = 0x34
SVC_TRANSFER_DATA = 0x36
SVC_READ_DTC = 0x18
SVC_CLEAR_DTC = 0x14
SVC_READ_DATA_LOCAL = 0x21


@dataclass
class KLineMessage:
    """A KWP2000 message."""
    service_id: int
    data: bytes
    source: int = TESTER_ADDR
    target: int = ECU_ADDR


def checksum8(data: bytes) -> int:
    """Calculate KWP2000 message checksum (sum mod 256)."""
    return sum(data) & 0xFF


def build_message(service_id: int, payload: bytes = b"",
                  source: int = TESTER_ADDR,
                  target: int = ECU_ADDR) -> bytes:
    """Build a KWP2000 message with header and checksum."""
    data_len = len(payload) + 1  # +1 for service ID
    header = bytes([0x80 | data_len, target, source])
    body = header + bytes([service_id]) + payload
    return body + bytes([checksum8(body)])


def build_raw_message(raw_bytes: list[int]) -> bytes:
    """Build a message from pre-computed bytes, adding checksum."""
    msg = bytes(raw_bytes)
    return msg + bytes([checksum8(msg)])


def parse_response(data: bytes) -> tuple[int, bytes] | None:
    """Parse a KWP2000 response. Returns (service_id, payload) or None."""
    if len(data) < 4:
        return None
    # Verify checksum
    if checksum8(data[:-1]) != data[-1]:
        return None
    # Extract service ID (positive response = request + 0x40)
    header_len = data[0] & 0x3F
    service_id = data[3]
    payload = data[4:-1]
    return service_id, payload


# --- Seed-Key Authentication ---

def calc_security_key(challenge: int) -> int:
    """Calculate the seed-key response for IAW 5AM SecurityAccess.

    Source: denandz/5am_util calc_key()
    """
    data = struct.pack('<I', challenge)
    a = struct.unpack('<H', data[0:2])[0]
    w = ((a >> 8) | ((a & 0xFF) << 8)) & 0xFFFF
    b1 = (w // 0xA1) & 0xFF
    b2 = (struct.unpack('<H', data[2:4])[0] % 0xC8) & 0xFF
    return (b1 << 24) | (b2 << 16) | (0x69 << 8) | 0x27


# --- Firmware Encryption/Decryption ---

def _ror8(val: int, n: int) -> int:
    """Rotate right 8-bit value by n bits."""
    val &= 0xFF
    return ((val >> n) | (val << (8 - n))) & 0xFF


def _rol8(val: int, n: int) -> int:
    """Rotate left 8-bit value by n bits."""
    val &= 0xFF
    return ((val << n) | (val >> (8 - n))) & 0xFF


def encrypt_byte(b: int, pos: int) -> int:
    """Encrypt a single byte at position pos (mod 8) for firmware upload."""
    b &= 0xFF
    ops = [
        lambda x: (~_ror8((x + 0x88) & 0xFF, 1)) & 0xFF,
        lambda x: _ror8((x + 0xC7) & 0xFF, 1),
        lambda x: (~_ror8((x + 0x26) & 0xFF, 3)) & 0xFF,
        lambda x: (~_ror8((x + 0xA5) & 0xFF, 5)) & 0xFF,
        lambda x: _ror8((x + 0x6C) & 0xFF, 2),
        lambda x: _ror8((x + 0xEB) & 0xFF, 6),
        lambda x: (~_ror8((x + 0x0A) & 0xFF, 6)) & 0xFF,
        lambda x: _ror8((0x66 + ((~x + 1) & 0xFF)) & 0xFF, 4),
    ]
    return ops[pos % 8](b)


def decrypt_byte(b: int, pos: int) -> int:
    """Decrypt a single byte at position pos (mod 8) from firmware download."""
    b &= 0xFF
    ops = [
        lambda x: ((~_rol8(x, 1)) & 0xFF - 0x88) & 0xFF,
        lambda x: (_rol8(x, 1) - 0xC7) & 0xFF,
        lambda x: ((~_rol8(x, 3)) & 0xFF - 0x26) & 0xFF,
        lambda x: ((~_rol8(x, 5)) & 0xFF - 0xA5) & 0xFF,
        lambda x: (_rol8(x, 2) - 0x6C) & 0xFF,
        lambda x: (_rol8(x, 6) - 0xEB) & 0xFF,
        lambda x: ((~_rol8(x, 6)) & 0xFF - 0x0A) & 0xFF,
        lambda x: ((0x66 - _rol8(x, 4)) & 0xFF ^ 0xFF) + 1 & 0xFF,
    ]
    return ops[pos % 8](b)


def encrypt_firmware(data: bytes) -> bytes:
    """Encrypt firmware data for upload to ECU."""
    return bytes(encrypt_byte(b, i) for i, b in enumerate(data))


def decrypt_firmware(data: bytes) -> bytes:
    """Decrypt firmware data received from ECU."""
    return bytes(decrypt_byte(b, i) for i, b in enumerate(data))


# --- Serial Connection ---

class KLineConnection:
    """Manages serial K-Line connection to IAW 5AM ECU."""

    def __init__(self, port: str, timeout: float = 0.5):
        if serial is None:
            raise ImportError(
                "pyserial is required for K-Line communication. "
                "Install with: pip install pyserial"
            )
        self.port = port
        self.timeout = timeout
        self._serial: serial.Serial | None = None

    def open(self, baudrate: int = BAUD_INIT) -> None:
        """Open serial connection."""
        self._serial = serial.Serial(
            port=self.port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )
        self._serial.reset_input_buffer()

    def close(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._serial = None

    def set_baudrate(self, baudrate: int) -> None:
        """Change baud rate on active connection."""
        if self._serial:
            self._serial.baudrate = baudrate
            self._serial.reset_input_buffer()
            time.sleep(0.1)

    def fast_init(self) -> None:
        """Perform ISO 14230 fast init (26ms break + 25ms idle)."""
        if not self._serial:
            raise ConnectionError("Serial port not open")
        self._serial.break_condition = True
        time.sleep(0.026)
        self._serial.break_condition = False
        time.sleep(0.025)

    def send(self, data: bytes) -> None:
        """Send raw bytes over K-Line."""
        if not self._serial:
            raise ConnectionError("Serial port not open")
        self._serial.write(data)
        self._serial.flush()
        # Read back echo (K-Line is half-duplex)
        self._serial.read(len(data))

    def receive(self, timeout: float | None = None) -> bytes:
        """Receive a KWP2000 response message."""
        if not self._serial:
            raise ConnectionError("Serial port not open")

        old_timeout = self._serial.timeout
        if timeout is not None:
            self._serial.timeout = timeout

        try:
            # Read header byte
            header = self._serial.read(1)
            if not header:
                return b""

            # Determine message length from header
            msg_len = header[0] & 0x3F
            # Read remaining: target + source + data + checksum
            remaining = self._serial.read(msg_len + 2)  # +2 for addr bytes, checksum included
            return header + remaining
        finally:
            self._serial.timeout = old_timeout

    def send_and_receive(self, msg: bytes, timeout: float | None = None) -> bytes:
        """Send a message and wait for response."""
        self.send(msg)
        time.sleep(0.05)  # Inter-message delay
        return self.receive(timeout)

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open
