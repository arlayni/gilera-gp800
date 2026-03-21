# Service & Maintenance — Intervals, Fluids, Common Issues

## Overview

Regular maintenance is critical before any diagnostic or tuning work. Several service items directly affect ECU tuning results (air filter, fuel filter, spark plugs, valve clearance).

Machine-readable maintenance schedule: [maintenance-schedule.json](../schemas/maintenance-schedule.json)

---

## Fluid Specifications

| Fluid | Specification | Capacity | Interval |
|-------|--------------|----------|---------|
| Engine oil | 10W-40 JASO MA2 | 3.5L with filter / 3.2L without | TODO: km interval from service manual |
| Coolant | 50/50 ethylene glycol / distilled water | 2.0–2.5L total / ~1.6L drain-refill | TODO: km/year interval |
| Brake fluid | DOT 4 | — | TODO: km/year interval |
| Final drive oil | SAE 80W-90 GL-5 | ~150–200 mL | TODO: km interval from service manual |
| CVT case | Dry — no oil; belt and variator only | — | Inspect at belt change |

---

## Spark Plugs

| Parameter | Value |
|-----------|-------|
| Type | NGK CR9EK |
| Quantity | 4 (2 per cylinder) |
| Replacement interval | TODO: From service manual |
| Gap | TODO: From service manual |
| Torque | TODO: From service manual |

**Note:** All four plugs should be replaced together. Inspect old plugs for color — light tan/gray = correct mixture; black/sooty = rich; white/ash = lean.

**Plug reading guide:**

| Plug Color | Interpretation |
|------------|---------------|
| Light tan or gray | Correct mixture and temperature |
| Black, sooty, wet | Rich — too much fuel |
| White or blistered | Lean — not enough fuel, or timing too advanced |
| Oily | Oil burning — ring or valve seal issue |
| Burned/melted electrode | Extreme lean or severe detonation |

---

## Service Intervals (TODO — populate from service manual)

| Service Item | Interval (km) | Interval (months) | Notes |
|-------------|---------------|--------------------|-------|
| Engine oil change | TODO | TODO | |
| Oil filter change | TODO | TODO | |
| Air filter clean/replace | TODO | TODO | Clean more often in dusty conditions |
| Fuel filter | TODO | TODO | |
| Spark plugs | TODO | TODO | |
| CVT belt | TODO | TODO | |
| Coolant change | TODO | TODO | |
| Final drive oil | TODO | TODO | |
| Brake fluid | TODO | TODO | |
| Valve clearance check | TODO | TODO | SOHC 4v — important for performance |
| Throttle body sync | After major work | — | |
| Brake pad inspection | TODO | TODO | |

---

## Valve Clearance

The GP800 uses SOHC with shim-under-bucket valves or similar (TODO: confirm exact type from service manual).

| Parameter | Inlet | Exhaust |
|-----------|-------|---------|
| Cold clearance | TODO | TODO |
| Hot clearance | TODO | TODO |

Incorrect valve clearance directly affects compression, which affects tuning. Check valve clearance before using compression test as a definitive baseline.

---

## Common Issues on GP800 / SRV850

### ECU and Electronics

| Issue | Description |
|-------|-------------|
| Side-stand switch failure | Can cause no-start or random stalling; caused original ECU replacement on this bike |
| Immobilizer communication | Intermittent no-start if antenna ring wiring degrades |
| Battery drain | Check for parasitic draw if battery repeatedly goes flat |

### Engine

| Issue | Description |
|-------|-------------|
| Oil consumption | Some consumption is normal for V-twin; blue smoke = excessive |
| Coolant loss | Check cap, hoses, and radiator; white exhaust smoke suggests head gasket |
| Rough idle when warm | May be valve clearance or throttle body sync |

### CVT and Drivetrain

| Issue | Description |
|-------|-------------|
| CVT belt wear | Belt slips or surging on acceleration; check belt width and condition |
| Clutch drag at idle | Idle RPM too high (>1500 RPM) causes clutch to partially engage |
| Cardan shaft noise | Worn U-joints or insufficient spline lubrication |
| Final drive oil seal leak | Inspect around output shaft |

### Fuel System

| Issue | Description |
|-------|-------------|
| Hard hot start | Normal fuel vaporization in hot intake; may also be TPS idle position |
| Power loss at WOT | Fuel filter, fuel pump weakness, or lean WOT maps |

---

## Pre-Ride Safety Checklist

Before any test ride after diagnostic or tuning work:

- [ ] All 14 points of [mechanical-pre-check.md](mechanical-pre-check.md) completed
- [ ] DTCs read and all critical codes resolved
- [ ] Exhaust color normal (no flames, no red glow)
- [ ] Idle stable within 1100–1400 RPM
- [ ] Battery charged
- [ ] No fuel leaks
- [ ] Second person present for first start after ECU flash
- [ ] Fire extinguisher accessible

---

## Related Files

- [mechanical-pre-check.md](mechanical-pre-check.md) — systematic pre-work inspection
- [maintenance-schedule.json](../schemas/maintenance-schedule.json) — machine-readable intervals
- [engine-specs.md](../reference/engine-specs.md) — fluid specs cross-reference
- [transmission-cvt.md](../reference/transmission-cvt.md) — CVT and final drive detail

---

*TODO: Complete all service intervals from GP800 or SRV850 service manual. Document valve clearance spec and adjustment procedure. Confirm final drive oil capacity.*
