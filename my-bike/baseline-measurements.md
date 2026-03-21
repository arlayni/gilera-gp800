# Baseline Measurements & Diagnostics

**Date Created:** 2026-03-21
**Status:** MEASUREMENT TABLES EMPTY — TO BE COMPLETED

This document contains measurement tables for establishing baseline engine condition and sensor operation. These measurements are critical for diagnosing current issues and validating ECU map corrections.

## Compression Test

| Cylinder | Pressure (bar) | Notes |
|----------|----------------|-------|
| Front    | —              | Expected: 11–14 bar (cold engine) |
| Rear     | —              | Expected: 11–14 bar (cold engine) |

**Procedure:**
1. Remove spark plugs
2. Install compression tester in each plug hole
3. Crank engine 3–4 times with throttle wide open
4. Record peak pressure
5. Difference between cylinders should be <1 bar

**Interpretation:**
- If both cylinders <10 bar: possible ring wear, valve leak, or head gasket issue
- If one cylinder significantly lower: possible valve issue on that side

---

## Sensor Readings (ECU Diagnostics)

### Throttle Position Sensor (TPS)
| Condition | Voltage (V) | Notes |
|-----------|------------|-------|
| Idle      | —          | Expected: 0.5–1.0 V |
| 25% Open  | —          | Expected: 1.3–1.8 V |
| 50% Open  | —          | Expected: 2.1–2.6 V |
| 75% Open  | —          | Expected: 2.9–3.4 V |
| Full Open | —          | Expected: 3.5–4.5 V |

### Engine Coolant Temperature (ECT)
| Temperature (°C) | Resistance (Ω) | Voltage (V) | Notes |
|-----------------|----------------|-----------|-------|
| Cold (<20°C)    | —              | —         | Expected: ~2500–3000 Ω |
| Warm (80°C)     | —              | —         | Expected: ~200–300 Ω |
| Hot (100°C)     | —              | —         | Expected: ~100–150 Ω |

### Intake Air Temperature (IAT)
| Temperature (°C) | Resistance (Ω) | Voltage (V) | Notes |
|-----------------|----------------|-----------|-------|
| Ambient         | —              | —         | Expected: ~2000–3000 Ω |
| Cold Start      | —              | —         | Expected higher resistance in cool air |
| After Warm-up   | —              | —         | Expected lower resistance as air heats |

### Manifold Absolute Pressure (MAP)
| Condition | Pressure (kPa) | Voltage (V) | Notes |
|-----------|----------------|-----------|-------|
| Idle      | —              | —         | Expected: ~35–45 kPa at idle |
| 2000 RPM  | —              | —         | Expected: ~50–60 kPa |
| WOT       | —              | —         | Expected: ~95–105 kPa |

### Oxygen Sensor (O2/Lambda)
| Condition | Voltage (V) | Notes |
|-----------|-----------|-------|
| Rich (idle) | —        | Expected: 0.7–0.9 V (fuel-rich) |
| Lean | —            | Expected: 0.1–0.3 V (fuel-lean) |
| Closed Loop | —       | Expected: 0.4–0.6 V (alternating) |

---

## Fuel System Measurements

### Fuel Pressure

| Condition | Pressure (bar) | PSI | Notes |
|-----------|----------------|-----|-------|
| Key On, Engine Off | — | — | Expected: ~3.5–4.0 bar |
| Idle | — | — | Expected: ~3.5–4.0 bar |
| WOT | — | — | Expected: ~3.5–4.0 bar (regulated) |

**Procedure:**
1. Connect fuel pressure gauge to fuel rail test port
2. Measure with engine off (key on, fuel pump priming)
3. Measure at idle (1000 RPM)
4. Measure at 3000 RPM steady throttle

**Interpretation:**
- If pressure too high: faulty regulator, blocked return line
- If pressure too low: failing pump, loose connection, bad regulator
- If pressure fluctuates wildly: bad regulator or fuel pump issue

---

## Electrical Tests

### Battery & Charging

| Test | Voltage (V) | Notes |
|------|------------|-------|
| Battery at rest (engine off) | — | Expected: ~12.6–12.8 V |
| Battery loaded (cranking) | — | Expected: >10.5 V (should not drop below) |
| Charging at idle | — | Expected: ~13.5–14.2 V |
| Charging at 3000 RPM | — | Expected: ~13.8–14.5 V |

### Ground Connections

| Location | Resistance (Ω) | Notes |
|----------|----------------|-------|
| Battery negative to engine block | — | Expected: <0.1 Ω |
| Battery negative to frame | — | Expected: <0.1 Ω |
| ECU ground pin 1 | — | Expected: <0.1 Ω |
| ECU ground pin 2 | — | Expected: <0.1 Ω |

### Ignition Coil(s) Resistance

| Measurement | Resistance (Ω) | Notes |
|------------|----------------|-------|
| Primary winding (front) | — | Expected: ~0.5–3.0 Ω |
| Primary winding (rear) | — | Expected: ~0.5–3.0 Ω |
| Secondary winding (front) | — | Expected: ~6000–12000 Ω |
| Secondary winding (rear) | — | Expected: ~6000–12000 Ω |

### Fuel Injector Resistance

| Injector | Resistance (Ω) | Notes |
|----------|----------------|-------|
| Front | — | Expected: ~12–14 Ω (high-impedance) |
| Rear | — | Expected: ~12–14 Ω (high-impedance) |

---

## Notes & Observations

**Space for additional measurements or findings:**

```
[To be filled during diagnostics]
```

---

**Last Updated:** 2026-03-21
**Measurements By:** [To be completed]
