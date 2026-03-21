# Platform Differences — Gilera GP800 vs Aprilia SRV850

## Overview

Both bikes share the same 839cc V-twin engine and IAW 5AM ECU platform. The key differences are in ABS integration, immobilizer antenna arrangement, calibration, and dashboard communication. This bike has an **SRV850 ECU installed in a GP800 chassis**.

---

## ECU

| Feature | GP800 | SRV850 | Impact on This Bike |
|---------|-------|--------|---------------------|
| ECU model | IAW 5AM | IAW 5AM | Same hardware platform |
| ABS module integration | No ABS | ABS module expected | ECU may expect ABS signals that don't exist in GP800 chassis |
| Immobilizer antenna | Integrated arrangement | Separate antenna ring | Wiring verification required |
| Calibration (maps) | GP800-specific | SRV850-specific | Maps must be correct for actual hardware |

---

## Immobilizer

| Feature | GP800 | SRV850 |
|---------|-------|--------|
| Transponder type | Megamos / ID48 | Megamos / ID48 |
| Antenna ring | Integrated with ignition barrel | Separate ring, externally wired to ECU |
| Key coding | Factory linked | Factory linked |

**Current bike:** SRV850 ECU is installed. The immobilizer antenna ring wiring needs to be verified to ensure it matches the SRV850 ECU's expected arrangement, not the GP800's. This may be one source of intermittent no-start symptoms if the immobilizer communication is unreliable.

---

## ABS

| Feature | GP800 | SRV850 |
|---------|-------|--------|
| ABS hardware | Not fitted | ABS pump, modulator, wheel sensors |
| ECU ABS entries | Not present | Expects ABS sensor signals |

**Impact:** The SRV850 ECU in the GP800 chassis will not receive ABS sensor signals. Whether this generates active faults or is silently ignored depends on the specific calibration. Need to verify via IAW5xReader DTC scan.

---

## Sensor Compatibility

| Signal | GP800 | SRV850 ECU Expects | Status |
|--------|-------|-------------------|--------|
| TPS voltage range | ~0.5–4.5V | 0.5–4.5V | Compatible — verify on actual hardware |
| Injector impedance | ~12 Ohm | ~12 Ohm | Compatible |
| Lambda heater circuit | Shared ground | Dedicated ground | Wiring check required |
| ECT sensor curve | NTC 2.5k @ 20°C | NTC 2.5k @ 20°C | Compatible |
| Immobilizer | Integrated | Separate ring | Wiring check required |

---

## Dashboard / Instrumentation

| Feature | GP800 | SRV850 |
|---------|-------|--------|
| Speedometer | Mechanical or CAN | CAN or K-Line |
| ABS warning lamp | Not present | Present |
| Other differences | TODO | TODO |

TODO: Document dashboard communication differences that may cause warning lights or incorrect readings.

---

## Shared Platform Parts (Cross-Compatible)

The following parts are shared across the Piaggio 850 platform and can be used interchangeably:

| Part | Compatible Models |
|------|-------------------|
| Engine internals | GP800, SRV850, Mana850, Dorsoduro850 |
| Injectors | Verify flow rate before use |
| ECT sensor | GP800, SRV850 (NTC curve identical) |
| IAT sensor | GP800, SRV850 |
| MAP sensor | GP800, SRV850 |

See [parts-compatibility.json](../schemas/parts-compatibility.json) for machine-readable compatibility data.

---

## Calibration Differences

TODO: Document any known differences in map values between OEM GP800 calibration and OEM SRV850 calibration:
- Idle RPM target
- Cold-start enrichment
- WOT fueling
- Rev limiter setting
- Lambda targets

This is critical for deciding which OEM map to use as the recovery baseline.

---

## Related Files

- [electrical.md](electrical.md) — immobilizer and wiring detail
- [ecu-iaw5am.md](ecu-iaw5am.md) — ECU architecture
- [srv850-to-gp800-wiring.md](../../my-bike/srv850-to-gp800-wiring.md) — open wiring investigation
- [platform-spec.json](../schemas/platform-spec.json) — machine-readable platform data
- [parts-compatibility.json](../schemas/parts-compatibility.json) — parts cross-reference

---

*TODO: Document exact ABS DTC behavior, dashboard CAN/K-Line differences, and OEM calibration differences from service manuals for both models.*
