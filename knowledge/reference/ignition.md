# Ignition System Reference

## Overview

The GP800 uses a **twin-spark** ignition system: two spark plugs per cylinder, four plugs total. Each cylinder has a dedicated ignition coil. The IAW 5AM ECU controls ignition timing independently per cylinder.

The rear cylinder runs hotter than the front. Ignition timing for the rear should start 1–2 degrees more retarded than the front.

---

## Spark Plugs

| Parameter | Value |
|-----------|-------|
| Plug type | NGK CR9EK |
| Quantity | 4 total (2 per cylinder) |
| Heat range | 9 (standard) |
| Plug gap | TODO: Confirm from service manual |
| Replacement interval | TODO: Confirm from service manual |

**Note:** Both plugs in a cylinder must be the same type and heat range.

---

## Ignition Coils

| Parameter | Value | Notes |
|-----------|-------|-------|
| Configuration | One coil per cylinder | 2 coils total |
| Primary resistance | 0.5–2.0 Ohm | Measure across primary terminals |
| Secondary resistance | 6,000–12,000 Ohm | Measure across HT lead terminals |
| DTC | Code 24 = coil 1 (front) primary circuit fault | |
| DTC | Code 25 = coil 2 (rear) primary circuit fault | |

**Coil testing procedure:**
1. Disconnect coil connector (engine off, ignition off)
2. Measure primary resistance across the two small-wire pins: expect 0.5–2.0 Ohm
3. Measure secondary resistance across the two HT lead towers: expect 6,000–12,000 Ohm
4. Any open circuit (OL) or short (<0.1 Ohm primary) = replace coil

---

## Ignition Timing

| Operating Condition | Target | Notes |
|--------------------|--------|-------|
| Idle | 10–14 deg BTDC | Front and rear independently tuned |
| Cruise | Advance for best torque | Watch for knock |
| WOT | Advance 1 degree at a time only | Rear: start 1–2 deg more retarded than front |
| Hard limit (max advance) | 45 deg BTDC | Flash blocker — no override |
| Hard limit (max retard) | -10 deg BTDC | Flash blocker — extreme retard causes exhaust fires |

**Ignition timing tuning order:** Always tune after fuel maps are stable. One degree at a time at WOT. See [tuning-workflow.md](../procedures/tuning-workflow.md).

---

## Crankshaft Position Sensor (CKP)

| Parameter | Value |
|-----------|-------|
| Type | VR inductive sensor |
| Resistance | 200–400 Ohm |
| Signal type | AC (generates sine wave as teeth pass) |
| DTC | Code 33 = CKP no signal (no start, random stalling) |

**CKP testing:**
1. Disconnect sensor connector
2. Measure resistance across sensor pins: 200–400 Ohm expected
3. Check for metal shavings on sensor tip (clean if found)
4. Verify air gap: TODO from service manual

---

## Camshaft Position Sensor (CMP)

TODO: Confirm whether GP800 / SRV850 uses a CMP sensor or relies on CKP-only cylinder identification. Document resistance and signal type if present.

---

## Ignition-Related Safety Rules

- Extreme retard (< -10 deg) causes unburned fuel in exhaust → exhaust fires → exhaust valve damage
- Excessive advance (> 40 deg on 95 RON) causes detonation → piston damage
- Red-hot exhaust manifold can indicate severely retarded or incorrect timing — diagnose before any changes
- Never change ignition timing and fuel maps simultaneously

---

## Related Files

- [engine-specs.md](engine-specs.md) — overall engine parameters
- [sensor-reference.md](sensor-reference.md) — CKP and CMP sensor testing
- [tuning-workflow.md](../procedures/tuning-workflow.md) — timing tuning sequence
- [exhaust-diagnostics.md](../procedures/exhaust-diagnostics.md) — interpreting exhaust symptoms

---

*TODO: Confirm plug gap, replacement interval, CMP sensor presence/absence, CKP air gap from service manual.*
