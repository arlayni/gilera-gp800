# Mechanical Pre-Check — 14-Point Gate Before ECU Work

## Overview

This checklist must be completed and all points must pass before any ECU map work is performed. Attempting to fix mechanical problems with ECU maps is the most common source of map corruption.

**Document actual measured values — pass/fail alone is not sufficient.**

---

## Checklist

### Point 1: Compression Test

| Cylinder | Measured (bar) | Expected | Pass? |
|----------|---------------|----------|-------|
| Front | — | 11–14 bar (cold) | |
| Rear | — | 11–14 bar (cold) | |
| Variance | — | <10% between cylinders | |

**Minimum serviceable:** 10.5 bar per cylinder.

**Procedure:**
1. Remove all 4 spark plugs
2. Install compression tester in each plug hole (one cylinder at a time)
3. Crank engine 3–4 times with throttle wide open
4. Record peak pressure
5. Repeat for other cylinder

**BLOCKING if:** Either cylinder <10.5 bar, or >10% variance between cylinders.

---

### Point 2: Vacuum Leak Test

| Area | Method | Result |
|------|--------|--------|
| Intake boots | Spray carb cleaner, watch RPM | — |
| Throttle body gaskets | Spray test | — |
| MAP sensor hose | Spray test | — |
| Any intake connection | Spray test | — |

**Method:** Engine running at idle. Spray small amounts of carburetor cleaner at each intake connection. RPM change = vacuum leak at that point.

**BLOCKING if:** Any vacuum leak found — AFR readings unreliable until repaired.

---

### Point 3: Throttle Body Synchronization

| TB | Measured Vacuum (kPa or mmHg) | Result |
|----|-------------------------------|--------|
| Front | — | |
| Rear | — | |
| Balance | — | Should be within 10% |

**Tool required:** Manometer (vacuum gauge, dual-column preferred).

**BLOCKING if:** Significant imbalance — one throttle body must not be substantially more open than the other at idle.

---

### Point 4: Fuel Pressure

| Condition | Measured (bar) | Expected | Pass? |
|-----------|---------------|----------|-------|
| Key on, engine off | — | 3.5–4.0 bar | |
| Idle | — | 3.0–3.5 bar | |
| 3000 RPM steady | — | 3.0–3.5 bar | |

**Tool required:** Fuel pressure gauge connected to fuel rail test port.

**BLOCKING if:** Pressure below 3.0 bar under load — ECU cannot compensate for fuel starvation.

---

### Point 5: Exhaust Integrity

| Check | Result |
|-------|--------|
| Header gaskets — no leaks | — |
| SAI valve — functional or blocked | — |
| Catalyst — no rattle | — |
| Header warpage — no visible warping | — |
| Lambda sensor resistance | — (expected: 2–15 Ohm heater) |

Exhaust leaks before the lambda sensor will cause false lean readings.

---

### Point 6: Cardan Shaft Verification

| Check | Result |
|-------|--------|
| Spline engagement correct depth | — |
| Splines lubricated | — |
| U-joint play — no excessive play | — |
| Flange bolt torque (TODO: spec from service manual) | — |
| No vibration at idle | — |
| Final drive oil level correct | — |
| Output shaft seal — no leak | — |
| Backlash measurement (TODO: spec) | — |

**Note:** Cardan shaft on this bike was owner-installed without documentation. This point is especially important.

---

### Point 7: Sensor Functionality

| Sensor | Test | Result |
|--------|------|--------|
| TPS sweep | 0.5V closed → 4.5V WOT, smooth | — |
| MAP at idle | ~1.0V | — |
| ECT cold | ~2,500 Ohm @ 20°C | — |
| IAT | ~2,000–3,000 Ohm @ 20°C | — |
| CKP | 200–400 Ohm | — |
| O2 heater | 2–15 Ohm | — |
| CMP (if present) | TODO | — |

See [sensor-reference.md](../reference/sensor-reference.md) for full testing procedures.

---

### Point 8: Battery Load Test

| Test | Measured | Expected | Pass? |
|------|----------|----------|-------|
| Battery at rest | — | >12.4V | |
| Battery during cranking | — | >10.5V | |
| Battery for flash operations | — | >12.0V | |

**BLOCKING:** Battery below 12.0V = do not flash ECU. Risk of corrupted write.

---

### Point 9: Ground Points

| Location | Resistance (Ohm) | Expected | Pass? |
|----------|-----------------|----------|-------|
| Battery negative to engine block | — | <0.1 Ohm | |
| Battery negative to frame | — | <0.1 Ohm | |
| ECU ground pin 1 | — | <0.1 Ohm | |
| ECU ground pin 2 | — | <0.1 Ohm | |

**Pre-check limit:** <0.5 Ohm acceptable. High resistance grounds cause sensor errors that mimic sensor failures.

---

### Point 10: ECU Connector Inspection

| Check | Result |
|-------|--------|
| No corrosion on pins | — |
| No bent or pushed-back pins | — |
| Connector locks click securely | — |
| No moisture inside connector | — |

---

### Point 11: CVT Belt Inspection

| Check | Result |
|-------|--------|
| Width (measured with calipers) | — |
| No cracking | — |
| No glazing (shiny surface) | — |
| No burning or scorch marks | — |

**TODO:** Obtain minimum belt width specification from service manual.

---

### Point 12: Clutch Assessment

| Check | Result |
|-------|--------|
| Engagement RPM (~3000 RPM expected) | — |
| Shoe/pad thickness above minimum | — |
| Drum condition — no deep scoring | — |
| Springs — no breakage or fatigue | — |

---

### Point 13: Air Filter Condition

| Check | Result |
|-------|--------|
| Filter clean (or replaced) | — |

A blocked air filter causes rich running. Fix mechanically, not in maps.

---

### Point 14: Fuel Filter Condition

| Check | Result |
|-------|--------|
| Filter inspected or replaced | — |

A restricted fuel filter causes power loss under load (insufficient fuel flow). Fix mechanically.

---

## Pass/Fail Summary

| Point | Description | Pass? | Notes |
|-------|-------------|-------|-------|
| 1 | Compression | | |
| 2 | Vacuum leak | | |
| 3 | TB sync | | |
| 4 | Fuel pressure | | |
| 5 | Exhaust integrity | | |
| 6 | Cardan shaft | | |
| 7 | Sensor functionality | | |
| 8 | Battery load test | | |
| 9 | Ground points | | |
| 10 | ECU connector | | |
| 11 | CVT belt | | |
| 12 | Clutch | | |
| 13 | Air filter | | |
| 14 | Fuel filter | | |

**ALL 14 points must pass before proceeding to ECU work.**

---

## Related Files

- [diagnostic-flowcharts.md](diagnostic-flowcharts.md) — symptom decision trees
- [sensor-reference.md](../reference/sensor-reference.md) — sensor test values
- [transmission-cvt.md](../reference/transmission-cvt.md) — CVT and cardan detail
- [tuning-workflow.md](tuning-workflow.md) — what comes after this checklist

---

*TODO: Add minimum CVT belt width, clutch shoe minimum thickness, cardan flange torque, and thermostat opening temp from service manual.*
