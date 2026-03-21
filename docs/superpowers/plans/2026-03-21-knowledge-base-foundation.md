# Knowledge Base Foundation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the complete directory structure, JSON schemas, and markdown knowledge files that serve as the foundation for the Gilera GP800 Expert Agent System.

**Architecture:** Flat file knowledge base using markdown for human-readable content and JSON for machine-readable schemas. The `schemas/` directory is the single source of truth — CLI tool and Claude Code skill both read from it at runtime. Git tracks all changes.

**Tech Stack:** Markdown, JSON, Git

**Spec:** `docs/superpowers/specs/2026-03-21-gilera-gp800-expert-agent-design.md`

**Related plans:**
- Plan 2: `2026-03-21-cli-tool-gp800.md` (Python CLI tool — depends on this plan)
- Plan 3: `2026-03-21-claude-skill-gp800-expert.md` (Claude Code skill — depends on plans 1+2)

---

## File Structure

```
Gilera GP800/
├── _index.md                              # Master cross-reference and entry point
├── .gitignore                             # Exclude sensitive data
├── knowledge/
│   ├── reference/
│   │   ├── engine-specs.md
│   │   ├── ecu-iaw5am.md
│   │   ├── fuel-system.md
│   │   ├── ignition.md
│   │   ├── transmission-cvt.md
│   │   ├── electrical.md
│   │   ├── platform-differences.md
│   │   ├── error-codes.md
│   │   └── sensor-reference.md
│   ├── procedures/
│   │   ├── diagnostic-flowcharts.md
│   │   ├── tuning-workflow.md
│   │   ├── tuning-common-mistakes.md
│   │   ├── mechanical-pre-check.md
│   │   ├── bricked-ecu-recovery.md
│   │   ├── iaw5x-reader-writer.md
│   │   ├── obd-diagnostics.md
│   │   ├── exhaust-diagnostics.md
│   │   └── service-maintenance.md
│   └── schemas/
│       ├── safe-ranges.json
│       ├── map-definitions.json
│       ├── sensor-specs.json
│       ├── error-codes.json
│       ├── maintenance-schedule.json
│       ├── platform-spec.json
│       ├── wiring.json
│       ├── torque-specs.json
│       ├── immobilizer.json
│       ├── parts-compatibility.json
│       ├── diagnostic-report.schema.json
│       ├── hardware-delta.schema.json
│       └── changelog-entry.schema.json
├── my-bike/
│   ├── history.md
│   ├── current-state.md
│   ├── modifications.md
│   ├── srv850-to-gp800-wiring.md
│   └── baseline-measurements.md
├── map-files/
│   ├── original/
│   ├── modified/
│   ├── working/
│   └── stock/
└── gp800-tool/                            # (created in Plan 2)
```

---

### Task 1: Initialize Git Repository and Directory Scaffold

**Files:**
- Create: `.gitignore`
- Create: All directories listed above (empty)

- [ ] **Step 1: Initialize git repo**

```bash
cd "C:/Users/arlay/Desktop/Gilera GP800"
git init
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Sensitive data
my-bike/immobilizer-keys/
*.key
*.pin

# OS files
Thumbs.db
.DS_Store

# Python (for CLI tool later)
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/

# Temp files
*.tmp
*.bak
```

- [ ] **Step 3: Create all directories**

```bash
mkdir -p knowledge/reference knowledge/procedures knowledge/schemas
mkdir -p my-bike map-files/original map-files/modified map-files/working map-files/stock
mkdir -p gp800-tool
```

- [ ] **Step 4: Create .gitkeep files in empty directories**

```bash
touch map-files/original/.gitkeep map-files/modified/.gitkeep map-files/working/.gitkeep map-files/stock/.gitkeep
touch gp800-tool/.gitkeep
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore knowledge/ my-bike/ map-files/ gp800-tool/
git commit -m "feat: initialize project directory structure for GP800 Expert Agent System"
```

---

### Task 2: Create Core JSON Schemas — Safety Ranges

**Files:**
- Create: `knowledge/schemas/safe-ranges.json`

This is the MOST IMPORTANT file — it's the single source of truth for all safety validation.

