# Tuning Workflow — Safe Incremental Map Tuning Procedure

## Overview

This workflow enforces the correct order for ECU map tuning on the IAW 5AM. Skipping steps or changing multiple variables simultaneously is the most common cause of tuning disasters.

**MANDATORY PREREQUISITE:** The [mechanical-pre-check.md](mechanical-pre-check.md) must be fully completed and all 14 points must pass before any ECU map work begins.

---

## Design Principles

- **Max 5% change per step** — 5% refers to injector pulse width (ms), not raw map value
- **One variable at a time** — never change fuel and ignition timing simultaneously
- **Always backup before flash** — verified backup with SHA256 hash must exist before any write
- **Rear cylinder runs hotter** — always tune rear slightly richer and with slightly less advance than front
- **Rollback instructions always prepared** — before any flash, know exactly how to undo it
- **Stock first** — when recovering from corrupted maps, flash stock/baseline first, tune from there

---

## Phase Overview

| Phase | Goal | When |
|-------|------|------|
| Pre-check | Verify mechanical baseline | Before any ECU work |
| Recovery | Get from broken to running | Current crisis phase |
| Idle | Stable idle, clean cold start | First tuning pass |
| Cruise | Part-throttle drivability | Second pass |
| Performance | WOT fueling, timing, rev limit | Final pass |

---

## Step 0: Injector Dead-Time Table (MUST DO FIRST)

**Before any fuel tuning, verify the injector dead-time table matches the installed injectors.**

The dead-time table corrects for the time the injector solenoid takes to open/close. An incorrect dead-time table will make ALL fuel map cells wrong by a fixed offset, especially at idle.

- Correct dead-time table = monotonically decreasing with battery voltage
- If table is not monotonically decreasing: DO NOT FLASH — table is corrupted
- Dead-time values must match the actual injectors fitted (12–16 Ohm high-impedance)

---

## Step 1: Idle Fuel — Front Cylinder

**Target:** Lambda 0.97–1.03 at idle (stoichiometric ±3%)

1. Flash baseline/stock map
2. Read live lambda at idle with IAW5xReader
3. If lambda >1.03 (lean): increase front idle fuel cells by max 5%
4. If lambda <0.97 (rich): decrease front idle fuel cells by max 5%
5. Flash, observe for 30 seconds, check exhaust color
6. Repeat until stable

---

## Step 2: Idle Fuel — Rear Cylinder

Same procedure as Step 1, applied to rear cylinder fuel map only.
Target: lambda 0.97–1.03. Rear cylinder may run slightly richer than front — acceptable.

---

## Step 3: Cold-Start Enrichment

**Target:** Engine starts within 3 cranks at 0–40°C ambient

- Tune cranking pulse width (injector open time during starter motor cranking) vs ECT
- Adjust in small increments
- Do not tune in hot weather; cold-start tuning requires cold engine

---

## Step 4: Warmup Enrichment Curve

**Target:** Smooth idle and no stalling from cold to operating temperature

- ECT-based fuel correction curve
- Reference: ~30% extra fuel at 0°C, tapering to 0% extra at 80°C
- Adjust if engine stalls or runs rough during warm-up

---

## Step 5: Cruise Fuel — Front Cylinder

**Target:** Lambda 0.97–1.03 at part-throttle cruise

- Work through fuel map cells at cruise RPM and load (typically 2000–4000 RPM, 30–50% throttle)
- Max 5% change per session
- Log lambda readings with each change

---

## Step 6: Cruise Fuel — Rear Cylinder

Same as Step 5 for rear cylinder. Rear runs hotter — acceptable to be 0.02–0.03 richer than front.

---

## Step 7: WOT Fuel — Front Cylinder

**Target:** Lambda 0.85–0.88 at WOT (slightly rich for power and protection)

- Only tune at WOT after idle and cruise are stable
- Hard limit: lambda must not exceed 1.05 at any WOT cell (dangerously lean)
- Hard limit: lambda must not go below 0.82 (catalyst destruction, fouling)

---

## Step 8: WOT Fuel — Rear Cylinder

Same as Step 7. Rear cylinder target: 0.02–0.03 richer than front (rear runs hotter, needs more protection).

---

## Step 9: Ignition Timing at Idle

**Target:** 10–14 deg BTDC at idle

- Start conservative (10 deg)
- Advance 1 degree at a time
- Listen for any pinging or knock
- Front and rear tuned independently

---

## Step 10: Ignition Timing at Cruise

- Advance for best torque
- Watch for knock (metallic pinging under load)
- Never advance both cylinders simultaneously — do front, then rear

---

## Step 11: Ignition Timing at WOT

- 1 degree at a time ONLY
- Rear: start 1–2 degrees more retarded than front
- Stop advancing at first sign of knock
- Do not exceed 45 deg BTDC (hard limit)

---

## Step 12: Throttle Body Sync Re-verification

After any idle changes, re-check throttle body synchronization with manometer. Sync changes as idle screw settings change.

---

## Step 13: Acceleration Enrichment

- Tune last — after all steady-state fuel and timing are stable
- Purpose: cure transient hesitation on quick throttle opening
- Small pulse of extra fuel when throttle opens quickly

---

## Step 14: Deceleration Fuel Cut-Off (DFCO)

- Verify thresholds: cut fuel at >1800 RPM with closed throttle
- Resume fuel at >1400 RPM
- Do not set cut RPM too high (engine braking too aggressive)

---

## Flash Safety Sequence (every time)

1. Verify backup file exists with known SHA256 hash
2. Confirm battery >12.0V
3. Connect IAW5xWriter
4. Read current ECU state (verify file size = expected)
5. Write new map
6. Read back and compare — verify write was successful
7. Have second person present for first start after any flash
8. Second person must have fire extinguisher

**Post-flash checklist (owner executes):**
1. Ignition ON, engine OFF: fuel pump primes? Dashboard normal? No new DTCs?
2. Start engine: idle within 1100–1400 RPM within 10 seconds?
3. 30-second observation: exhaust normal? No red glow? No flames?
4. **If ANY check fails: KILL ENGINE immediately → rollback**

---

## Abort Criteria (memorize before any flash)

Kill engine immediately if:
- Exhaust manifold begins glowing
- Flames from exhaust
- RPM oscillates wildly (>500 RPM swings)
- Unusual metallic pinging
- Stalling within first 30 seconds (do NOT restart)
- Coolant temperature past 3/4 mark within 2 minutes
- Excessive white/blue smoke or strong raw fuel smell

---

## Related Files

- [mechanical-pre-check.md](mechanical-pre-check.md) — must pass before this workflow
- [tuning-common-mistakes.md](tuning-common-mistakes.md) — what goes wrong
- [bricked-ecu-recovery.md](bricked-ecu-recovery.md) — if flash goes wrong
- [iaw5x-reader-writer.md](iaw5x-reader-writer.md) — tool usage
- [safe-ranges.json](../schemas/safe-ranges.json) — hard limits (authoritative)

---

*TODO: Add specific map cell coordinate instructions once map-definitions.json is fully populated with axis values.*
