# Engine Specifications — Gilera GP800

## Overview

The GP800 uses a longitudinally mounted, liquid-cooled V-twin shared across the Piaggio Group 850cc platform (GP800, Aprilia SRV850, Mana850, Dorsoduro850).

---

## Core Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Displacement | 839cc | V-twin |
| Configuration | 90° V-twin | Longitudinal mount |
| Valve train | SOHC, 4 valves per cylinder | Twin-spark heads |
| Spark plugs | 2 per cylinder, 4 total | NGK CR9EK |
| Bore | ~92mm | TODO: Confirm from service manual |
| Stroke | ~63mm | TODO: Confirm from service manual |
| Compression ratio | 10.5:1 | Requires 95 RON minimum |
| Peak power | 75 HP @ 7500 RPM | |
| Peak torque | 76 Nm @ 6000 RPM | |
| Idle RPM | 1100–1400 RPM | <1100 stalls; >1500 causes clutch drag |
| Rev limiter | ~8500 RPM stock | Do not exceed 9500 RPM |
| Cooling | Liquid cooled | Radiator fan controlled by ECT sensor |

---

## Fuel System

| Parameter | Value |
|-----------|-------|
| Fuel delivery | Electronic fuel injection (EFI) |
| Fuel pressure | 3.0–3.5 bar |
| Injector type | High-impedance |
| Injector resistance | 12–16 Ohm |
| Fuel grade | 95 RON minimum (premium unleaded) |

---

## Ignition System

| Parameter | Value |
|-----------|-------|
| Ignition type | Twin-spark (2 plugs/cylinder) |
| Spark plugs | NGK CR9EK (x4) |
| Plug gap | TODO: Confirm from service manual |
| Ignition timing at idle | 10–14 deg BTDC |
| Max ignition advance | 45 deg BTDC (hard limit) |

---

## Lubrication

| Parameter | Value |
|-----------|-------|
| Oil type | 10W-40 JASO MA2 |
| Oil capacity (with filter) | 3.5L |
| Oil capacity (without filter) | 3.2L |
| Oil pressure | TODO: Confirm from service manual |

---

## Cooling System

| Parameter | Value |
|-----------|-------|
| Coolant type | 50/50 ethylene glycol |
| Coolant capacity (total system) | 2.0–2.5L |
| Coolant capacity (drain-refill) | ~1.6L |
| Thermostat opening temp | TODO: Confirm from service manual |

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

*TODO: Cross-check displacement, bore, stroke, plug gap, oil pressure, and thermostat specs against service manual.*
