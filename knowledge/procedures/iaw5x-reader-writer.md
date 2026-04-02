# IAW5xReader / IAW5xWriter — Tool Usage Guide

## Overview

The owner has IAW5xReader/Writer hardware and software. This is the primary tool for:
- Reading current ECU maps
- Writing (flashing) new maps
- Reading diagnostic trouble codes (DTCs)
- Monitoring live sensor data

**The IAW 5AM uses K-Line ISO 9141-2 at 10,400 baud. This is NOT a standard OBD2 connection.** Standard OBD2 scanners will not work.

---

## Available Tools

| Tool | Source | Cost | Capabilities |
|------|--------|------|-------------|
| **IAWDiag suite** (IAW5xReader/Writer/EEPROM) | von-der-salierburg.de | Gratis | Read/write ECU binary, EEPROM, DTCs |
| **5am_util** | github.com/denandz/5am_util | Gratis | Low-level IAW5AM read/write |
| **GuzziDiag** | von-der-salierburg.de | Gratis | DTCs, beperkte live data |
| **PADS** (Piaggio Advanced Diagnostic System) | Dealer portal | Dealer-only | Alles + TPS cal, immobilizer, CO adjust |
| **OBDSTAR iScan Piaggio** | Commercieel | ~€300-500 | Dealer-level incl. key programming |

## Hardware Setup

| Component | Notes |
|-----------|-------|
| USB-KKL adapter | **Moet FTDI chip hebben** — klonen zijn onbetrouwbaar |
| 3-pin adapter kabel | Proprietary Piaggio/Aprilia connector (NIET standaard OBD2) |
| Power | Bike must have ignition ON, engine OFF for most operations |
| Battery | Must be >12.0V for flash operations |

**Connection procedure:**
1. Verify battery >12.0V
2. Connect IAW5x adapter to bike's diagnostic connector
3. Connect USB to computer
4. Open IAW5xReader or IAW5xWriter software
5. Select correct COM port
6. Turn ignition ON (engine OFF)
7. Attempt connection

---

## IAW5xReader — Reading ECU Data

### Reading Current Maps

1. Connect and establish communication
2. Select "Read ECU" or equivalent option
3. Allow full read to complete (K-Line at 10.4 kbaud — this takes several minutes)
4. Save the file with a timestamp: `gp800-ecu-YYYY-MM-DD-HHmm.bin` (or .txt as software uses)
5. Compute SHA256 hash of saved file and record it

**File types:**
- `.txt` files — IAW5xWriter folder format (map tables in text format)
- `.bin` files — binary dump
- There is currently 1 .txt file in the Reader folder; files exist in the Writer folder

**CRITICAL:** The file saved after reading is your backup. Verify it saved completely before proceeding.

### Reading DTCs

1. Connect as above
2. Select "Diagnostics" or "Read Fault Codes"
3. Record ALL active codes before clearing any
4. Cross-reference with [error-codes.md](../reference/error-codes.md)

### Reading Live Data

1. Connect as above
2. Select "Live Data" or "Data Stream"
3. Key channels to monitor:
   - RPM
   - TPS voltage
   - MAP voltage
   - ECT temperature
   - IAT temperature
   - Lambda voltage
   - Battery voltage
   - Injection time (ms)
   - Ignition advance (deg)

---

## IAW5xWriter — Writing Maps

### Pre-Write Checklist

Before writing any map, verify:

- [ ] Verified backup exists with known SHA256 hash (from this session)
- [ ] Battery voltage >12.0V
- [ ] New map has passed 5-stage validation pipeline (see [tuning-workflow.md](tuning-workflow.md))
- [ ] No active hard-limit violations in new map
- [ ] Second person present for first start after flash
- [ ] Fire extinguisher accessible

### Write Procedure

1. Complete pre-write checklist above
2. Connect IAW5x adapter
3. Open IAW5xWriter
4. Load map file to be flashed
5. Verify map file loads correctly (correct structure, expected size)
6. Select "Write ECU" or equivalent
7. Do NOT disconnect or lose power during write (K-Line write = several minutes)
8. After write completes: read back ECU and compare to written file
9. Verify read-back matches what was written (SHA256 comparison if supported)

### Post-Write Verification

See [tuning-workflow.md](tuning-workflow.md) for the full post-flash human checklist.

Summary:
1. Ignition ON, engine OFF — check dashboard, check for new DTCs
2. Start engine — verify idle within 1100–1400 RPM within 10 seconds
3. 30-second observation — no red exhaust, no flames, no pinging

---

## Map File Format

TODO: Document the exact map file structure used by IAW5xReader/Writer:
- File extension (.txt vs .bin)
- Map table names as they appear in the software
- Cell value format (raw 0–255 or scaled engineering units)
- Axis values (RPM and load breakpoints)
- Checksum location and algorithm
- Expected binary size for IAW 5AM

---

## Exporting Map Tables

TODO: Document how to export individual map tables to CSV or text for analysis:
- Which menu option
- Which file format is most useful for analysis
- How to import back after editing

---

## Common Connection Problems

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Software cannot find COM port | Driver not installed | Install USB adapter drivers |
| "No ECU response" | Battery low, bad connection, wrong COM port | Check battery, cable, port selection |
| Connection timeout | K-Line speed mismatch | Verify baud rate set to 10400 |
| Read stops partway | Poor connection / interference | Check cable, retry |
| Write fails midway | STOP — read ECU immediately to check state | Re-attempt write with better connection |

---

## Safety During Flash

- Never disconnect power during a write operation
- If power is lost mid-write: ECU may be in indeterminate state — see [bricked-ecu-recovery.md](bricked-ecu-recovery.md)
- Keep laptop on mains power (not battery) during flash operations
- Do not use the same USB port as other devices during flash

---

## Related Files

- [ecu-iaw5am.md](../reference/ecu-iaw5am.md) — ECU architecture and K-Line protocol
- [obd-diagnostics.md](obd-diagnostics.md) — diagnostic protocol context
- [tuning-workflow.md](tuning-workflow.md) — map editing and flash safety sequence
- [bricked-ecu-recovery.md](bricked-ecu-recovery.md) — if connection or flash fails

---

*TODO: Document exact software version, file format details, export procedure, and diagnostic connector location from hands-on session with the tool.*
