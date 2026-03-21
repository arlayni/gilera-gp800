# Sensor Reference — All Sensors with Test Procedures

## Overview

This document provides multimeter testing procedures and expected values for all major sensors on the GP800 / SRV850 ECU system.

Machine-readable sensor specs: [sensor-specs.json](../schemas/sensor-specs.json)

**Always test with ignition ON, engine OFF unless otherwise noted.**

---

## Quick Reference Table

| Sensor | Test Method | Expected Value | DTC |
|--------|-------------|----------------|-----|
| TPS signal | DC Volts | 0.5V closed → 4.5V WOT | 14 |
| MAP signal | DC Volts | ~1V idle, ~4V key-on | 13 |
| IAT resistance | Ohms | 2,000–3,000 Ohm @ 20°C | 12 |
| ECT resistance | Ohms | 2,500 Ohm @ 20°C, 300 Ohm @ 90°C | 11 |
| CKP resistance | Ohms | 200–400 Ohm (inductive VR sensor) | 33 |
| CMP sensor | TODO | TODO | — |
| O2 heater | Ohms | 2–15 Ohm | 21 |
| O2 signal | DC Volts | 0.1V lean, 0.7–0.9V rich | 21 |
| Injector | Ohms | 12–16 Ohm | 22/23 |
| Coil primary | Ohms | 0.5–2.0 Ohm | 24/25 |
| Coil secondary | Ohms | 6,000–12,000 Ohm | 24/25 |
| Battery resting | DC Volts | >12.4V | 15 |
| Charging @ idle | DC Volts | 13.5–14.5V | 15 |
| Fuel pressure | Pressure gauge | 3.0–3.5 bar | — |

---

## Throttle Position Sensor (TPS)

**Type:** Potentiometer (3-wire: 5V reference, signal, ground)
**DTC:** Code 14 — out of range / implausible

| Condition | Expected Voltage |
|-----------|-----------------|
| Fully closed (idle) | 0.5V (±0.1V) |
| 25% open | ~1.5V |
| 50% open | ~2.5V |
| 75% open | ~3.5V |
| Wide open throttle | 4.5V (±0.2V) |

**Test procedure:**
1. Ignition ON, engine OFF
2. Backprobe signal wire at TPS connector (do not disconnect)
3. Slowly open throttle from fully closed to fully open
4. Verify smooth linear voltage increase, no dead spots, no dropouts

**Failure indicators:** Any sudden drop to 0V or jump to 5V during sweep = contamination or wear.

---

## Manifold Absolute Pressure (MAP)

**Type:** Piezo-resistive (3-wire: 5V reference, signal, ground)
**DTC:** Code 13 — out of range

| Condition | Expected Voltage | Pressure |
|-----------|-----------------|----------|
| Key on, engine off | ~4.0V | ~100 kPa (atmospheric) |
| Idle | ~1.0V | ~35–45 kPa |
| 2000 RPM | ~1.2–1.5V | ~50–60 kPa |
| WOT | ~3.5–4.0V | ~95–105 kPa |

---

## Engine Coolant Temperature (ECT)

**Type:** NTC thermistor (2-wire: signal and ground)
**DTC:** Code 11 — open/short circuit

| Temperature | Expected Resistance | Notes |
|-------------|---------------------|-------|
| Cold 20°C | ~2,500 Ohm | |
| Warm 80°C | ~200–300 Ohm | Normal operating temp |
| Hot 100°C | ~100–150 Ohm | Near thermostat opening |

**Test procedure:**
1. Disconnect ECT sensor connector
2. Measure resistance across sensor pins with multimeter on Ohms
3. Compare to temperature vs resistance table

**If open circuit (OL):** ECU assumes -40°C → applies maximum cold-start enrichment → engine runs excessively rich.

---

## Intake Air Temperature (IAT)

**Type:** NTC thermistor (2-wire: signal and ground)
**DTC:** Code 12 — open/short circuit

| Temperature | Expected Resistance |
|-------------|---------------------|
| 0°C | ~5,000–6,000 Ohm |
| 20°C | ~2,000–3,000 Ohm |
| 40°C | ~1,000–1,500 Ohm |

**If open circuit:** ECU assumes -40°C → applies cold-air density correction → rich running.

---

## Crankshaft Position Sensor (CKP)

**Type:** Variable reluctance (VR) inductive sensor (2-wire, generates AC signal)
**DTC:** Code 33 — no signal

| Test | Expected |
|------|----------|
| Resistance | 200–400 Ohm |
| Signal type | AC sine wave (check with oscilloscope at cranking speed) |

**Test procedure:**
1. Disconnect CKP connector
2. Measure resistance across the two pins: 200–400 Ohm
3. Check sensor tip for metal shavings — clean if found
4. Air gap: TODO from service manual

---

## Camshaft Position Sensor (CMP)

**Status:** TODO — Confirm whether the GP800 / SRV850 uses a CMP sensor or relies on CKP-only for cylinder identification.

---

## Oxygen / Lambda Sensor

**Type:** Heated narrowband lambda (4-wire: signal, ground, heater+, heater-)
**DTC:** Code 21 — no activity or heater circuit fault

| Test | Expected |
|------|----------|
| Heater resistance | 2–15 Ohm (across heater wires) |
| Signal: rich | 0.7–0.9V |
| Signal: lean | 0.1–0.3V |
| Signal: closed loop | 0.4–0.6V (oscillating between rich/lean) |

**Note:** Lambda sensor must be at operating temperature (>300°C) for accurate signal. Allow engine warm-up before interpreting signal voltage.

---

## Fuel Injectors

**Type:** High-impedance electromagnetic (2-wire)
**DTC:** Code 22 (front), Code 23 (rear)

| Test | Expected |
|------|----------|
| Resistance | 12–16 Ohm |

**Test procedure:**
1. Disconnect injector connector
2. Measure resistance across the two pins
3. <1 Ohm = short circuit; OL = open circuit — both require replacement

---

## Ignition Coils

**DTC:** Code 24 (front), Code 25 (rear)

| Test | Expected |
|------|----------|
| Primary resistance | 0.5–2.0 Ohm |
| Secondary resistance | 6,000–12,000 Ohm |

---

## Cross-Reference Priority Matrix

When diagnosing a symptom, use this table to prioritize which sensors to test first:

| Component | Rough Idle | Power Loss | Red Exhaust | Stalling |
|-----------|:---:|:---:|:---:|:---:|
| Vacuum leak | *** | * | * | ** |
| TPS | ** | * | — | *** |
| MAP sensor | ** | ** | *** | * |
| ECT sensor | ** | ** | *** | * |
| Fuel pressure | ** | *** | ** | * |
| Ignition coils | * | *** | *** | * |
| O2 sensor | * | ** | * | ** |

(*** = highly likely cause, * = less likely)

---

## Related Files

- [sensor-specs.json](../schemas/sensor-specs.json) — machine-readable sensor data (authoritative)
- [error-codes.md](error-codes.md) — DTC reference
- [diagnostic-flowcharts.md](../procedures/diagnostic-flowcharts.md) — symptom decision trees
- [baseline-measurements.md](../../my-bike/baseline-measurements.md) — measurement tables for this bike

---

*TODO: Confirm CMP sensor presence/absence, CKP air gap, IAT resistance curve at additional temperature points from service manual.*
