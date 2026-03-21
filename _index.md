# Gilera GP800 Knowledge Base — Master Index

**Bike:** Gilera GP800 with Aprilia SRV850 ECU (IAW 5AM)
**Status:** Maps scrambled — recovery in progress
**Safety:** DO NOT RIDE — Severity 5 fire risk (red-hot exhaust, flames, rough idle)

---

## My Bike

Live state, measurements, and history for this specific machine.

| File | Description |
|------|-------------|
| [current-state.md](my-bike/current-state.md) | Active symptoms, root cause assessment, safety status |
| [baseline-measurements.md](my-bike/baseline-measurements.md) | Sensor and compression measurement tables (to be filled) |
| [history.md](my-bike/history.md) | Ownership timeline and event log |
| [modifications.md](my-bike/modifications.md) | All deviations from stock GP800 configuration |
| [srv850-to-gp800-wiring.md](my-bike/srv850-to-gp800-wiring.md) | SRV850 ECU wiring integration investigation checklist |

---

## Reference

Static technical facts — engine, ECU, sensors, platform differences.

| File | Description |
|------|-------------|
| [engine-specs.md](knowledge/reference/engine-specs.md) | V-twin 839cc, 75HP, 76Nm, SOHC 4v/cyl, twin-spark |
| [ecu-iaw5am.md](knowledge/reference/ecu-iaw5am.md) | IAW 5AM architecture, K-Line protocol, memory layout |
| [fuel-system.md](knowledge/reference/fuel-system.md) | EFI, injectors, fuel pressure, TPS, lambda |
| [ignition.md](knowledge/reference/ignition.md) | Twin-spark system, coils, NGK CR9EK plugs, timing |
| [transmission-cvt.md](knowledge/reference/transmission-cvt.md) | CVT, centrifugal clutch, cardan shaft, final drive |
| [electrical.md](knowledge/reference/electrical.md) | Immobilizer, side-stand switch, K-Line, wiring |
| [platform-differences.md](knowledge/reference/platform-differences.md) | GP800 vs SRV850 — ABS, immobilizer, calibration, dashboard |
| [error-codes.md](knowledge/reference/error-codes.md) | IAW 5AM DTC list, MIL blink code procedure |
| [sensor-reference.md](knowledge/reference/sensor-reference.md) | All sensors with test values and multimeter procedures |

---

## Procedures

Step-by-step workflows — diagnostics, tuning, recovery, maintenance.

| File | Description |
|------|-------------|
| [diagnostic-flowcharts.md](knowledge/procedures/diagnostic-flowcharts.md) | Symptom decision trees (rough idle, power loss, red exhaust, stalling, flames) |
| [tuning-workflow.md](knowledge/procedures/tuning-workflow.md) | 12-step enforced tuning order with safety gates |
| [tuning-common-mistakes.md](knowledge/procedures/tuning-common-mistakes.md) | What goes wrong, symptoms, and corrections |
| [mechanical-pre-check.md](knowledge/procedures/mechanical-pre-check.md) | 14-point gate that must pass before any ECU work |
| [bricked-ecu-recovery.md](knowledge/procedures/bricked-ecu-recovery.md) | BDM/boot mode recovery, when to call a professional |
| [iaw5x-reader-writer.md](knowledge/procedures/iaw5x-reader-writer.md) | IAW5xReader/Writer tool usage — read, write, export |
| [obd-diagnostics.md](knowledge/procedures/obd-diagnostics.md) | NOT standard OBD2 — Piaggio/K-Line protocol and compatible tools |
| [exhaust-diagnostics.md](knowledge/procedures/exhaust-diagnostics.md) | Reading exhaust color, temperature, flames, and smoke |
| [service-maintenance.md](knowledge/procedures/service-maintenance.md) | Service intervals, fluid specs, common issues |

---

## Schemas

JSON files — runtime authority for all parameter limits, sensor specs, and definitions.
These are the single source of truth; spec tables in markdown are illustrative only.

| File | Description |
|------|-------------|
| [safe-ranges.json](knowledge/schemas/safe-ranges.json) | Per-parameter min/max/danger thresholds for tuning and flashing |
| [map-definitions.json](knowledge/schemas/map-definitions.json) | Map names, axes, units, and dimensions |
| [sensor-specs.json](knowledge/schemas/sensor-specs.json) | Sensor voltages, resistances, and thresholds |
| [error-codes.json](knowledge/schemas/error-codes.json) | IAW 5AM DTCs — machine-readable |
| [immobilizer.json](knowledge/schemas/immobilizer.json) | Immobilizer system data (REDACTED — key codes never shared) |
| [platform-spec.json](knowledge/schemas/platform-spec.json) | GP800 and SRV850 platform comparison |
| [maintenance-schedule.json](knowledge/schemas/maintenance-schedule.json) | Service intervals and fluid specifications |
| [parts-compatibility.json](knowledge/schemas/parts-compatibility.json) | Cross-reference: GP800, SRV850, Mana850, Dorsoduro850 |
| [wiring.json](knowledge/schemas/wiring.json) | Connector pinouts, signal names, wire colors |
| [torque-specs.json](knowledge/schemas/torque-specs.json) | Fastener torque values |
| [hardware-delta.schema.json](knowledge/schemas/hardware-delta.schema.json) | Schema for GP800 vs SRV850 hardware differences |
| [diagnostic-report.schema.json](knowledge/schemas/diagnostic-report.schema.json) | Schema for inter-agent diagnostic reports |
| [changelog-entry.schema.json](knowledge/schemas/changelog-entry.schema.json) | Schema for tracking map and configuration changes |

---

## Map Files

ECU map file storage — organized by state.

| Directory | Description |
|-----------|-------------|
| [map-files/original/](map-files/original/) | Original unmodified dumps from ECU |
| [map-files/stock/](map-files/stock/) | OEM stock maps for GP800 and SRV850 |
| [map-files/working/](map-files/working/) | Current working copies being analyzed or edited |
| [map-files/modified/](map-files/modified/) | Modified maps with change records |

---

## Design Documents

| File | Description |
|------|-------------|
| [Expert Agent System Design Spec](docs/superpowers/specs/2026-03-21-gilera-gp800-expert-agent-design.md) | Full system architecture, agent specifications, safety rules |
| [Knowledge Base Foundation Plan](docs/superpowers/plans/2026-03-21-knowledge-base-foundation.md) | Task plan for building this knowledge base |

---

*Last updated: 2026-03-21*