- [ ] **Step 1: Create safe-ranges.json**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "IAW 5AM safety ranges — single source of truth for CLI tool and Claude Code skill",
  "version": "1.0.0",
  "last_updated": "2026-03-21",
  "parameters": {
    "fuel_map_value": {
      "unit": "raw",
      "hard_limits": { "min": 0, "max": 255 },
      "tuning_guidance": { "max_change_percent": 15 },
      "flash_blockers": ["all_zero_row", "all_255_row"],
      "notes": "TODO: Confirm 8-bit vs 16-bit from actual ECU dump"
    },
    "ignition_advance": {
      "unit": "deg_btdc",
      "hard_limits": { "min": -10, "max": 45 },
      "tuning_guidance": { "max_change_from_stock_deg": 3, "max_advance_over_stock_high_load_deg": 5 },
      "flash_blockers": ["below_min", "above_max"],
      "notes": ">40 deg risks detonation on 95 RON fuel"
    },
    "idle_rpm": {
      "unit": "rpm",
      "hard_limits": { "min": 1100, "max": 1500 },
      "tuning_guidance": { "target_warm": 1200, "acceptable_range": [1100, 1400] },
      "notes": "<1100 stalls; >1500 causes clutch drag"
    },
    "rev_limiter": {
      "unit": "rpm",
      "hard_limits": { "min": 8000, "max": 9500 },
      "tuning_guidance": { "stock": 8500 },
      "flash_blockers": ["above_max"],
      "notes": ">9500 risks valve float on stock internals"
    },
    "lambda_target": {
      "unit": "lambda",
      "hard_limits": { "min": 0.82, "max": 1.05 },
      "tuning_guidance": {
        "idle": { "target": 1.0, "range": [0.97, 1.03] },
        "cruise": { "target": 1.0, "range": [0.97, 1.03] },
        "wot": { "target": 0.86, "range": [0.85, 0.88] },
        "wot_rear_cylinder_offset": -0.02
      },
      "flash_blockers": ["below_min", "above_max_at_wot"],
      "notes": "<0.82 fouling/catalyst destruction; >1.05 lean misfire/piston damage"
    },
    "injector_duration": {
      "unit": "ms",
      "hard_limits": { "min": 0.5, "max": 12.0 },
      "notes": ">12ms hydro-lock risk"
    },
    "injector_dead_time": {
      "unit": "ms",
      "validation": "must_be_monotonically_decreasing_with_voltage",
      "typical_at_14v": { "min": 0.5, "max": 3.0 },
      "typical_at_8v": { "min": 1.0, "max": 6.0 },
      "flash_blockers": ["not_monotonic"]
    },
    "battery_voltage_for_flash": {
      "unit": "volts",
      "hard_limits": { "min": 12.0 },
      "notes": "Below 12V risks corrupted flash write"
    }
  },
  "tuning_rules": {
    "max_single_step_percent": 5,
    "injector_flow_scaling": "max_raw_change = max_step% * (stock_flow / actual_flow)",
    "one_variable_at_a_time": true,
    "cylinder_order": "front_first_then_rear",
    "rear_cylinder_offset": {
      "fuel": "0.02-0.03 lambda richer than front",
      "timing": "1-2 deg more retarded than front"
    }
  }
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('knowledge/schemas/safe-ranges.json'))"
```
Expected: no output (valid JSON)

- [ ] **Step 3: Commit**

```bash
git add knowledge/schemas/safe-ranges.json
git commit -m "feat: add safe-ranges.json — core safety validation schema"
```

---

### Task 3: Create Sensor Specs Schema

**Files:**
- Create: `knowledge/schemas/sensor-specs.json`

- [ ] **Step 1: Create sensor-specs.json**

```json
{
  "description": "IAW 5AM sensor specifications for the GP800/SRV850 platform",
  "version": "1.0.0",
  "sensors": {
    "tps": {
      "name": "Throttle Position Sensor",
      "type": "potentiometer",
      "wires": 3,
      "test": "DC Volts backprobe",
      "expected": { "closed": 0.5, "wot": 4.5, "unit": "V" },
      "resistance": { "sweep": "1-5 kOhm", "no_dropouts": true },
      "failure_mode": "wear spot at idle position causes erratic idle",
      "notes": "Verify GP800 TPS matches SRV850 ECU expected range"
    },
    "map": {
      "name": "Manifold Absolute Pressure",
      "type": "piezo-resistive",
      "wires": 3,
      "test": "DC Volts",
      "expected": { "key_on_engine_off": 4.0, "idle": 1.0, "unit": "V" },
      "failure_mode": "cracked vacuum hose, corroded connector"
    },
    "iat": {
      "name": "Intake Air Temperature",
      "type": "NTC thermistor",
      "wires": 2,
      "test": "Ohms",
      "expected": { "at_20c": 2500, "at_80c": 400, "unit": "ohm" },
      "voltage": { "at_20c": 3.0, "at_80c": 1.0, "unit": "V" },
      "failure_mode": "open circuit = ECU sees -40C = runs very rich"
    },
    "ect": {
      "name": "Engine Coolant Temperature",
      "type": "NTC thermistor",
      "wires": 2,
      "test": "Ohms",
      "expected": { "at_20c": 2500, "at_90c": 300, "unit": "ohm" },
      "voltage": { "at_20c": 3.2, "at_90c": 0.6, "unit": "V" },
      "failure_mode": "incorrect reading causes permanent cold-start enrichment"
    },
    "ckp": {
      "name": "Crankshaft Position Sensor",
      "type": "VR inductive (variable reluctance)",
      "wires": 2,
      "test": "Ohms and AC mV",
      "expected": { "resistance": { "min": 200, "max": 400, "unit": "ohm" }, "cranking_ac": { "min": 200, "unit": "mV" } },
      "air_gap": "0.5-1.5mm",
      "signal": "AC sine wave, amplitude increases with RPM",
      "failure_mode": "intermittent connection, metallic debris on tip"
    },
    "cmp": {
      "name": "Camshaft Position Sensor",
      "status": "TODO: Confirm if GP800/SRV850 uses CMP or CKP-only cylinder ID",
      "notes": "If present: Hall-effect 3-wire, toggles 0-5V while cranking"
    },
    "o2": {
      "name": "Oxygen / Lambda Sensor",
      "type": "narrowband zirconia, heated",
      "wires": 4,
      "test_heater": { "resistance": { "min": 2, "max": 15, "unit": "ohm" } },
      "test_signal": { "oscillation": "0.1-0.9V at 1-3 Hz", "stuck_high": "rich", "stuck_low": "lean" },
      "failure_mode": "slow switching >3s/cycle = lazy sensor"
    },
    "injector": {
      "name": "Fuel Injector",
      "type": "high-impedance electromagnetic",
      "test": "Ohms",
      "expected": { "min": 12, "max": 16, "unit": "ohm" },
      "match_tolerance": "both injectors within 1 ohm",
      "notes": "Verify GP800 vs SRV850 injector part numbers and flow rates"
    },
    "coil_primary": {
      "name": "Ignition Coil Primary",
      "test": "Ohms",
      "expected": { "min": 0.5, "max": 2.0, "unit": "ohm" },
      "notes": "Both cylinders must match. Check resistance cold vs hot for heat breakdown"
    },
    "coil_secondary": {
      "name": "Ignition Coil Secondary",
      "test": "Ohms (20k range)",
      "expected": { "min": 5000, "max": 15000, "unit": "ohm" }
    },
    "battery": {
      "name": "Battery",
      "tests": {
        "resting": { "min": 12.4, "unit": "V" },
        "cranking": { "min": 10.5, "unit": "V" },
        "charging_idle": { "min": 13.5, "max": 14.5, "unit": "V" }
      }
    },
    "fuel_pressure": {
      "name": "Fuel System Pressure",
      "test": "inline gauge",
      "expected": { "key_on": { "min": 3.0, "max": 3.5, "unit": "bar" }, "idle": 3.0 },
      "notes": "Must hold under sustained WOT load"
    },
    "idle_stepper": {
      "name": "Idle Air Control Stepper Motor",
      "type": "4-wire bipolar stepper",
      "test": "Ohms per winding",
      "expected": { "min": 40, "max": 60, "unit": "ohm" }
    }
  }
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('knowledge/schemas/sensor-specs.json'))"
```

- [ ] **Step 3: Commit**

```bash
git add knowledge/schemas/sensor-specs.json
git commit -m "feat: add sensor-specs.json with all IAW 5AM sensor test values"
```

---

### Task 4: Create Error Codes Schema

**Files:**
- Create: `knowledge/schemas/error-codes.json`

- [ ] **Step 1: Create error-codes.json**

```json
{
  "description": "IAW 5AM Diagnostic Trouble Codes — partial list, expand from IAW5xReader output",
  "version": "1.0.0",
  "reading_method": "MIL blink code: key ON, within 3s fully open/close throttle 3 times. Long flash = tens, short = units.",
  "codes": {
    "11": { "description": "ECT sensor open/short", "system": "cooling", "severity": "high", "symptoms": ["rich running", "no fan activation", "wrong cold-start enrichment"] },
    "12": { "description": "IAT sensor open/short", "system": "intake", "severity": "high", "symptoms": ["rich running if open circuit (ECU sees -40C)"] },
    "13": { "description": "MAP sensor out of range", "system": "intake", "severity": "high", "symptoms": ["wrong fueling at all RPM/load points"] },
    "14": { "description": "TPS out of range / implausible", "system": "throttle", "severity": "critical", "symptoms": ["erratic idle", "unpredictable fueling"] },
    "15": { "description": "Battery voltage out of range", "system": "electrical", "severity": "medium", "symptoms": ["injector dead-time errors", "weak spark"] },
    "21": { "description": "O2 sensor no activity / heater circuit", "system": "exhaust", "severity": "medium", "symptoms": ["no closed-loop correction", "stuck rich or lean at cruise"] },
    "22": { "description": "Injector 1 open/short", "system": "fuel", "severity": "critical", "symptoms": ["cylinder 1 misfire or no fuel"] },
    "23": { "description": "Injector 2 open/short", "system": "fuel", "severity": "critical", "symptoms": ["cylinder 2 misfire or no fuel"] },
    "24": { "description": "Ignition coil 1 primary circuit", "system": "ignition", "severity": "critical", "symptoms": ["cylinder 1 misfire"] },
    "25": { "description": "Ignition coil 2 primary circuit", "system": "ignition", "severity": "critical", "symptoms": ["cylinder 2 misfire"] },
    "31": { "description": "Fuel pump relay circuit", "system": "fuel", "severity": "critical", "symptoms": ["no fuel delivery", "no prime on key-on"] },
    "32": { "description": "Idle air control valve circuit", "system": "idle", "severity": "medium", "symptoms": ["unstable idle", "stalling"] },
    "33": { "description": "CKP sensor no signal", "system": "ignition", "severity": "critical", "symptoms": ["no start", "random stalling"] },
    "41": { "description": "Vehicle speed sensor no signal", "system": "drivetrain", "severity": "low", "symptoms": ["no speedometer", "DFCO may not function"] },
    "42": { "description": "Side-stand switch circuit", "system": "safety", "severity": "medium", "symptoms": ["engine cuts when in gear", "no start"] },
    "43": { "description": "Tip-over sensor circuit", "system": "safety", "severity": "medium", "symptoms": ["random engine kill"] },
    "44": { "description": "Immobilizer communication error", "system": "security", "severity": "critical", "symptoms": ["no start", "intermittent no-start", "fuel cut"] }
  },
  "notes": "Code numbers may vary by ECU calibration/year. This is a partial list — expand from IAW5xReader DTC readout."
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('knowledge/schemas/error-codes.json'))"
```

- [ ] **Step 3: Commit**

```bash
git add knowledge/schemas/error-codes.json
git commit -m "feat: add error-codes.json with IAW 5AM DTC database"
```

---

### Task 5: Create Platform Spec Schema (GP800 vs SRV850)

**Files:**
- Create: `knowledge/schemas/platform-spec.json`

- [ ] **Step 1: Create platform-spec.json**

```json
{
  "description": "GP800 vs SRV850 platform comparison — hardware differences affecting ECU swap",
  "version": "1.0.0",
  "platforms": {
    "GP800": {
      "production": "2008-2012",
      "engine": { "displacement_cc": 839.3, "bore_mm": 76, "stroke_mm": 92.5, "compression": 10.5, "layout": "V90", "cylinders": 2, "valves_per_cyl": 4, "valvetrain": "SOHC" },
      "power": { "kw": 56, "hp": 75, "at_rpm": 7500 },
      "torque": { "nm": 76, "at_rpm": 6000 },
      "ecu": "IAW 5AM",
      "spark_plugs": { "type": "NGK CR9EK", "count": 4, "per_cylinder": 2, "gap_mm": 0.7 },
      "fuel": { "system": "EFI", "pressure_bar": 3.0 },
      "transmission": "CVT + cardan shaft",
      "abs": false,
      "immobilizer": "integrated antenna ring",
      "protocol": "K-Line ISO 9141-2 at 10400 baud"
    },
    "SRV850": {
      "production": "2012-2016",
      "engine": "same as GP800",
      "abs": true,
      "abs_type": "2-channel Continental",
      "immobilizer": "separate antenna ring",
      "notes": "Updated fuel/ignition maps, different throttle response tuning"
    },
    "differences": {
      "abs": { "gp800": false, "srv850": true, "impact": "ECU may throw DTCs or enter limp mode if ABS signals missing" },
      "immobilizer_antenna": { "gp800": "integrated", "srv850": "separate ring", "impact": "verify physical compatibility" },
      "ecu_calibration": { "impact": "different fuel/ignition maps for different exhaust/intake geometry" },
      "bodywork": { "impact": "cosmetic only, no functional impact" },
      "dashboard": { "impact": "different CAN messages may cause gauge issues" },
      "exhaust_routing": { "impact": "different backpressure affects fuel map requirements" }
    },
    "parts_interchangeability": {
      "engine_internals": "direct fit",
      "cvt_components": "direct fit",
      "cardan_shaft": "direct fit",
      "brake_calipers": "direct fit (non-ABS side)",
      "suspension": "similar but different spring rates",
      "sensors": "VERIFY — calibration curves may differ",
      "injectors": "VERIFY — flow rates may differ",
      "throttle_body": "VERIFY — diameter may differ",
      "ecu": "compatible with adaptation (this bike's situation)"
    }
  }
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('knowledge/schemas/platform-spec.json'))"
```

- [ ] **Step 3: Commit**

```bash
git add knowledge/schemas/platform-spec.json
git commit -m "feat: add platform-spec.json — GP800 vs SRV850 comparison"
```

---

### Task 6: Create Inter-Agent Communication Schemas

**Files:**
- Create: `knowledge/schemas/diagnostic-report.schema.json`
- Create: `knowledge/schemas/hardware-delta.schema.json`
- Create: `knowledge/schemas/changelog-entry.schema.json`

- [ ] **Step 1: Create diagnostic-report.schema.json**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DiagnosticReport",
  "description": "Diagnostician → SafetyGuard communication format",
  "type": "object",
  "required": ["report_id", "timestamp", "severity", "symptoms_confirmed", "fault_hypotheses", "blocks_flash"],
  "properties": {
    "report_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "severity": { "type": "string", "enum": ["INFORMATIONAL", "CAUTION", "CRITICAL", "EMERGENCY"] },
    "symptoms_confirmed": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "evidence_type": { "type": "string", "enum": ["OWNER_REPORT", "SENSOR_DATA", "VISUAL_INSPECTION", "LOG_ANALYSIS"] },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "fault_hypotheses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "affected_maps": { "type": "array", "items": { "type": "string" } },
          "affected_systems": { "type": "array", "items": { "type": "string" } },
          "mechanical_flag": { "type": "boolean" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "platform_context": {
      "type": "object",
      "properties": {
        "base_vehicle": { "type": "string" },
        "ecu_installed": { "type": "string" }
      }
    },
    "blocks_flash": { "type": "boolean" }
  }
}
```

