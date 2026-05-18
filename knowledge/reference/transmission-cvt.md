# Transmission, CVT & Drivetrain Reference

## Overview

The GP800 uses a continuously variable transmission (CVT) with a centrifugal wet clutch, followed by a cardan shaft (propshaft) and bevel gear final drive to the rear wheel. There is no manual clutch lever.

---

## CVT (Continuously Variable Transmission)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Type | Belt-drive CVT | Variator + clutch drum system |
| Clutch type | Centrifugal wet clutch | Engages automatically with RPM |
| CVT engagement RPM | ~3000–3500 RPM | Below this, clutch is disengaged |
| Idle RPM limit | 1100–1400 RPM | Must stay below CVT engagement RPM |

**If idle RPM exceeds ~1500 RPM:** clutch begins to drag → bike creeps forward → dangerous at stops.

### CVT Belt Inspection

| Check | Criteria |
|-------|----------|
| Width | Measure with calipers; replace if below minimum (TODO: spec from service manual) |
| Cracking | Any visible cracks = replace |
| Glazing | Shiny/hardened surface = replace |
| Burning | Burned smell or scorched appearance = replace |

Replace CVT belt as part of pre-check if condition is suspect. See [mechanical-pre-check.md](../procedures/mechanical-pre-check.md).

### Clutch Assessment

*Verified against GP800 i.e. Workshop Manual p.ENG-7 t/m ENG-13*

| Check | Criteria | Bron |
|-------|----------|------|
| Engagement RPM | Should engage cleanly at ~3000 RPM | |
| Clutch mass friction min. thickness | 1 mm | Verified WM ENG-8 |
| Clutch bell inside diameter max | 175.5 mm (std: 175 +0/+0.2 mm) | Verified WM ENG-7 |
| Clutch bell eccentricity max | 0.2 mm | Verified WM ENG-7 |
| Clutch spring standard length | 190.2 mm | Verified WM ENG-12 |
| Clutch spring min. length (worn) | 182 mm | Verified WM ENG-12 |
| Driven pulley bushing OD min | 54.91 mm (std: 55.00 -0.015/-0.035) | Verified WM ENG-10 |
| Driven pulley bushing ID max | 55.05 mm (std: 55.00 +0.035/0.00) | Verified WM ENG-10 |
| Clutch ring nut torque | 65–75 Nm | Verified WM ENG-13 |
| Drive pulley nut torque | 252–278 Nm | Verified WM Torque table |
| Driven pulley nut torque | 153–187 Nm | Verified WM Torque table |
| Clutch removal tool | 020659Y | Verified WM ENG-7 |
| Driven pulley grease | AGIP GREASE SM 2 (~10g) | Verified WM ENG-12 |

---

## Cardan Shaft (Propshaft)

The cardan shaft transfers power from the CVT output to the rear bevel gear. On this bike, the **cardan shaft was replaced by the owner** and the installation has not been independently verified.

| Check | What to Inspect |
|-------|----------------|
| Spline engagement | Correct depth and engagement at both ends |
| Lubrication | Splines greased with correct CV/spline grease |
| U-joint play | No excessive play in universal joints |
| Flange bolt torque | TODO: Torque spec from service manual |
| Balance | No vibration at speed |
| Output shaft seal | No gear oil leak from final drive seal |
| Backlash | Measure and compare to spec |

**Current status:** Cardan shaft replacement was owner-installed without documentation of source, specification, or alignment verification. Performance degradation observed after replacement. Requires inspection. See [modifications.md](../../my-bike/modifications.md).

---

## Final Drive (Bevel Gear)

| Parameter | Value |
|-----------|-------|
| Type | Bevel gear (hypoid) |
| Lubricant | SAE 80W-90 GL-5 |
| Capacity | ~150–200 mL (verify from service manual) |
| Drain/fill interval | TODO: From service manual |

**Check output shaft seal for leaks** before any sustained testing.

---

## Fluid Specifications Summary

| Fluid | Spec | Capacity |
|-------|------|----------|
| Final drive oil | SAE 80W-90 GL-5 | ~150–200 mL |

---

## Drivetrain and Tuning Interaction

- CVT engagement RPM (~3000–3500 RPM) is a critical threshold for recovery map strategy
- A recovery map must set the rev limiter above CVT engagement RPM to allow any movement
- Clutch issues (possible, unconfirmed) may mask or compound power delivery problems
- Cardan shaft vibration or incorrect ratio can make power delivery feel abnormal independent of ECU maps

---

## Related Files

- [mechanical-pre-check.md](../procedures/mechanical-pre-check.md) — cardan, CVT, clutch inspection checklist
- [modifications.md](../../my-bike/modifications.md) — cardan shaft replacement history
- [torque-specs.json](../schemas/torque-specs.json) — fastener torques

---

*TODO: Document CVT belt minimum width, clutch shoe minimum thickness, cardan flange torque, final drive oil capacity and interval from service manual.*
