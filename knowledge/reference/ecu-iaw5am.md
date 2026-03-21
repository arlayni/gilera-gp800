# ECU Reference — Magneti Marelli IAW 5AM

## Overview

The IAW 5AM (Integrated Acquisition and Actuation, 5th generation, Aprilia Moto) is the engine management ECU used on the Gilera GP800 and Aprilia SRV850. This bike currently has an **SRV850 ECU fitted in place of the original GP800 ECU**.

**This is NOT an OBD2 ECU.** It uses the Piaggio-proprietary K-Line ISO 9141-2 protocol.

---

## Communication Protocol

| Parameter | Value |
|-----------|-------|
| Protocol | K-Line ISO 9141-2 |
| Baud rate | 10,400 baud (10.4 kbaud) |
| Standard | NOT OBD2 / SAE J1979 |
| Interface hardware | IAW5xReader/Writer (owner has this) |
| Flash time (full reflash) | Several minutes (not seconds) |
| Automated rollback | NOT POSSIBLE — all rollback is human-executed |

See [obd-diagnostics.md](../procedures/obd-diagnostics.md) for compatible diagnostic tools.

---

## ECU Variants on This Platform

| Variant | Notes |
|---------|-------|
| GP800 OEM | Original fit; failed (side-stand switch signal fault) |
| SRV850 | Currently installed; same IAW 5AM platform, electrically compatible; adds ABS module integration |

See [platform-differences.md](platform-differences.md) for full GP800 vs SRV850 comparison.

---

## Memory Layout

TODO: Document from IAW5xReader output:
- Map table start addresses
- Calibration table start addresses
- Immobilizer region (do not modify)
- Checksum region

---

## Key Map Tables

Defined in [map-definitions.json](../schemas/map-definitions.json) (authoritative). Key maps include:

| Map Name | Description | Axes |
|----------|-------------|------|
| Fuel map (front) | Injector pulse width — front cylinder | RPM × MAP (load) |
| Fuel map (rear) | Injector pulse width — rear cylinder | RPM × MAP (load) |
| Ignition map (front) | Advance degrees BTDC — front cylinder | RPM × MAP (load) |
| Ignition map (rear) | Advance degrees BTDC — rear cylinder | RPM × MAP (load) |
| Injector dead-time | Pulse width correction vs battery voltage | Voltage |
| Cold-start enrichment | Extra fuel during cranking vs ECT | ECT |
| Warmup enrichment | Fuel correction during warm-up vs ECT | ECT |
| Lambda target | Target AFR vs operating region | RPM × load |
| Idle RPM target | Target idle speed | ECT |

---

## Safety Flash Rules

The following will **block any flash operation** (no override):

- `rev_limiter > 9500 RPM`
- `ignition_advance > 45 deg` at any cell
- `ignition_advance < -10 deg` at any cell
- `lambda_target > 1.05` at any WOT cell
- `lambda_target < 0.82` at any cell
- Fuel map contains all-zero row (lean seizure risk)
- Fuel map contains all-255 row (hydro-lock risk)
- Injector dead-time table not monotonically decreasing with voltage (corrupted)
- Checksum mismatch after edit
- File size != expected IAW 5AM binary size
- No verified backup from this session
- Battery voltage < 12.0V

---

## Pin Mapping

TODO: Document full ECU connector pinout from service manual:
- Signal ground pins
- Sensor reference voltage pins
- K-Line pin
- Immobilizer communication pin
- Injector drive pins
- Ignition coil drive pins
- Fuel pump relay pin
- Side-stand switch input pin

See [wiring.json](../schemas/wiring.json) for machine-readable pinout (when populated).

---

## Related Files

- [platform-differences.md](platform-differences.md) — SRV850 vs GP800 ECU differences
- [iaw5x-reader-writer.md](../procedures/iaw5x-reader-writer.md) — tool usage guide
- [obd-diagnostics.md](../procedures/obd-diagnostics.md) — diagnostic protocol details
- [bricked-ecu-recovery.md](../procedures/bricked-ecu-recovery.md) — recovery if flash fails

---

*TODO: Document exact binary file size, checksum algorithm, memory map addresses from IAW5xReader session.*
