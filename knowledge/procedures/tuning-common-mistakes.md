# Tuning Common Mistakes — What Goes Wrong and Why

## Overview

This document records known tuning mistakes, their symptoms, and how to identify and correct them. Many of these mistakes can cause dangerous riding conditions. Some require a full map recovery.

---

## Mistake 1: Global Lean-Out

**What it is:** Reducing fuel across all map cells simultaneously, rather than targeting specific operating regions.

**How it happens:**
- Applying a percentage reduction across the entire fuel map
- Copying a map from a different engine or injector size without scaling
- Using AI-generated map values without understanding the baseline

**Symptoms:**
- Lean misfire at idle (stumbling, popping)
- Red-hot exhaust manifold
- Flames from exhaust under certain conditions
- Power loss under load
- Lambda readings consistently >1.0 across operating range
- Risk of melted pistons if sustained at WOT

**How to identify:** Load fuel map, compute cell-by-cell delta vs stock. Systematic reduction across all cells at all RPM/load points.

**Fix:** Flash known-good stock map. Re-tune from baseline. Never reduce fuel globally without a specific measured reason at each operating point.

---

## Mistake 2: Excessive Ignition Advance

**What it is:** Advancing ignition timing beyond safe limits, especially at high RPM or under load.

**How it happens:**
- Copying timing maps from a higher-octane or turbo application
- Advancing timing in all cells simultaneously looking for "more power"
- Not checking the rear cylinder separately (it needs less advance than the front)

**Symptoms:**
- Pinging / knocking under load (metallic rattling sound)
- Piston crown damage (visible during inspection)
- Overheating
- Lambda may read normal while engine is destroying itself

**Hard limits:** Never exceed 45 deg BTDC at any cell. Hard flash blocker — no override.

**Fix:** Flash map with timing within safe range. Use 1 degree increments only. Always listen for knock.

---

## Mistake 3: Disabling Lambda Correction

**What it is:** Setting lambda target outside the active range, zeroing the oxygen sensor correction table, or physically disconnecting the O2 sensor without compensating fuel maps.

**How it happens:**
- Attempt to "run open loop" without understanding the implications
- Disconnecting O2 sensor after it gives DTC 21, without diagnosing why
- Zeroing trim tables as a "quick fix"

**Symptoms:**
- Lambda trims stuck at maximum positive or negative correction
- Fuel mixture drifts as engine warms up
- Cruise economy degrades
- DTC 21 if sensor is disconnected

**Fix:** Re-enable lambda correction. Diagnose and repair O2 sensor heater circuit if Code 21 was the trigger. Never disable closed-loop correction unless running a known-verified open-loop map.

---

## Mistake 4: Wrong Cylinder Targeted

**What it is:** Editing the front cylinder fuel map when the rear was the problem, or vice versa.

**How it happens:**
- IAW5xReader/Writer presents maps in a certain order; easy to select the wrong one
- Symptom incorrectly attributed to wrong cylinder

**Symptoms:**
- Symptom is unchanged after map edit
- Opposite cylinder now runs wrong
- Lambda readings showing opposite of expected correction

**How to identify:** Always confirm which cylinder you are editing before writing. Check which DTC code is active (22 = front injector, 23 = rear injector).

**Fix:** Revert the incorrect edit. Re-diagnose which cylinder is at fault. Edit the correct map.

---

## Mistake 5: Copying Maps From Another Bike or Platform

**What it is:** Copying map files from a forum, another owner's bike, or a different model without validating compatibility with your specific hardware.

**How it happens:**
- Searching online for "GP800 ECU map" and flashing whatever is found
- Assuming SRV850 maps work on GP800 or vice versa without checking calibration
- Using AI-generated map values (this is how the current maps were corrupted)

**Symptoms:**
- Any combination of the above symptoms
- Hard to predict because it depends on how different the source map is from your hardware

**Validation pipeline (must complete before flashing any external map):**
1. Structural validation: file size = expected IAW 5AM binary size, checksum valid
2. Safety bounds: no cells outside hard limits (rev limiter, AFR, timing)
3. Hardware compatibility: injector size, sensor curves match THIS hardware
4. Delta comparison vs known baseline: flag cells >15% different
5. Only flash if validation PASSES; otherwise use as REFERENCE ONLY

---

## Mistake 6: Not Backing Up First

**What it is:** Flashing a new map without saving and verifying the current map first.

**How it happens:**
- Rushed troubleshooting
- Assuming the current map is already known / documented

**Consequence:** If new map is worse, you cannot roll back to the previous state. Current situation on this bike is partially the result of this.

**Rule:** No backup with verified SHA256 hash = no flash. Hard blocker. No override.

---

## Mistake 7: Changing Fuel and Ignition Simultaneously

**What it is:** Editing both fuel map and ignition timing map in the same flash operation.

**Why it's dangerous:**
- If something goes wrong, you cannot determine which change caused the problem
- Changes interact — a fuel change affects lambda, which affects whether timing is safe

**Rule:** One variable at a time. Tune, verify, log, then move to the next variable.

---

## Mistake 8: Skipping the Mechanical Pre-Check

**What it is:** Attempting to fix a running problem with ECU maps when the root cause is mechanical.

**Common examples:**
- Vacuum leak causing lean reading → add fuel in maps → vacuum leak gets worse → add more fuel → catastrophic map
- Weak fuel pump causing power loss at WOT → add WOT fuel → pump can't deliver it anyway → problem persists with corrupted maps
- Compression issue causing rough idle → adjust idle fuel endlessly → engine damage continues

**Rule:** Fix mechanical issues first. ECU maps cannot compensate for mechanical failures.

See [mechanical-pre-check.md](mechanical-pre-check.md).

---

## Recovery From Current Situation

The maps on this bike were corrupted using AI-generated values (ChatGPT). The correct recovery path is:

1. Complete mechanical pre-check first
2. Obtain known-good baseline map (OEM GP800 or SRV850 stock)
3. Validate the baseline map through the 5-stage validation pipeline
4. Flash baseline map with verified backup
5. Observe and verify basic operation
6. Only then begin incremental tuning if needed

Do not attempt to "tune around" the current corrupt maps. Start from stock.

---

## Related Files

- [tuning-workflow.md](tuning-workflow.md) — correct procedure
- [mechanical-pre-check.md](mechanical-pre-check.md) — required gates
- [bricked-ecu-recovery.md](bricked-ecu-recovery.md) — if ECU is in unrecoverable state
- [safe-ranges.json](../schemas/safe-ranges.json) — parameter hard limits

---

*TODO: Add additional examples from service forum research as they are encountered.*
