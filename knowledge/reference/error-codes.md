# Error Codes — IAW 5AM Diagnostic Trouble Codes

## Overview

The IAW 5AM ECU stores and reports DTCs (Diagnostic Trouble Codes) via two methods:
1. **IAW5xReader software** — reads codes over K-Line (preferred, complete list)
2. **MIL blink code** — reads codes via the dashboard warning lamp without tools

Machine-readable DTC data: [error-codes.json](../schemas/error-codes.json)

---

## MIL Blink Code Reading Procedure

**Precondition:** Ignition ON, engine OFF.

**Trigger sequence:**
1. Turn ignition ON (engine OFF)
2. Within 3 seconds, fully open and close the throttle **3 times**
3. The MIL (engine warning light) will begin flashing

**Reading the code:**
- **Long flash** = tens digit
- **Short flash** = units digit
- Example: 2 long flashes + 3 short flashes = Code 23

**Multiple codes:** After a pause, the ECU will blink the next code. Note all codes before clearing.

**Clearing codes:** TODO — confirm procedure from IAW5xReader documentation (may require connecting the tool).

---

## DTC Quick Reference

| Code | System | Description | Severity | Symptoms |
|------|--------|-------------|----------|----------|
| 11 | Cooling | ECT sensor open/short | High | Rich running, no fan, wrong cold-start enrichment |
| 12 | Intake | IAT sensor open/short | High | Rich running if open (ECU sees -40°C) |
| 13 | Intake | MAP sensor out of range | High | Wrong fueling at all RPM/load points |
| 14 | Throttle | TPS out of range / implausible | Critical | Erratic idle, unpredictable fueling |
| 15 | Electrical | Battery voltage out of range | Medium | Injector dead-time errors, weak spark |
| 21 | Exhaust | O2 sensor no activity / heater circuit | Medium | No closed-loop correction, stuck rich or lean |
| 22 | Fuel | Injector 1 (front) open/short | Critical | Front cylinder misfire or no fuel |
| 23 | Fuel | Injector 2 (rear) open/short | Critical | Rear cylinder misfire or no fuel |
| 24 | Ignition | Coil 1 (front) primary circuit | Critical | Front cylinder misfire |
| 25 | Ignition | Coil 2 (rear) primary circuit | Critical | Rear cylinder misfire |
| 31 | Fuel | Fuel pump relay circuit | Critical | No fuel delivery, no prime on key-on |
| 32 | Idle | Idle air control valve circuit | Medium | Unstable idle, stalling |
| 33 | Ignition | CKP sensor no signal | Critical | No start, random stalling |
| 41 | Drivetrain | Vehicle speed sensor no signal | Low | No speedometer, DFCO may not function |
| 42 | Safety | Side-stand switch circuit | Medium | Engine cuts when in gear, no-start |
| 43 | Safety | Tip-over sensor circuit | Medium | Random engine kill |
| 44 | Security | Immobilizer communication error | Critical | No start, intermittent no-start, fuel cut |

**Note:** Code numbers may vary by ECU calibration and year. Always confirm via IAW5xReader live DTC readout.

---

## First Steps When a DTC Is Present

1. **Read all codes** — note every code before clearing any
2. **Do not clear and ignore** — understand the root cause first
3. **Cross-reference symptoms** — does the DTC match the observed behavior?
4. **Check mechanical causes first** — a sensor DTC can be caused by a wiring fault, not a bad sensor
5. **Verify with multimeter** — see [sensor-reference.md](sensor-reference.md) for test procedures

---

## Current Active DTCs

TODO: Connect IAW5xReader and document current live DTCs for this bike. This is a mandatory first step before any diagnostic work.

---

## ABS-Related Codes (SRV850 ECU)

The installed SRV850 ECU may generate ABS-related codes because the GP800 chassis does not have ABS hardware. Document which ABS codes are present and whether they are blocking engine operation.

---

## Related Files

- [error-codes.json](../schemas/error-codes.json) — machine-readable DTC data
- [sensor-reference.md](sensor-reference.md) — sensor testing when DTCs are sensor-related
- [obd-diagnostics.md](../procedures/obd-diagnostics.md) — IAW5xReader procedure for reading DTCs
- [diagnostic-flowcharts.md](../procedures/diagnostic-flowcharts.md) — what to do after reading codes

---

*TODO: Document code clearing procedure, ABS DTC codes for SRV850, and expand DTC list from IAW5xReader full DTC output.*
