# Engine Specifications — Gilera GP800

## Overview

The GP800 uses a longitudinally mounted, liquid-cooled V-twin shared across the Piaggio Group 850cc platform (GP800, Aprilia SRV850, Mana850, Dorsoduro850).

---

## Core Specifications

*Verified against GP800 i.e. Workshop Manual*

| Parameter | Value | Notes |
|-----------|-------|-------|
| Displacement | 839 cm³ | V-twin |
| Configuration | 90° V-twin | 4-stroke, double spark plug |
| Valve train | SOHC, 4 valves per cylinder | Single overhead camshaft |
| Spark plugs | NGK CR7EKB | 2 per cylinder, 4 total |
| Plug gap | 0.7–0.9 mm | Verified WM MAIN-4 |
| Bore x Stroke | 88 x 69 mm | Verified WM CHAR-5 |
| Compression ratio | 10.5 ± 0.5 : 1 | Requires 95 RON minimum |
| Peak power | 50.5 kW (68 HP) @ 7,750 RPM | Verified WM CHAR-5 |
| Peak torque | 71 Nm @ 4,500 RPM | Verified WM CHAR-5 |
| Idle RPM | 1,250 ± 100 RPM | Verified WM CHAR-5; >1500 causes clutch drag |
| Rev limiter | ~8,500 RPM stock | Do not exceed 9,500 RPM |
| Cooling | Forced liquid circulation | Radiator fan controlled by ECT sensor |
| Fuel | Unleaded 95 RON | Verified WM CHAR-5 |
| Throttle body | Ø 38 mm | Single throttle body, electronic injection |

---

## Fuel System

| Parameter | Value | Bron |
|-----------|-------|------|
| Fuel delivery | Multipoint EFI, Ø38mm throttle body | Verified WM |
| Fuel pressure | 3.0 bar | Verified WM CHAR-10 |
| Injector type | 4-hole, 24° nozzle cone, high-impedance | Verified WM CHAR-10 |
| Injector resistance | 13.7–15.2 Ohm | Verified WM CHAR-10 |
| Fuel grade | Unleaded 95 RON | Verified WM CHAR-5 |
| Fuel pump resistance | ~1.5 Ohm (winding) | Verified WM CHAR-10 |
| Fuel tank | ~14 L (reserve ~1.8 L) | Verified WM Capacities |

---

## Ignition System

| Parameter | Value | Bron |
|-----------|-------|------|
| Ignition type | High efficiency electronic inductive, variable advance | Verified WM |
| Spark plugs | NGK CR7EKB (x4, 2 per cylinder) | Verified WM CHAR-6 |
| Plug gap | 0.7–0.9 mm | Verified WM MAIN-4 |
| Ignition advance | 3D map managed by ECU | Verified WM CHAR-6 |
| Max ignition advance | 45 deg BTDC (hard limit) | safe-ranges.json |
| HV coil primary resistance | 520–620 mΩ | Verified WM CHAR-11 |
| HV coil secondary resistance | 6,830–7,830 Ω | Verified WM CHAR-11 |

---

## Lubrication

| Parameter | Value | Bron |
|-----------|-------|------|
| Oil type | 10W-40 JASO MA2 | |
| Oil capacity (without filter) | 2.5 L | Verified WM Capacities |
| Oil capacity (with filter) | 2.6 L | Verified WM Capacities |
| Oil pressure (normal) | 3.5–4.0 bar | Verified WM CHAR-5 |
| Min oil pressure @ 100°C | 0.8 bar | Verified WM CHAR-5 |
| Oil pressure sensor | Normally closed, activates at 0.3–0.6 bar | Verified WM CHAR-11 |
| Oil pump type | Trochoidal dry sump (delivery + scavenge) | Verified WM |

---

## Cooling System

| Parameter | Value | Bron |
|-----------|-------|------|
| Coolant type | AGIP PERMANENT SPEZIAL (ethylene glycol) | Verified WM |
| Coolant capacity (total system) | ~2.4 L | Verified WM Capacities |
| Thermostat | Automatic, parallel with radiator | Verified WM |
| Stator output | 3-phase AC, 450W | Verified WM CHAR-6 |
| Charging voltage | 14.0–14.7V @ 1,000–8,000 RPM | Verified WM |
| Battery | 12V / 14Ah, sealed | Verified WM CHAR-6 |

---

## Compression Test Reference

| Condition | Expected | Minimum Serviceable |
|-----------|----------|---------------------|
| Both cylinders | 11–14 bar (cold) | 10.5 bar |
| Max variance between cylinders | <10% | |

---

## Safety Limits (IAW 5AM Hard Limits)

| Parameter | Min | Max | Unit |
|-----------|-----|-----|------|
| Idle RPM | 1100 | 1500 | RPM |
| Rev limiter | 8000 | 9500 | RPM |
| Ignition advance | -10 | 45 | deg BTDC |
| Lambda target | 0.82 | 1.05 | lambda |
| Injector duration max | 0.5 | 12.0 | ms |

See [safe-ranges.json](../schemas/safe-ranges.json) for machine-readable limits (authoritative).

---

## Related Files

- [fuel-system.md](fuel-system.md) — injector, pump, and pressure details
- [ignition.md](ignition.md) — coil and spark plug details
- [sensor-reference.md](sensor-reference.md) — ECT, MAP, TPS sensor specs
- [platform-differences.md](platform-differences.md) — GP800 vs SRV850 differences

---

*Verified against GP800 i.e. Workshop Manual — May 2026. Remaining TODO: cardan flange torque, thermostat opening temperature.*