- [ ] **Step 2: Create hardware-delta.schema.json**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HardwareDelta",
  "description": "ECUEngineer → TuningAdvisor MANDATORY communication format",
  "type": "object",
  "required": ["injector_flow_cc_min", "tps_voltage_range", "coolant_sensor_curve", "exhaust_config", "sai_valve_state"],
  "properties": {
    "injector_flow_cc_min": {
      "type": "object",
      "properties": {
        "stock": { "type": "number" },
        "current": { "type": "number" },
        "verified": { "type": "boolean" }
      }
    },
    "tps_voltage_range": {
      "type": "object",
      "properties": {
        "stock_srv850": { "type": "array", "items": { "type": "number" } },
        "actual_measured": { "type": ["array", "string"] }
      }
    },
    "coolant_sensor_curve": { "type": "string", "enum": ["NTC_GP800", "NTC_SRV850", "UNKNOWN"] },
    "exhaust_config": { "type": "string", "enum": ["2-1", "2-2", "UNKNOWN"] },
    "sai_valve_state": { "type": "string", "enum": ["open", "closed", "disconnected", "unknown"] }
  }
}
```

- [ ] **Step 3: Create changelog-entry.schema.json**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ChangelogEntry",
  "description": "Tuning session log entry format",
  "type": "object",
  "required": ["session_id", "date", "phase", "step"],
  "properties": {
    "session_id": { "type": "string", "format": "uuid" },
    "date": { "type": "string", "format": "date-time" },
    "phase": { "type": "string", "enum": ["Recovery", "Idle", "Cruise", "Performance"] },
    "step": { "type": "string" },
    "map_version_before": { "type": "string" },
    "map_version_after": { "type": "string" },
    "cells_changed": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "map": { "type": "string" },
          "row": { "type": "integer" },
          "col": { "type": "integer" },
          "old_value": { "type": "number" },
          "new_value": { "type": "number" }
        }
      }
    },
    "measured_result": { "type": "object" },
    "target": { "type": "object" },
    "result_vs_target": { "type": "string", "enum": ["CLOSER", "MET", "DIVERGED", "UNKNOWN"] },
    "notes": { "type": "string" },
    "next_action": { "type": "string" }
  }
}
```

