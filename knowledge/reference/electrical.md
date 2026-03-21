# Electrical System Reference

## Overview

Key electrical systems: immobilizer (Megamos/ID48 transponder), side-stand safety switch, K-Line diagnostic protocol, battery, and charging system.

---

## Battery & Charging

| Test | Expected | Notes |
|------|----------|-------|
| Battery at rest (engine off) | 12.6–12.8V | <12.4V = needs charging or replacement |
| Battery during cranking | >10.5V | Should not drop below this |
| Charging at idle | 13.5–14.2V | |
| Charging at 3000 RPM | 13.8–14.5V | |

**Flash requirement:** Battery must be >12.0V before any ECU flash operation. Risk of corrupted write below this threshold.

---

## Ground Connections

Ground integrity is critical for correct sensor readings and ECU operation.

| Test Point | Expected Resistance | Notes |
|------------|---------------------|-------|
| Battery negative to engine block | <0.1 Ohm | |
| Battery negative to frame | <0.1 Ohm | |
| ECU ground pin 1 | <0.1 Ohm | |
| ECU ground pin 2 | <0.1 Ohm | |

Acceptable limit for pre-check: <0.5 Ohm at any ground point. High resistance grounds cause erratic sensor readings that look like sensor failures.

---

## Immobilizer System

| Parameter | Value |
|-----------|-------|
| Transponder type | Megamos / ID48 |
| Protocol | RF transponder in key, read by antenna ring around ignition barrel |
| ECU integration | Integrated into IAW 5AM ECU |
| DTC | Code 44 = immobilizer communication error |

**GP800 vs SRV850 difference:** The SRV850 ECU uses a separate antenna ring rather than the GP800's integrated arrangement. See [platform-differences.md](platform-differences.md).

**Current status:** Key chip codes were re-linked to the SRV850 ECU by a friend after memory loss. Only one key is currently linked. No backup key or code recovery documentation. See [modifications.md](../../my-bike/modifications.md).

**Security policy:** Transponder key codes and immobilizer PIN codes are NEVER stored in shared files. See [immobilizer.json](../schemas/immobilizer.json) (redacted).

**If immobilizer blocks start:**
1. Check DTC 44 in IAW5xReader
2. Verify key is the correct coded key
3. Check antenna ring wiring continuity
4. Check ECU connector for corrosion on immobilizer communication pin
5. Professional immobilizer specialist if above fail — do not attempt to bypass without understanding consequences

---

## Side-Stand Switch

| Parameter | Value |
|-----------|-------|
| Function | Safety interlock — cuts engine when stand deployed and in gear |
| Failure mode | Engine cuts unexpectedly, or no-start |
| DTC | Code 42 = side-stand switch circuit |
| History | Original GP800 ECU failed due to a side-stand switch signal fault |

**Testing:**
1. With stand up: switch should show closed circuit (TODO: confirm polarity from wiring diagram)
2. With stand down: switch should show open circuit
3. Verify resistance and continuity at ECU pin level

---

## K-Line Diagnostic Protocol

| Parameter | Value |
|-----------|-------|
| Protocol | K-Line ISO 9141-2 |
| Baud rate | 10,400 baud |
| Connector | TODO: Locate diagnostic connector on bike (under seat? near ECU?) |
| Hardware required | IAW5xReader/Writer (owner has this) |
| NOT compatible with | Standard OBD2 scanners |

See [obd-diagnostics.md](../procedures/obd-diagnostics.md) and [ecu-iaw5am.md](ecu-iaw5am.md).

---

## Tip-Over Sensor

| Parameter | Value |
|-----------|-------|
| Function | Cuts engine if bike tips over |
| DTC | Code 43 = tip-over sensor circuit |
| Note | Can cause random engine cuts if faulty or dirty |

---

## Wiring Reference

Full pinout data lives in [wiring.json](../schemas/wiring.json) (to be populated).

Key wiring areas to verify for this bike (SRV850 ECU in GP800 chassis):
- Lambda sensor heater circuit (SRV850 uses dedicated ground; GP800 uses shared ground)
- ABS wiring stubs (SRV850 ECU may expect ABS signals that GP800 chassis does not have)
- Immobilizer antenna ring wiring

See [srv850-to-gp800-wiring.md](../../my-bike/srv850-to-gp800-wiring.md) for the open investigation checklist.

---

## Related Files

- [platform-differences.md](platform-differences.md) — GP800 vs SRV850 electrical differences
- [ecu-iaw5am.md](ecu-iaw5am.md) — ECU communication and pinout
- [obd-diagnostics.md](../procedures/obd-diagnostics.md) — diagnostic tool usage
- [immobilizer.json](../schemas/immobilizer.json) — immobilizer data (redacted)
- [wiring.json](../schemas/wiring.json) — full pinout (to be populated)

---

*TODO: Document diagnostic connector location, confirm side-stand switch polarity, document ABS stub wiring handling from service manuals for both GP800 and SRV850.*
