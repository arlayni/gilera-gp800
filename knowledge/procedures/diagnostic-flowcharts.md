# Diagnostic Flowcharts — Symptom Decision Trees

## How to Use

1. Start with **structured symptom intake** (section below)
2. Find the matching symptom flowchart
3. Follow branches in order — do not skip steps
4. Fix mechanical issues before touching ECU maps
5. Re-diagnose after each fix before moving to the next

**Mandatory first step:** Read all active DTCs via IAW5xReader before proceeding. See [obd-diagnostics.md](obd-diagnostics.md).

---

## Structured Symptom Intake

Before any diagnostic work, record the following:

1. **What exactly happens?** (describe the symptom precisely)
2. **When does it occur?** (cold start / warm / always / only at certain RPM or throttle)
3. **What was changed recently?** (maps, parts, wiring, anything)
4. **Current state:** Can it start? Does the MIL light come on? Can it idle?

---

## Flowchart 1: Rough Idle

```
Rough idle / unstable idle
    |
    ├─ Read DTCs → Code 14 (TPS)? → Test TPS voltage sweep → repair/replace if bad
    |
    ├─ Code 32 (IAC)? → Test IAC circuit → repair/replace if bad
    |
    ├─ Check throttle body sync → re-sync with manometer if unbalanced
    |
    ├─ Check for vacuum leaks → spray carb cleaner at intake boots (RPM change = leak)
    |
    ├─ Check idle RPM target in ECU → should be 1100–1400 RPM
    |
    ├─ Check MAP sensor (Code 13?) → test voltage at idle (~1.0V expected)
    |
    ├─ Check ECT sensor (Code 11?) → if open circuit, ECU over-enriches cold-start
    |
    └─ If all above pass → suspect fuel map corruption → read and analyze fuel maps
```

---

## Flowchart 2: Power Loss at Full Throttle

```
Power loss / cuts out at WOT after 2 minutes
    |
    ├─ Read DTCs first
    |
    ├─ Fuel pressure under load? → measure at 3000 RPM sustained → should be 3.0–3.5 bar
    |   ├─ Low pressure → failing pump or blocked filter → fix mechanically
    |
    ├─ Fuel filter blocked? → replace fuel filter
    |
    ├─ WOT fuel map too lean? → lambda sensor reading, AFR at WOT
    |
    ├─ Rev limiter too low in maps? → check rev limit setting in ECU
    |
    ├─ Ignition coil breaking down under heat? → coil resistance normal cold but fails hot
    |
    ├─ CVT slip at high load? → CVT belt inspection
    |
    └─ If no mechanical cause → analyze fuel and ignition maps at high RPM/load cells
```

---

## Flowchart 3: Red-Hot Exhaust / Exhaust Glowing

**SAFETY: Red-hot exhaust = fire risk. Do not ride. Kill engine immediately if observed.**

```
Red exhaust manifold or exhaust glowing
    |
    ├─ KILL ENGINE immediately
    |
    ├─ This indicates: unburned fuel reaching exhaust (rich/misfiring) OR
    |                  extreme ignition retard pushing combustion into exhaust stroke
    |
    ├─ Read DTCs → prioritize: Code 24/25 (ignition coils), Code 22/23 (injectors)
    |
    ├─ Check compression → both cylinders should be 11–14 bar
    |   ├─ Low compression → mechanical repair required BEFORE ECU work
    |
    ├─ Check ignition timing in maps → look for extreme retard values (<0 deg BTDC)
    |
    ├─ Check fuel maps → look for extreme richness (all-255 or very high values at idle)
    |
    ├─ Check exhaust for leaks → exhaust gas escaping at manifold can glow nearby metal
    |
    └─ Do NOT ride until resolved. Consult [bricked-ecu-recovery.md](bricked-ecu-recovery.md) if maps are confirmed corrupt.
```

---

## Flowchart 4: Stalling (at Idle / Traffic Lights)

```
Stalling at idle or traffic lights
    |
    ├─ Read DTCs first
    |
    ├─ Code 42 (side-stand switch)? → test switch continuity → if deployed stand = engine cut
    |
    ├─ Code 44 (immobilizer)? → intermittent immobilizer fault → check antenna ring wiring
    |
    ├─ Code 32 (IAC)? → idle control issue → test IAC
    |
    ├─ Idle RPM set too low? → if idle < 1100 RPM → ECU target may be wrong
    |
    ├─ TPS idle position learned? → perform TPS reset/learn if recently disconnected battery
    |
    ├─ Vacuum leak? → unstable idle that dips below stall threshold
    |
    ├─ Fuel pressure low at idle? → check pump and regulator
    |
    └─ If all mechanical checks pass → suspect idle fuel map corruption
```

---

## Flowchart 5: Flames from Exhaust

**SAFETY: Flames from exhaust = active fire risk. Kill engine immediately. Have fire extinguisher ready.**

```
Flames from exhaust
    |
    ├─ KILL ENGINE
    |
    ├─ This is unburned fuel igniting in exhaust — classic lean misfire + rich maps combination
    |   OR extreme ignition retard
    |
    ├─ Do NOT restart without understanding the cause
    |
    ├─ Same root causes as red exhaust — follow Flowchart 3
    |
    ├─ Check: Was the ECU recently reflashed? → if yes, the new maps are the likely cause
    |
    ├─ Verify: Is a known-good backup map available? → flash it via IAW5xWriter
    |
    └─ If no good backup → see [bricked-ecu-recovery.md](bricked-ecu-recovery.md) for recovery strategy
```

---

## Post-Diagnosis Decision

After completing diagnostic flowcharts:

- **Mechanical fault found** → fix it → re-run compression and sensor checks → then and only then consider ECU maps
- **ECU maps confirmed corrupt** → obtain baseline/stock map → validate with safety checks → flash
- **Immobilizer issue** → resolve before any other work (immobilizer can mask other faults)
- **Multiple faults** → fix in order: safety systems → mechanical → sensors → ECU maps

---

## Related Files

- [sensor-reference.md](../reference/sensor-reference.md) — sensor test procedures
- [mechanical-pre-check.md](mechanical-pre-check.md) — systematic mechanical inspection
- [error-codes.md](../reference/error-codes.md) — DTC meanings
- [exhaust-diagnostics.md](exhaust-diagnostics.md) — exhaust color interpretation
- [obd-diagnostics.md](obd-diagnostics.md) — how to read DTCs with IAW5xReader

---

*TODO: Expand flowcharts with more branch detail once service manual data is available. Add specific multimeter readings at each decision point.*