- [ ] **Step 4: Verify all three schemas are valid JSON**

```bash
python3 -c "
import json
for f in ['diagnostic-report.schema.json', 'hardware-delta.schema.json', 'changelog-entry.schema.json']:
    json.load(open(f'knowledge/schemas/{f}'))
    print(f'{f}: OK')
"
```

- [ ] **Step 5: Commit**

```bash
git add knowledge/schemas/diagnostic-report.schema.json knowledge/schemas/hardware-delta.schema.json knowledge/schemas/changelog-entry.schema.json
git commit -m "feat: add inter-agent communication schemas"
```

---

### Task 7: Create Remaining JSON Schemas (Stubs)

**Files:**
- Create: `knowledge/schemas/map-definitions.json`
- Create: `knowledge/schemas/maintenance-schedule.json`
- Create: `knowledge/schemas/wiring.json`
- Create: `knowledge/schemas/torque-specs.json`
- Create: `knowledge/schemas/immobilizer.json`
- Create: `knowledge/schemas/parts-compatibility.json`

These are populated with structure and known data. Fields marked TODO require the service manual or physical measurement.

- [ ] **Step 1: Create map-definitions.json**

```json
{
  "description": "IAW 5AM map table definitions — populate from actual .txt export analysis",
  "version": "1.0.0",
  "status": "STUB — requires real ECU dump to complete",
  "maps": {
    "fuel_main_front": { "description": "Main fuel map, cylinder 1 (front)", "axes": { "x": "RPM", "y": "TPS%" }, "value_unit": "ms", "storage": "TODO: confirm 8-bit or 16-bit", "dimensions": "TODO: discover from .txt export" },
    "fuel_main_rear": { "description": "Main fuel map, cylinder 2 (rear)", "axes": { "x": "RPM", "y": "TPS%" }, "value_unit": "ms" },
    "ignition_front": { "description": "Ignition advance, cylinder 1 (front)", "axes": { "x": "RPM", "y": "load" }, "value_unit": "deg_btdc" },
    "ignition_rear": { "description": "Ignition advance, cylinder 2 (rear)", "axes": { "x": "RPM", "y": "load" }, "value_unit": "deg_btdc" },
    "idle_rpm_target": { "description": "Target idle RPM by coolant temp", "axes": { "x": "ECT_degC" }, "value_unit": "rpm" },
    "lambda_target": { "description": "Target lambda at each operating point", "axes": { "x": "RPM", "y": "TPS%" }, "value_unit": "lambda" },
    "cold_start_enrichment": { "description": "Cranking fuel by coolant temp", "axes": { "x": "ECT_degC" }, "value_unit": "ms" },
    "warmup_enrichment": { "description": "Post-start fuel correction by temp", "axes": { "x": "ECT_degC" }, "value_unit": "percent" },
    "accel_enrichment": { "description": "Transient fuel by TPS rate", "axes": { "x": "TPS_rate" }, "value_unit": "ms" },
    "injector_dead_time": { "description": "Injector opening delay vs battery voltage", "axes": { "x": "battery_V" }, "value_unit": "ms" },
    "rev_limiter": { "description": "RPM limit", "type": "scalar", "value_unit": "rpm" }
  }
}
```

