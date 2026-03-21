# Fuel System Reference

## Overview

The GP800 uses a sequential electronic fuel injection (EFI) system managed by the IAW 5AM ECU. Each cylinder has one high-impedance injector. Fuel pressure is regulated to a constant 3.0–3.5 bar.

---

## Fuel Pressure

| Condition | Expected Pressure | Notes |
|-----------|-------------------|-------|
| Key on, engine off (pump prime) | 3.5–4.0 bar | Pump runs ~2s on key-on |
| Idle | 3.0–3.5 bar | Regulated |
| WOT | 3.0–3.5 bar | Regulated (constant pressure system) |

**If pressure too high:** faulty regulator, blocked return line
**If pressure too low:** failing pump, loose connection, bad regulator
**If pressure fluctuates:** bad regulator or failing fuel pump

---

## Injectors

| Parameter | Value | Notes |
|-----------|-------|-------|
| Type | High-impedance (saturated) | Do NOT use peak-and-hold driver |
| Resistance | 12–16 Ohm | Measure across pins with harness disconnected |
| Count | 2 (one per cylinder) | |
| Cylinder numbering | Front = cylinder 1, Rear = cylinder 2 | Rear runs hotter |
| Max pulse width | 12.0 ms | >12ms risks hydro-lock |
| Min pulse width | 0.5 ms | |

**Injector testing (multimeter):**
1. Disconnect injector harness connector
2. Measure resistance across the two pins
3. 12–16 Ohm = serviceable
4. <1 Ohm = short circuit (replace)
5. OL/infinite = open circuit (replace)

---

## Fuel Pump

| Parameter | Value |
|-----------|-------|
| Location | In-tank (submersible) |
| Activation | Relay controlled by ECU |
| Prime sequence | Runs ~2 seconds on key-on before starting |
| DTC | Code 31 = fuel pump relay circuit fault |

---

## Throttle Body & Idle Control

| Parameter | Value |
|-----------|-------|
| Configuration | Two throttle bodies (one per cylinder) |
| Idle speed control | Idle air control (IAC) valve or stepper motor |
| DTC | Code 32 = IAC circuit fault |
| Target idle RPM | 1100–1400 RPM |

**Throttle body synchronization** must be performed with a manometer after any idle adjustments. See [mechanical-pre-check.md](../procedures/mechanical-pre-check.md).

---

## Lambda / Oxygen Sensor

| Parameter | Value |
|-----------|-------|
| Type | Narrowband heated lambda sensor |
| Location | Exhaust, before or at catalyst |
| Heater resistance | 2–15 Ohm |
| Signal: rich | 0.7–0.9V |
| Signal: lean | 0.1–0.3V |
| Signal: closed loop oscillation | 0.4–0.6V (switching) |
| DTC | Code 21 = O2 sensor no activity or heater fault |

---

## Air Filter

- Clean or replace before any tuning work
- Blocked air filter causes rich running — address mechanically, not via maps

---

## Fuel Filter

- Restricted fuel filter starves the engine under load (power loss at WOT)
- Inspect or replace as part of pre-check — see [mechanical-pre-check.md](../procedures/mechanical-pre-check.md)

---

## Diagnostic Reference

See [diagnostic-flowcharts.md](../procedures/diagnostic-flowcharts.md) for fuel-related symptom trees.

**Key DTCs:**
- Code 22 — Injector 1 (front) open/short
- Code 23 — Injector 2 (rear) open/short
- Code 31 — Fuel pump relay circuit

---

## Related Files

- [engine-specs.md](engine-specs.md) — compression and operating limits
- [sensor-reference.md](sensor-reference.md) — TPS, MAP, lambda sensor specs
- [safe-ranges.json](../schemas/safe-ranges.json) — injector pulse width limits (authoritative)

---

*TODO: Confirm fuel pressure spec (3.0–3.5 bar vs 3.5–4.0 bar at prime) from service manual. Document injector flow rate (cc/min) — needed for TuningAdvisor scaling calculations.*
