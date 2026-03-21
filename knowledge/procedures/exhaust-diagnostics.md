# Exhaust Diagnostics — Reading Symptoms from Exhaust Behavior

## Overview

The exhaust tells you a great deal about combustion quality, fuel mixture, and ignition timing. This document covers how to interpret exhaust color, temperature, flames, and smoke.

**Safety note:** Red-hot exhaust or flames are active fire hazards. Kill engine immediately if observed.

---

## Exhaust Color

| Color | What It Indicates | Severity |
|-------|-------------------|----------|
| Light gray / colorless | Normal combustion on a warm engine | Normal |
| White (cold start, dissipates) | Normal condensation in cold exhaust | Normal |
| White (persistent when warm) | Coolant burning — possible head gasket failure | High |
| Blue/gray | Burning oil — worn rings or valve seals | Medium |
| Black, sooty | Excessively rich mixture — too much fuel | Medium |
| Black with raw fuel smell | Severe over-fueling or misfire | High |

---

## Exhaust Temperature

| Observation | Indication | Action |
|-------------|-----------|--------|
| Normal color, no glow | Correct combustion temperature | Continue |
| Muffler / pipes discoloring (bluing) | Higher than normal temperature | Investigate mixture and timing |
| Exhaust manifold/header glowing orange/red at idle | CRITICAL — extreme heat | KILL ENGINE immediately |
| Exhaust glowing within first minute of start | CRITICAL — severe problem | KILL ENGINE, do not restart |

**Current bike symptom:** Red-hot muffler visible during operation — this is the primary safety concern.

### Why Does Exhaust Glow?

Two primary causes of glowing exhaust:
1. **Unburned fuel combusting in exhaust pipe** — rich misfire: fuel that didn't burn in cylinder ignites in hot exhaust
2. **Extreme ignition retard** — combustion continues into exhaust stroke, heating the exhaust directly

Both require correcting the root cause (maps or mechanical). Do not mask with exhaust wrapping.

---

## Flames from Exhaust

**Flames from exhaust = active fire risk. Kill engine immediately.**

| Flame Behavior | Likely Cause |
|----------------|-------------|
| Flames on overrun / deceleration | Deceleration fuel cut-off too aggressive, or backfire on lean misfire |
| Flames at idle | Severe over-fueling, ignition misfire, or extreme timing retard |
| Continuous flames | Multiple causes — do not attempt diagnosis while running |
| Flames on acceleration | Lean misfire at tip-in, or ignition coil breakdown |

**Current bike symptom:** Flames observed at idle at home. This is consistent with the scrambled maps producing extreme fueling or ignition errors.

---

## Exhaust-Related DTCs

| Code | Description | Exhaust Symptom |
|------|-------------|-----------------|
| 21 | O2 sensor no activity | Rich or lean running at cruise |
| 24 | Ignition coil 1 (front) | Front cylinder misfire, raw fuel in exhaust |
| 25 | Ignition coil 2 (rear) | Rear cylinder misfire, raw fuel in exhaust |
| 22 | Injector 1 (front) open | No fuel, cylinder misfiring |
| 23 | Injector 2 (rear) open | No fuel, cylinder misfiring |

---

## Exhaust Leak Detection

An exhaust leak before the lambda sensor will cause false lean readings, leading to over-fueling.

| Check | Method |
|-------|--------|
| Header gasket leaks | Run engine, listen for ticking, look for soot at joint |
| Pipe joints | Look for soot streaks indicating escaping gas |
| Catalyst | Shake the cat — rattle indicates a broken catalyst substrate |

---

## Catalytic Converter Notes

| Issue | Symptom |
|-------|---------|
| Partially blocked catalyst | Power loss especially at WOT, high backpressure |
| Broken substrate | Rattling, possible blockage |
| Overheated catalyst | Extreme richness over time destroys washcoat |

Running extremely rich (current situation) will eventually destroy the catalytic converter if not corrected.

---

## Exhaust Smoke Interpretation Summary

| Smoke Type | Color | Smell | Meaning |
|------------|-------|-------|---------|
| Normal condensation | White | None | OK at cold start |
| Coolant leak | White/sweet | Sweet/antifreeze | Head gasket or worse |
| Oil burning | Blue | Oily/acrid | Ring or seal wear |
| Rich mixture | Black/gray | Fuel | Too much fuel |
| Raw fuel | Black | Very strong fuel | Severe misfire/flooding |

---

## What to Do Right Now (Current Bike)

Given the current symptoms (red-hot exhaust, flames at idle):

1. Do NOT start the bike
2. Read DTCs before starting — note all active codes
3. Inspect exhaust system physically for leaks or damage
4. Do not attempt to "fix" exhaust symptoms by adjusting maps without first completing [mechanical-pre-check.md](mechanical-pre-check.md)
5. Obtain and flash a known-good stock map before attempting any test run
6. First start after flash: second person present with fire extinguisher

---

## Related Files

- [diagnostic-flowcharts.md](diagnostic-flowcharts.md) — decision trees for red exhaust and flames
- [tuning-common-mistakes.md](tuning-common-mistakes.md) — how map errors cause these symptoms
- [mechanical-pre-check.md](mechanical-pre-check.md) — exhaust integrity check
- [error-codes.md](../reference/error-codes.md) — relevant DTCs

---

*TODO: Document normal exhaust color at operating temperature with correctly tuned maps, and add exhaust temperature probe measurement procedure if thermocouple is available.*