- [ ] **Step 2: Create maintenance-schedule.json**

```json
{
  "description": "GP800 maintenance schedule — verify against service manual",
  "version": "1.0.0",
  "intervals_km": {
    "1000": ["oil_change", "general_inspection"],
    "6000": ["oil_change", "oil_filter", "spark_plugs_inspect", "valve_clearance_inspect", "coolant_level", "brake_fluid_check"],
    "12000": ["oil_change", "oil_filter", "spark_plugs_replace", "air_filter_replace", "cvt_belt_inspect", "variator_rollers_inspect", "final_drive_oil", "throttle_body_clean"],
    "24000": ["oil_change", "oil_filter", "cvt_belt_replace", "variator_rollers_replace", "clutch_inspect", "coolant_replace", "brake_fluid_replace", "valve_clearance_adjust"],
    "48000": ["all_24000_items", "cardan_shaft_inspect", "bevel_gear_bearings_inspect"]
  },
  "fluids": {
    "engine_oil": { "spec": "10W-40 JASO MA2", "capacity_with_filter_L": 3.5, "capacity_without_filter_L": 3.2 },
    "coolant": { "spec": "50/50 ethylene glycol", "total_system_L": 2.25, "drain_refill_L": 1.6 },
    "brake_fluid": { "spec": "DOT 4" },
    "final_drive": { "spec": "SAE 80W-90 GL-5", "capacity_mL": 175, "notes": "verify from service manual" }
  }
}
```

- [ ] **Step 3: Create torque-specs.json**

```json
{
  "description": "GP800 torque specifications — approximate, verify against service manual",
  "version": "1.0.0",
  "status": "PARTIAL — needs service manual verification",
  "specs": {
    "spark_plugs": { "nm": 12, "verified": false },
    "oil_drain_plug": { "nm": 30, "verified": false },
    "cardan_shaft_flange_bolts": { "nm": null, "notes": "MUST verify from service manual", "verified": false },
    "exhaust_manifold_nuts": { "nm": 22, "verified": false },
    "wheel_axle_nut": { "nm": 120, "verified": false },
    "throttle_body_clamps": { "method": "hand-tight + 1/4 turn", "verified": false },
    "variator_nut": { "nm": 100, "verified": false },
    "clutch_nut": { "nm": 100, "verified": false }
  }
}
```

- [ ] **Step 4: Create wiring.json, immobilizer.json, parts-compatibility.json stubs**

`knowledge/schemas/wiring.json`:
```json
{
  "description": "GP800/SRV850 wiring reference — populate from wiring diagrams",
  "version": "1.0.0",
  "status": "STUB — requires wiring diagram analysis",
  "ecu_connector": {
    "type": "Molex multi-pin",
    "pin_count": "TODO: count from physical ECU",
    "pins": {}
  },
  "notes": "Pin mapping between GP800 harness and SRV850 ECU must be documented in my-bike/srv850-to-gp800-wiring.md"
}
```

`knowledge/schemas/immobilizer.json`:
```json
{
  "description": "Immobilizer system data — SENSITIVE: fields marked redact:true must never be shared",
  "version": "1.0.0",
  "system": {
    "type": "Piaggio/Magneti Marelli",
    "transponder_chip": "Megamos Crypto 48 / ID48 (verify)",
    "max_keys": 4,
    "requires_pin_for_coding": true
  },
  "this_bike": {
    "ecu_origin": "Aprilia SRV850",
    "immobilizer_status": "UNKNOWN — verify: FULLY_CODED / PARTIALLY_CODED / BYPASSED",
    "pin_code": { "value": null, "redact": true, "notes": "NEVER share this value" },
    "key_codes": { "values": [], "redact": true, "notes": "NEVER share these values" },
    "coding_history": "Key codes synced to SRV850 ECU, later lost and re-linked by friend"
  }
}
```

`knowledge/schemas/parts-compatibility.json`:
```json
{
  "description": "Cross-platform parts compatibility — GP800 / SRV850 / Mana850 / Dorsoduro850",
  "version": "1.0.0",
  "status": "STUB — expand as parts are identified",
  "parts": {}
}
```

- [ ] **Step 5: Verify all JSON files are valid**

```bash
python3 -c "
import json, os
for root, dirs, files in os.walk('knowledge/schemas'):
    for f in sorted(files):
        if f.endswith('.json'):
            path = os.path.join(root, f)
            json.load(open(path))
            print(f'{f}: OK')
"
```
Expected: all files print OK

- [ ] **Step 6: Commit**

```bash
git add knowledge/schemas/
git commit -m "feat: add all remaining JSON schemas (map-definitions, maintenance, torque, wiring, immobilizer, parts)"
```

---

### Task 8: Create My-Bike Owner Documentation

**Files:**
- Create: `my-bike/history.md`
- Create: `my-bike/current-state.md`
- Create: `my-bike/modifications.md`
- Create: `my-bike/srv850-to-gp800-wiring.md`
- Create: `my-bike/baseline-measurements.md`

- [ ] **Step 1: Create history.md**

```markdown
# Bike History

## Acquisition
- Bought from previous owner who could not get the bike running
- Original problem: ECU did not receive signal from side-stand switch
- Side-stand switch controls immobilizer — with immobilizer active, engine will never start

## ECU Swap
- Original GP800 ECU replaced with Aprilia SRV850 ECU from dealer
- SRV850 shares same IAW 5AM platform but has ABS (GP800 does not)
- Key chip codes synced to new ECU — bike started and ran

## Key Coding Issue
- ECU later forgot its memory / could not read key chips
- Friend re-linked key codes to ECU — resolved

## Cardan Shaft Replacement
- Original cardan shaft broke (transfers power from clutch to small gear)
- Replaced by owner with new cardan shaft
- After replacement: bike felt less performant

## ChatGPT Tuning Attempt
- Owner attempted ECU tuning using ChatGPT + IAW5xReader/Writer
- Changed fuel maps, ignition timing, TPS calibration, possibly CVT settings
- Result: bike performance worsened significantly
- No backup of pre-ChatGPT map values saved

## Current Status (2026-03-21)
- Bike starts and rides but with serious problems
- See current-state.md for symptoms
```

- [ ] **Step 2: Create current-state.md**

```markdown
# Current State

**Date last updated:** 2026-03-21
**Rideable:** YES but DANGEROUS — do NOT ride until maps are fixed

## Active Symptoms
1. **Rough idle** — engine stumbles and hiccups at idle
2. **Stalling after start** — sometimes engine stops shortly after starting
3. **Stalling at traffic lights** — engine dies when stopped
4. **Power loss at full throttle** — after ~2 minutes of riding, full throttle causes power to drop off
5. **Choking/air sound** — at full throttle, sounds like choking or getting too much air (similar to running out of fuel)
6. **Red-hot muffler** — visible from inside, glowing red/orange
7. **Flames from exhaust** — visible when bike idles at home after riding

## Safety Assessment
- Red-hot exhaust + flames = SEVERITY 5 (fire risk, catalyst damage, valve damage)
- Power loss at WOT = SEVERITY 4 (thermal protection or detonation)
- Stalling at lights = SEVERITY 3 (traffic safety risk)
- **VERDICT: DO NOT RIDE until resolved**

## Suspected Causes (to be confirmed by Diagnostician)
- Scrambled ECU maps from ChatGPT tuning
- Possible sensor curve mismatch (SRV850 ECU expecting different sensor ranges)
- Possible mechanical issues (cardan shaft alignment, clutch wear)
- Possible exhaust damage from running with bad maps
```

- [ ] **Step 3: Create modifications.md**

```markdown
# Modifications from Stock

## ECU
- **MODIFIED:** Original GP800 ECU replaced with Aprilia SRV850 ECU
- **MODIFIED:** Fuel maps, ignition maps, TPS calibration changed via ChatGPT + IAW5xReader/Writer
- **STATUS:** Maps are scrambled — need recovery

## Drivetrain
- **MODIFIED:** Cardan shaft replaced with new unit (owner-installed)
- **STATUS:** Not independently verified — needs inspection

## Immobilizer
- **MODIFIED:** Key codes re-linked to SRV850 ECU by friend
- **STATUS:** Currently functional but history of issues

## Everything Else
- Stock as far as known
```

- [ ] **Step 4: Create srv850-to-gp800-wiring.md**

```markdown
# SRV850 ECU to GP800 Wiring Adaptation

**STATUS:** NOT YET DOCUMENTED — this is the highest-priority knowledge gap

## What Needs to Be Documented
- [ ] SRV850 ECU connector pinout (from service manual or physical inspection)
- [ ] GP800 wiring harness connector pinout
- [ ] Pin-by-pin comparison: which signals match, which were adapted
- [ ] Any wires that were spliced, rerouted, or disconnected
- [ ] ABS-related pins: what happens on the SRV850 ECU when ABS signals are missing?
- [ ] Dashboard communication: does GP800 dash receive correct data from SRV850 ECU?

## Known Differences
- SRV850 has ABS; GP800 does not — ECU may expect ABS module on CAN bus
- SRV850 immobilizer uses separate antenna ring; GP800 uses integrated
- Sensor calibration curves may differ (TPS, ECT, IAT)

## Action Required
Owner must physically trace and document every wire connection between the GP800 harness and SRV850 ECU.
```

- [ ] **Step 5: Create baseline-measurements.md**

```markdown
# Baseline Measurements

**STATUS:** NOT YET MEASURED — complete during Phase 1 mechanical pre-check

## Compression Test
| Cylinder | Reading (bar) | Date |
|----------|--------------|------|
| Front | — | — |
| Rear | — | — |
| Expected: 11-14 bar, max 10% variance |

## Sensor Readings (key ON, engine OFF)
| Sensor | Expected | Measured | Date |
|--------|----------|----------|------|
| TPS closed | 0.5V | — | — |
| TPS WOT | 4.5V | — | — |
| ECT @ ambient | see sensor-specs.json | — | — |
| IAT @ ambient | see sensor-specs.json | — | — |
| MAP (atmospheric) | ~4.0V | — | — |
| Battery | >12.4V | — | — |

## Fuel Pressure
| Condition | Expected (bar) | Measured | Date |
|-----------|---------------|----------|------|
| Key ON static | 3.0-3.5 | — | — |
| Idle | ~3.0 | — | — |
| Sustained WOT | 3.0-3.5 | — | — |

## Electrical
| Test | Expected | Measured | Date |
|------|----------|----------|------|
| Battery resting | >12.4V | — | — |
| Cranking | >10.5V | — | — |
| Charging @ 3000rpm | 13.5-14.5V | — | — |
| Ground: battery to engine | <0.5 ohm | — | — |
| Ground: engine to frame | <0.5 ohm | — | — |
| Injector 1 resistance | 12-16 ohm | — | — |
| Injector 2 resistance | 12-16 ohm | — | — |
| Coil 1 primary | 0.5-2.0 ohm | — | — |
| Coil 2 primary | 0.5-2.0 ohm | — | — |
```

- [ ] **Step 6: Commit**

```bash
git add my-bike/
git commit -m "feat: add owner-specific bike documentation (history, state, mods, wiring, measurements)"
```

---

### Task 9: Create Master Index

**Files:**
- Create: `_index.md`

- [ ] **Step 1: Create _index.md**

```markdown
# Gilera GP800 Expert Agent System — Master Index

**Bike:** Gilera GP800 with Aprilia SRV850 ECU (IAW 5AM)
**Status:** Maps scrambled — recovery in progress
**Safety:** DO NOT RIDE until maps are corrected

---

## Quick Navigation

### My Bike (owner-specific)
- [History](my-bike/history.md) — ownership timeline, ECU swap, repairs
- [Current State](my-bike/current-state.md) — active symptoms, safety assessment
- [Modifications](my-bike/modifications.md) — every deviation from stock
- [SRV850-to-GP800 Wiring](my-bike/srv850-to-gp800-wiring.md) — ECU swap pin mapping
- [Baseline Measurements](my-bike/baseline-measurements.md) — sensor readings, compression, fuel pressure

### Reference (static facts)
- [Engine Specs](knowledge/reference/engine-specs.md)
- [ECU — IAW 5AM](knowledge/reference/ecu-iaw5am.md)
- [Fuel System](knowledge/reference/fuel-system.md)
- [Ignition](knowledge/reference/ignition.md)
- [Transmission/CVT](knowledge/reference/transmission-cvt.md)
- [Electrical](knowledge/reference/electrical.md)
- [Platform Differences (GP800 vs SRV850)](knowledge/reference/platform-differences.md)
- [Error Codes](knowledge/reference/error-codes.md)
- [Sensor Reference](knowledge/reference/sensor-reference.md)

### Procedures (step-by-step)
- [Diagnostic Flowcharts](knowledge/procedures/diagnostic-flowcharts.md)
- [Tuning Workflow](knowledge/procedures/tuning-workflow.md)
- [Common Tuning Mistakes](knowledge/procedures/tuning-common-mistakes.md)
- [Mechanical Pre-Check](knowledge/procedures/mechanical-pre-check.md)
- [Bricked ECU Recovery](knowledge/procedures/bricked-ecu-recovery.md)
- [IAW5xReader/Writer Guide](knowledge/procedures/iaw5x-reader-writer.md)
- [OBD Diagnostics](knowledge/procedures/obd-diagnostics.md)
- [Exhaust Diagnostics](knowledge/procedures/exhaust-diagnostics.md)
- [Service & Maintenance](knowledge/procedures/service-maintenance.md)

### Schemas (machine-readable, single source of truth)
- [Safe Ranges](knowledge/schemas/safe-ranges.json) — **PRIMARY**: all safety limits
- [Sensor Specs](knowledge/schemas/sensor-specs.json) — test values for all sensors
- [Error Codes](knowledge/schemas/error-codes.json) — DTC database
- [Platform Spec](knowledge/schemas/platform-spec.json) — GP800 vs SRV850
- [Map Definitions](knowledge/schemas/map-definitions.json) — ECU map structure
- [Maintenance Schedule](knowledge/schemas/maintenance-schedule.json)
- [Torque Specs](knowledge/schemas/torque-specs.json)
- [Wiring](knowledge/schemas/wiring.json)
- [Immobilizer](knowledge/schemas/immobilizer.json) — SENSITIVE DATA
- [Parts Compatibility](knowledge/schemas/parts-compatibility.json)

### Map Files
- [original/](map-files/original/) — first ECU read
- [modified/](map-files/modified/) — ChatGPT-modified versions
- [working/](map-files/working/) — current working files
- [stock/](map-files/stock/) — validated stock/community maps

### Design Documents
- [Spec](docs/superpowers/specs/2026-03-21-gilera-gp800-expert-agent-design.md)
- [Plan 1: Knowledge Base](docs/superpowers/plans/2026-03-21-knowledge-base-foundation.md) — this plan
```

- [ ] **Step 2: Commit**

```bash
git add _index.md
git commit -m "feat: add master index with navigation to all knowledge base files"
```

---

### Task 10: Create Knowledge Reference Files (Stubs)

**Files:**
- Create: All 9 files in `knowledge/reference/`
- Create: All 9 files in `knowledge/procedures/`

These are created as stubs with headers and key content from the spec. They will be populated with full content during the knowledge base growth phase.

- [ ] **Step 1: Create all reference stubs**

Create each file in `knowledge/reference/` with a header, brief content summary from the spec, and TODO markers for content that needs the service manual. Key files to populate immediately (from spec Section 9):

`engine-specs.md` — V-twin 839cc specs from spec lines 576-583
`ecu-iaw5am.md` — IAW 5AM architecture from spec lines 585-593
`sensor-reference.md` — full sensor table from spec lines 176-189
`error-codes.md` — DTC table from spec lines 635-646
`platform-differences.md` — GP800 vs SRV850 from spec lines 626-631

- [ ] **Step 2: Create all procedure stubs**

Create each file in `knowledge/procedures/` with a header, brief content from the spec, and TODO markers. Key files to populate immediately:

`mechanical-pre-check.md` — 14-point checklist from spec lines 234-248
`tuning-workflow.md` — 12-step tuning order from spec lines 269-281
`diagnostic-flowcharts.md` — cross-reference matrix from spec lines 163-172

- [ ] **Step 3: Commit**

```bash
git add knowledge/reference/ knowledge/procedures/
git commit -m "feat: add reference and procedure stubs for all knowledge base topics"
```

---

### Task 11: Final Verification

- [ ] **Step 1: Verify complete directory structure**

```bash
find . -type f | grep -v '.git/' | sort
```

Expected: all files from the spec Section 5 directory tree are present

- [ ] **Step 2: Verify all JSON schemas are valid**

```bash
python3 -c "
import json, os
errors = []
for root, dirs, files in os.walk('knowledge/schemas'):
    for f in sorted(files):
        if f.endswith('.json'):
            path = os.path.join(root, f)
            try:
                json.load(open(path))
                print(f'OK: {f}')
            except Exception as e:
                errors.append(f'{f}: {e}')
                print(f'FAIL: {f}: {e}')
if errors:
    print(f'\n{len(errors)} ERRORS')
else:
    print(f'\nAll schemas valid')
"
```
Expected: "All schemas valid"

- [ ] **Step 3: Verify git status is clean**

```bash
git status
```
Expected: "nothing to commit, working tree clean"

- [ ] **Step 4: Final commit tag**

```bash
git tag v0.1.0-knowledge-base -m "Knowledge base foundation complete — ready for CLI tool implementation"
```

---

## What's Next

This plan creates the foundation. The next two plans build on it:

- **Plan 2:** `2026-03-21-cli-tool-gp800.md` — Python CLI tool (`gp800-tool`) with parse, validate, compare, export commands. Reads from `schemas/` for all validation logic.
- **Plan 3:** `2026-03-21-claude-skill-gp800-expert.md` — Claude Code skill with 8 agents. Uses knowledge base for context and calls CLI tool for validation.
