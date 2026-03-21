# Gilera GP800 Expert Agent System — Design Specification

**Date:** 2026-03-21
**Status:** Approved
**Owner:** arlay
**Validated by:** 12 specialized agent reviews across 2 iterations

---

## 1. Problem Statement

The owner has a Gilera GP800 motorcycle with an Aprilia SRV850 ECU (Magneti Marelli IAW 5AM) that was tuned using ChatGPT-generated map values. The maps are now scrambled, causing dangerous symptoms: red-hot exhaust manifold, flames from exhaust, rough idle, stalling at traffic lights, and power loss at full throttle after 2 minutes of riding.

**SAFETY WARNING:** The bike must NOT be ridden until maps are corrected. Red-hot exhaust and flames indicate severe lean condition or grossly incorrect ignition timing — active fire risk and engine destruction risk.

**Additional context:**
- Original GP800 ECU failed (side-stand switch signal fault). Replaced with Aprilia SRV850 ECU from dealer.
- Key chip codes were synced to new ECU. Later lost and re-linked by a friend.
- Cardan shaft (clutch-to-gear power transfer) was replaced by the owner.
- Possible clutch issues (unconfirmed).
- No backup of pre-ChatGPT map values.
- Owner has IAW5xReader/Writer hardware and can flash the ECU.
- .txt map files exist in the Writer folder; 1 .txt file in the Reader folder.

---

## 2. System Overview

Three integrated components:

1. **Knowledge Base** — Structured markdown + JSON files containing all GP800/SRV850 technical data
2. **Claude Code Skill** (`gilera-gp800-expert`) — Interactive expert agent with 8 specialized sub-agents
3. **Python CLI Tool** (`gp800-tool`) — Standalone map analysis, validation, and management tool

### Design Principles
- **Rider safety first** — never recommend changes that could cause dangerous riding conditions
- **Don't break the bike** — validate changes won't damage engine, ECU, exhaust, or drivetrain
- **Don't over-tune** — conservative incremental changes only, max 5% per step
- **Diagnose before tuning** — never suggest map changes without understanding root cause
- **Mechanical before ECU** — fix mechanical issues before touching maps
- **Backup before flash** — always save current state before writing
- **Stock first** — when in doubt, return to stock/safe values as baseline
- **Make it harder to flash a dangerous map than a safe one**

---

## 3. Agent Architecture (8 Agents)

### 3.1 Hierarchy

```
                      COORDINATOR
                           |
           +-------+-------+-------+-------+
           |       |       |       |       |
      SAFETY   DIAGNOSTICIAN  ECU     MECHANICAL  KNOWLEDGE
      LAYER        |       ENGINEER   ADVISOR     SERVICE
        |          |          |          |            |
   +----+----+    |          |          |            |
   |         |    |          |          |            |
SafetyGuard  FlashMonitor   |          |            |
                            |          |            |
                       TuningAdvisor---+            |
                            |                       |
                            +-----------------------+
```

### 3.2 Agent Specifications

#### Agent 1: Coordinator
- **Role:** Top-level router, workflow orchestrator, conflict resolver
- **Triggers:** All user input
- **Responsibilities:**
  - Route queries to appropriate agent(s)
  - Enforce mandatory workflow ordering (diagnose → mechanical → ECU)
  - Enforce pre-flash safety sequence
  - Aggregate multi-agent responses
  - Manage conversation state
- **Skill mapping:** Main Claude Code skill (`gilera-gp800-expert`)

#### Agent 2: SafetyGuard
- **Role:** Pre-operation validation + risk scoring. **VETO AUTHORITY** — cannot be bypassed.
- **Absorbed from:** SafetyValidator + RiskAssessor
- **Functions:**
  - `validate_parameters()` — validate all ECU parameters against safety limits
  - `assess_risk()` — score operational risk (1-10) before any flash/modification
- **5 internal sub-validators:**
  - FuelSafety — AFR limits, injector bounds, lean protection
  - IgnitionSafety — timing advance limits, dwell time, knock thresholds
  - PlatformCompatibility — SRV850-to-GP800 sensor curves, pin mapping, ABS entries
  - ThermalSafety — exhaust temp, catalyst protection, cooling maps
  - MechanicalLimits — rev limiter, fuel pressure vs demand, component stress
- **Hard limits (IAW 5AM):**

| Parameter | Min | Max | Unit | Notes |
|-----------|-----|-----|------|-------|
| fuel_map_value | 0 | 255 | raw | |
| ignition_advance | -10 | 45 | deg BTDC | >40 risks detonation on 95 RON |
| idle_rpm | 1100 | 1500 | RPM | <1100 stalls; >1500 clutch drag |
| rev_limiter | 8000 | 9500 | RPM | Stock ~8500; >9500 valve float |
| lambda_target | 0.82 | 1.05 | lambda | <0.82 fouling; >1.05 lean misfire |
| injector_duration_max | 0.5 | 12.0 | ms | >12ms hydro-lock risk |

- **Flash blockers (absolute, no override):**
  - `rev_limiter > 9500`
  - `ignition_advance > 45` at any cell
  - `ignition_advance < -10` at any cell (extreme retard = exhaust fires, valve damage)
  - `lambda_target > 1.05` at any WOT cell (dangerously lean = melted pistons)
  - `lambda_target < 0.82` at any cell (extreme rich = fouling, catalyst destruction)
  - Fuel map contains all-zero row (no fuel = lean seizure)
  - Fuel map contains all-255 row (max saturation = hydro-lock, catalyst destruction)
  - Injector dead-time table not monotonically decreasing with voltage (corrupted)
  - Checksum mismatch after edit
  - File size != expected IAW 5AM binary size
  - No verified backup exists (must be specific filename + SHA256 from THIS session)
  - Immobilizer PIN not confirmed available
  - Mechanical pre-check not passed (with actual measured values recorded, not just pass/fail)
  - Battery voltage < 12.0V (risk of corrupted flash write)
- **Skill mapping:** `eng-security`

#### Agent 3: FlashMonitor
- **Role:** Post-flash verification checklists + manual rollback management
- **Absorbed from:** PostFlashMonitor + RollbackAgent
- **Important hardware constraint:** The IAW 5AM communicates over K-Line ISO 9141-2 at 10.4 kbaud. A full ECU reflash takes **several minutes**, not seconds. Automated real-time rollback is NOT possible with this hardware. All rollback is **human-executed** using IAW5xReader/Writer.
- **Functions:**
  - `verify_post_flash()` — generates structured post-flash checklist with go/no-go criteria for the owner to execute manually
  - `execute_rollback()` — provides step-by-step instructions to re-flash last-known-good state via IAW5xWriter (estimated time: 5-10 minutes)
- **Post-flash human checklist (executed by owner):**
  1. Ignition ON, engine OFF: fuel pump primes? Dashboard normal? No new DTCs?
  2. Start engine: idle within 1100-1400 RPM within 10 seconds?
  3. 30-second observation: exhaust color normal? No red glow? No flames?
  4. If ANY check fails: **KILL ENGINE IMMEDIATELY** → follow rollback procedure
- **Rollback procedure (manual):**
  1. Turn ignition OFF
  2. Connect IAW5xWriter
  3. Flash the verified backup file (from pre-flash backup)
  4. Verify flash via read-back comparison
  5. Estimated time: 5-10 minutes
- **Abort criteria (owner must memorize before any flash):**
  - Exhaust manifold begins glowing → KILL ENGINE
  - Flames from exhaust → KILL ENGINE
  - RPM oscillates wildly (>500 RPM swings) → KILL ENGINE
  - Any unusual metallic pinging sound → KILL ENGINE
  - Stalling within first 30 seconds → do NOT restart, investigate
  - Coolant temperature gauge rises past 3/4 mark within first 2 minutes → KILL ENGINE
  - Excessive white/blue smoke or strong raw fuel smell from exhaust → KILL ENGINE
  - **First post-flash engine start requires second person present with fire extinguisher**
- **Skill mapping:** `eng-security`

#### Agent 4: Diagnostician
- **Role:** Full-system diagnostic reasoning. **MANDATORY FIRST STEP** — no other agent acts without diagnosis.
- **Absorbed from:** Diagnostician + ElectricalDiagnostics + ImmobilizerExpert
- **Functions:**
  - Core diagnostic decision trees for all GP800 systems
  - `diagnose_electrical()` — wiring, connectors, grounds, charging, sensor signals
  - `check_immobilizer()` — key coding, PIN recovery, transponder, antenna ring, bypass verification
- **Structured symptom intake:** Every diagnostic session starts with:
  1. Symptom description (what exactly happens?)
  2. Conditions (when? cold/warm/always?)
  3. Recent changes (what was modified last?)
  4. Current state (rideable? starts? fault lights?)
- **Cross-reference priority matrix:**

| Component | Rough Idle | Power Loss | Red Exhaust | Stalling |
|-----------|:---:|:---:|:---:|:---:|
| Vacuum leak | *** | * | * | ** |
| TPS | ** | * | - | *** |
| MAP sensor | ** | ** | *** | * |
| ECT sensor | ** | ** | *** | * |
| Fuel pressure | ** | *** | ** | * |
| Ignition coils | * | *** | *** | * |
| O2 sensor | * | ** | * | ** |

- **Sensor reference (multimeter testing):**

| Sensor | Test | Expected |
|--------|------|----------|
| TPS signal | DC Volts | 0.5V closed → 4.5V WOT |
| MAP signal | DC Volts | ~1V idle, ~4V WOT |
| IAT resistance | Ohms | 2-3 kOhm @ 20C |
| ECT resistance | Ohms | 2.5 kOhm @ 20C, 0.3 kOhm @ 90C |
| CKP resistance | Ohms | 200-400 Ohm (VR inductive sensor, AC signal) |
| CMP sensor | Verify | **TODO: Confirm if GP800/SRV850 uses CMP or CKP-only cylinder ID** |
| O2 heater | Ohms | 2-15 Ohm |
| Injector | Ohms | 12-16 Ohm |
| Coil primary | Ohms | 0.5-2.0 Ohm |
| Battery resting | DC Volts | >12.4V |
| Charging @ idle | DC Volts | 13.5-14.5V |
| Fuel pressure | Gauge | 3.0-3.5 bar |

- **Skill mapping:** `eng-backend`

#### Agent 5: ECUEngineer
- **Role:** All ECU map operations — analysis, comparison, recovery, stock map sourcing
- **Absorbed from:** MapAnalyst + CrossPlatformChecker + MapRecoverySpecialist + StockMapDatabase
- **Functions:**
  - `parse()` — parse IAW5xReader/Writer .txt and .bin files with strict schema validation
  - `compare()` — cell-by-cell delta with severity ranking
  - `validate()` — pre-flash 10-point safety checklist
  - `query_stock_maps()` — 4-tier fallback: exact → fuzzy → cousin platform → web/forum search. If all tiers fail: STOP and recommend professional tuner (no synthetic map generation — too dangerous)
  - `check_platform_compatibility()` — GP800 vs SRV850 hardware delta analysis
  - `generate_recovery_map()` — ONLY when a stock/community map exists as base: apply conservative safety margins (20% rich, retarded timing, 4000 RPM rev limit — above CVT engagement speed of ~3000-3500 RPM) to create an "idle-and-limp-to-tuner" map. **NEVER generates maps from scratch** — if no base map exists, directs owner to professional tuner. Note: even with a recovery map, trailering to a tuner is preferred over riding
- **HardwareDelta output (mandatory for TuningAdvisor):**

| Signal | GP800 Native | SRV850 ECU Expects | Action |
|--------|-------------|-------------------|--------|
| TPS | ~0.5-4.5V (verify on actual hardware) | 0.5-4.5V | Verify match; rescale if different |
| Injector impedance | ~12 ohm | ~12 ohm | Compatible |
| Lambda heater | Shared ground | Dedicated ground | Wiring check |
| ECT sensor | NTC 2.5k@20C | NTC 2.5k@20C | Compatible |
| Immobilizer | Integrated | Separate ring | Hardware check |

- **Community map validation pipeline (5 stages):**
  1. Structural validation (file size, checksum, parseable)
  2. Safety bounds check (rev limiter, AFR, timing limits)
  3. Hardware compatibility (injector size, sensor curves match OUR hardware)
  4. Delta comparison against baseline (flag >15% deviations)
  5. Final gate: PASS → "CANDIDATE"; FAIL → "REFERENCE_ONLY"
- **Skill mapping:** `eng-backend`

#### Agent 6: MechanicalAdvisor
- **Role:** All mechanical systems + parts compatibility + tools + cost estimates
- **Absorbed from:** MechanicalAdvisor + PartsCompatibility + ToolRequirements + CostEstimator
- **Functions:**
  - Full mechanical diagnosis (clutch, CVT, cardan, cooling, brakes, intake, exhaust)
  - `check_parts_compatibility()` — cross-reference GP800/SRV850/Mana850/Dorsoduro850
  - `estimate_cost_and_tools()` — parts cost, tool lists, torque specs
  - Maintenance interval tracking
- **Can BLOCK tuning** with MechanicalStateReport severity: BLOCKING when:
  - Vacuum leak detected (AFR data unreliable)
  - Coolant leak / overheating (engine damage risk)
  - Fuel pressure out of spec
  - Compression test failed
- **Mechanical pre-check (MUST pass before any ECU work):**
  1. Compression test — both cylinders, 11-14 bar expected, min 10.5 bar serviceable, max 10% variance
  2. Vacuum leak test — spray test all intake connections
  3. Throttle body sync and cleaning — manometer balance, clean IAC/stepper valve
  4. Fuel pressure — 3.0-3.5 bar static AND under sustained load
  5. Exhaust integrity — no leaks, SAI valve check, catalyst rattle test, header warpage check, lambda sensor resistance
  6. Cardan shaft verification — spline engagement and lubrication, U-joint play, flange bolt torque, final drive oil level, output shaft seal, backlash measurement
  7. Sensor functionality — all sensors within spec (including CMP if present)
  8. Battery load test — >10.5V cranking, >12.0V for flash operations
  9. Ground points — <0.5 ohm resistance
  10. ECU connector inspection — no corrosion, bent pins
  11. CVT belt inspection — width measurement (replace if below spec), cracking, glazing
  12. Clutch assessment — engagement RPM, shoe/pad thickness, drum condition, spring check
  13. Air filter condition — clean or replace
  14. Fuel filter condition — inspect or replace (restricted filter starves engine under load)
- **Key fluid specs:**

| Fluid | Spec | Capacity |
|-------|------|----------|
| Engine oil | 10W-40 JASO MA2 | 3.5L (with filter) / 3.2L (without) |
| Coolant | 50/50 ethylene glycol | 2.0-2.5L (total system) / ~1.6L (drain-refill) |
| Brake fluid | DOT 4 | - |
| Final drive | SAE 80W-90 GL-5 | ~150-200mL (verify from service manual) |

- **Skill mapping:** `eng-backend`

#### Agent 7: TuningAdvisor
- **Role:** Safe incremental tuning guidance, bridges ECU data to rider-facing advice
- **Mandatory inputs:** HardwareDelta from ECUEngineer, MechanicalStateReport from MechanicalAdvisor
- **Rules:**
  - Max 5% change per step: 5% refers to resulting change in injector pulse width (ms). When HardwareDelta indicates different injector flow rate, scale raw value change by (stock_flow / actual_flow). Example: actual 260cc vs stock 220cc → max raw change = 5% * (220/260) = 4.23%
  - One variable at a time — never change fuel and timing simultaneously
  - Always includes rollback instructions
  - Always check both cylinders (rear runs hotter)
  - Refuses to tune without baseline map and mechanical pre-check
- **Tuning order (enforced):**
  0. Verify injector dead-time table matches installed injectors (must be correct before any fuel tuning)
  1. Fuel maps at idle (FRONT cylinder first, then REAR independently) → target lambda 0.97-1.03
  2. Cold-start enrichment — cranking pulse width by ECT. Target: starts within 3 cranks at 0-40C
  3. Warmup enrichment curve — ECT-based fuel correction (30% extra at 0C, taper to 0% at 80C)
  4. Fuel maps at cruise (front then rear) → target lambda 0.97-1.03
  5. Fuel maps at WOT (front then rear) → target lambda 0.85-0.88. **Rear cylinder: 0.02-0.03 richer than front**
  6. Ignition timing at idle (front then rear) → 10-14 deg BTDC
  7. Ignition timing at cruise → advance for best torque, watch for knock
  8. Ignition timing at WOT → 1 degree at a time only. **Rear: start 1-2 deg more retarded than front**
  9. Throttle body sync verification — re-sync after idle changes
  10. Acceleration enrichment — tune last, to cure transient hesitation
  11. Deceleration fuel cut-off — verify thresholds (cut >1800 RPM closed throttle, resume >1400 RPM)
- **Phase-based approach:**

| Phase | Focus | When |
|-------|-------|------|
| RecoveryTuner | Getting from broken to running | Initial crisis |
| IdleTuner | Stable idle, clean cold start | First tuning pass |
| CruiseTuner | Part-throttle drivability, economy | Second pass |
| PerformanceTuner | WOT fueling, timing, rev limit | Final pass |

- **Skill mapping:** `eng-backend`

#### Agent 8: KnowledgeService
- **Role:** All data I/O — specs, files, web research, changelog
- **Absorbed from:** KnowledgeAndFiles + WebResearcher + ChangelogTracker
- **Functions:**
  - Document storage and retrieval
  - `fetch_web_data()` — search forums for GP800/SRV850 technical data
  - `track_changelog()` — semantic layer on top of git (records WHY, not just WHAT)
  - File versioning with git under the hood
  - Stock map storage in `stock_maps/` namespace
- **Data contracts:**
  - `getMapTable(mapName, version)` → structured table data
  - `getSpec(specName)` → value with units and source
  - `getWiringInfo(connector, pin)` → signal name, expected voltage, wire color
- **Immobilizer data policy:** NEVER share transponder key codes publicly. Redact from any shared files.
- **Skill mapping:** `eng-backend`

---

## 4. Inter-Agent Communication Protocols

### 4.1 DiagnosticReport (Diagnostician → SafetyGuard)

```json
{
  "report_id": "UUID",
  "severity": "INFORMATIONAL | CAUTION | CRITICAL | EMERGENCY",
  "symptoms_confirmed": [{"description": "...", "confidence": 0.0-1.0}],
  "fault_hypotheses": [{"description": "...", "affected_maps": [], "mechanical_flag": false, "confidence": 0.0-1.0}],
  "platform_context": {"base_vehicle": "GP800", "ecu_installed": "SRV850"},
  "blocks_flash": true
}
```

### 4.2 Rollback Procedures (FlashMonitor — all human-executed)

**Hardware constraint:** K-Line at 10.4 kbaud. No automated real-time rollback exists. All rollback is manual via IAW5xWriter.

| Urgency | Owner Action | Rollback Time |
|---------|-------------|---------------|
| EMERGENCY (exhaust glow, flames, pinging) | KILL ENGINE immediately, then manual reflash | ~5-10 min reflash |
| MANDATORY (rough idle, stalling, high fuel trims) | Shut down, investigate, then manual reflash if needed | ~5-10 min reflash |
| ADVISORY (minor drivability issues) | Continue monitoring, reflash at next session | operator-dependent |

### 4.3 HardwareDelta (ECUEngineer → TuningAdvisor, MANDATORY)

```json
{
  "injector_flow_cc_min": {"stock": 220, "current": 260},
  "tps_voltage_range": {"stock_srv850": [0.5, 4.5], "actual_measured": "MUST VERIFY ON BIKE"},
  "coolant_sensor_curve": "NTC_GP800 | NTC_SRV850",
  "exhaust_config": "2-1 | 2-2",
  "sai_valve_state": "open | closed | disconnected | unknown"
}
```

### 4.4 MechanicalStateReport (MechanicalAdvisor → TuningAdvisor)

```json
{
  "issues": [{
    "system": "intake",
    "condition": "vacuum_leak_suspected",
    "severity": "BLOCKING",
    "tuning_impact": "AFR readings unreliable until fixed"
  }]
}
```

### 4.5 Conflict Resolution Rules (priority order)
1. **SafetyGuard always has veto power** — nothing overrides a BLOCK
2. **Diagnostician determines necessity** — "mechanical, not ECU" suspends flash approvals
3. **Mechanical findings create HOLD** — `mechanical_flag: true` with confidence >0.6 suspends pending flashes
4. **Dual-cause protocol** — fix mechanical FIRST, re-diagnose, THEN ECU maps
5. **Operator override** — explicit acknowledgment required and logged

---

## 5. Knowledge Base Structure

```
Gilera GP800/
├── _index.md                           # Master cross-reference
├── knowledge/
│   ├── reference/                      # Static facts
│   │   ├── engine-specs.md             # V-twin 839cc, 75HP, 76Nm
│   │   ├── ecu-iaw5am.md              # IAW 5AM architecture, memory layout, pins
│   │   ├── fuel-system.md             # Injectors, fuel pump, pressure, TPS, lambda
│   │   ├── ignition.md               # Coils, timing, spark plugs (4 total, twin-spark)
│   │   ├── transmission-cvt.md        # CVT, clutch, cardan shaft, final drive
│   │   ├── electrical.md             # Immobilizer, side-stand, wiring, K-Line protocol
│   │   ├── platform-differences.md    # GP800 vs SRV850 complete comparison
│   │   ├── error-codes.md            # Full IAW 5AM DTC list + MIL blink code procedure
│   │   └── sensor-reference.md        # All sensors with test values and procedures
│   ├── procedures/                     # Step-by-step workflows
│   │   ├── diagnostic-flowcharts.md   # Symptom → test → cause → fix decision trees
│   │   ├── tuning-workflow.md         # Safe tuning procedure with order enforcement
│   │   ├── tuning-common-mistakes.md  # What goes wrong and symptoms
│   │   ├── mechanical-pre-check.md    # 10-point gate before ECU work
│   │   ├── bricked-ecu-recovery.md    # Emergency recovery via BDM/boot mode
│   │   ├── iaw5x-reader-writer.md    # Tool usage guide
│   │   ├── obd-diagnostics.md        # Compatible tools, K-Line protocol details
│   │   ├── exhaust-diagnostics.md    # Reading symptoms from exhaust
│   │   └── service-maintenance.md     # Intervals, fluids, common issues
│   └── schemas/                        # Single source of truth (JSON) — runtime authority, spec tables are illustrative only
│       ├── safe-ranges.json           # Per-parameter min/max/danger thresholds (tuning guidance + hard limits)
│       ├── map-definitions.json       # Map names, axes, units, dimensions
│       ├── sensor-specs.json          # Voltages, resistances, thresholds
│       ├── error-codes.json           # DTC database (partial initially, expand from IAW5xReader)
│       ├── maintenance-schedule.json  # Intervals + items
│       ├── platform-spec.json         # GP800 vs SRV850 hardware comparison
│       ├── wiring.json                # Connector, pin, signal, voltage, wire color
│       ├── torque-specs.json          # All torque values from service manual
│       ├── immobilizer.json           # Immobilizer data with redaction fields (sensitive fields marked "redact": true)
│       ├── parts-compatibility.json   # Cross-reference GP800/SRV850/Mana850/Dorsoduro850
│       ├── diagnostic-report.schema.json  # Inter-agent DiagnosticReport format
│       ├── hardware-delta.schema.json     # Inter-agent HardwareDelta format
│       └── changelog-entry.schema.json    # Tuning session log entry format
├── my-bike/
│   ├── history.md                     # Full ownership history, timeline
│   ├── current-state.md              # Current symptoms, what's been tried
│   ├── modifications.md              # Every deviation from stock
│   ├── srv850-to-gp800-wiring.md     # ECU swap pin-by-pin mapping
│   └── baseline-measurements.md      # Actual sensor readings, compression, fuel pressure from pre-check
├── map-files/
│   ├── original/                      # First ECU read (if available)
│   ├── modified/                      # ChatGPT-modified versions
│   ├── working/                       # Current working files
│   └── stock/                         # Stock/community reference maps (validated)
├── gp800-tool/                        # Python CLI tool source
└── docs/
    └── superpowers/
        └── specs/
            └── this file
```

---

## 6. Python CLI Tool (`gp800-tool`)

### 6.1 Commands

```
gp800-tool init                         # Initialize project directory + git repo
gp800-tool parse <file>                 # Validate and summarize a map file
gp800-tool compare <file1> <file2>      # Cell-by-cell diff with safety flags
gp800-tool validate <file>              # Pre-flash 10-point safety checklist
gp800-tool export <file> [--strict]     # Generate flash-ready output
gp800-tool explain <map-name>           # Plain-language map explanation
gp800-tool quickcheck <file>            # Go/no-go (green/yellow/red)
gp800-tool diagnose <file> [--symptoms] # Symptom-based map diagnosis
gp800-tool history                      # Version log (git-backed)
gp800-tool diff <v1> <v2>              # Compare historical versions
gp800-tool rollback <version>           # Restore previous version
gp800-tool merge <base> <donor> --maps  # Cherry-pick maps between files
gp800-tool backup <file>                # Timestamped backup with checksum
gp800-tool plot <file> <map-name>       # Matplotlib heatmap/3D surface (static PNG)
gp800-tool export-csv <file> <map>      # Export single map as CSV
gp800-tool log-note "message"           # Attach note to current version
```

### 6.2 Tech Stack
- Python 3.10+
- No heavy dependencies: `matplotlib` for visualization, `json`/`csv` for data
- Git for version tracking (under the hood)
- All structured data from `schemas/` directory (single source of truth)
- Encoding handling: detect Windows-1252 vs UTF-8, normalize decimal separators

### 6.3 Pre-Flash Validation Checklist (automated)
1. All expected maps present and correct dimensions
2. No values outside absolute hardware limits
3. Rev limiter set and within safe range
4. Ignition advance within detonation-safe limits at all cells
5. Fuel maps not leaner than -10% from stock at high RPM/high load
6. TPS/throttle maps are monotonic
7. Idle speed target within sane range
8. Lambda target maps not commanding dangerously lean
9. Round-trip parse test passes (export → re-import = identical)
10. File hash recorded for traceability

### 6.4 Build Priority
1. Parsing with strict validation
2. Pre-flash safety validation
3. Compare with delta maps and per-map thresholds
4. Export in IAW5xWriter format with round-trip verification
5. Stock map library and auto-detection
6. Version tracking via git
7. Matplotlib visualization (heatmaps, 3D surfaces)
8. Map merge
9. Safe restore / conservative map generation

---

## 7. Claude Code Skill (`gilera-gp800-expert`)

### 7.1 Trigger Conditions
Invoke when user mentions: Gilera, GP800, SRV850, ECU, tuning, mapping, IAW, bike problems, motorcycle diagnostics.

### 7.2 Context Loading (Retrieval Pattern)
- **Always loaded:** `_index.md`, `my-bike/*`, `schemas/safe-ranges.json`
- **Loaded on demand:** Specific knowledge files pulled based on conversation topic
- **Never bulk-loaded:** Full knowledge base (context window limit)

### 7.3 Behavior Priorities
1. **Rider safety** — never recommend changes causing dangerous riding conditions
2. **Don't break the bike** — validate against component stress limits
3. **Don't over-tune** — conservative incremental changes, test between each
4. **Diagnose before tuning** — understand root cause first
5. **Mechanical before ECU** — fix mechanical issues first
6. **Backup before flash** — always save current state
7. **Stock first** — when in doubt, return to safe baseline

### 7.4 Skill Calls CLI Tool
For all validation operations, the skill runs `gp800-tool validate` rather than reimplementing range checks from markdown. The CLI tool is the source of truth for validation logic.

---

## 8. Master Recovery Workflow

### Phase 0: Safety Lockout (25 min)
- Risk assessment of current symptoms
- Establish safety protocols (fire extinguisher, ventilation, second person)
- Owner acknowledges all safety rules

### Phase 1: Mechanical Pre-Check (4-5 hours)
- Visual inspection (exhaust, intake, fuel, coolant, connectors, cardan)
- Electrical baseline (battery, grounds, charging, injector/coil resistance)
- Sensor functionality (TPS, ECT, IAT, MAP, CKP, O2)
- Cross-platform compatibility verification (SRV850 ECU vs GP800 hardware)
- Immobilizer status check
- **GO/NO-GO:** Fix vacuum leaks, exhaust leaks, sensor faults BEFORE proceeding

### Phase 2: ECU Backup & Analysis (2-4 hours)
- Full ECU read via IAW5xReader (read twice, compare byte-for-byte)
- Triple backup to separate storage locations
- Analyze scrambled maps — identify what ChatGPT changed
- Read DTCs

### Phase 3: Stock Map Sourcing (2.5-9 hours)
- 4-tier search: exact match → fuzzy → cousin platform → web/forums. If all fail → PROFESSIONAL TUNER REQUIRED
- Validate sourced map (file size, checksum, safety bounds, compatibility)
- **GO/NO-GO:** If no stock map found → PROFESSIONAL TUNER REQUIRED

### Phase 4: Map Recovery & Flash (30-60 min)
- Pre-flash safety gate (10-point checklist, all must be YES — see Section 6.3)
- Flash stock map via IAW5xWriter
- Verify flash (read-back byte comparison)
- Clear DTCs and adaptive learning values
- **Rollback:** Re-flash scrambled backup if verification fails

### Phase 5: Post-Flash Verification (1-1.5 hours)
- Static checks (fuel pump primes, no new DTCs, sensor readings plausible)
- First start (30 sec observation: exhaust color, idle RPM, stability)
- Warm idle assessment (lambda oscillation, fuel trims, timing)
- Short road test (conditional — low speed, no full throttle)
- **GO/NO-GO:** Red-hot manifold → KILL ENGINE → wrong map for hardware

### Phase 6: Iterative Tuning (7-14 hours)
- Install wideband O2 sensor (~150-300 EUR)
- Fuel map adjustment based on wideband data (2-5% steps)
- Ignition timing verification
- Idle quality fine-tuning
- **PROFESSIONAL HELP RECOMMENDED** for dyno tuning (300-600 EUR)

### Phase 7: Mechanical Follow-Up (1 hour)
- Re-assess clutch (may have been ECU-caused symptoms)
- Verify cardan shaft with correct engine operation
- Exhaust system damage assessment (catalyst may be destroyed)

### Phase 8: Final Validation & Sign-Off (2 hours)
- Extended road test covering all conditions
- Final DTC check and data log
- Documentation and archive of all files
- Safety sign-off

**Total estimated time: 20-37 hours**
**Estimated parts cost: 500-2000 EUR (worst case)**
**Professional tuning (if needed): 300-600 EUR**

---

## 9. Gilera GP800 Technical Reference Summary

### Engine
- Type: 90-degree V-twin, liquid-cooled, 4-stroke, SOHC 4v/cyl
- Displacement: 839.3cc (76mm bore x 92.5mm stroke)
- Compression: 10.5:1
- Power: 56kW (75HP) @ 7,500 RPM
- Torque: 76Nm @ 6,000 RPM
- Spark plugs: NGK CR9EK x4 (twin-spark, 2 per cylinder)
- ECU: Magneti Marelli IAW 5AM
- Protocol: K-Line ISO 9141-2 (NOT standard OBD2)

### ECU Map Tables
- **Fuel maps** — separate per cylinder (front/rear), 3D: RPM x TPS, values in ms. **TODO: Confirm 8-bit vs 16-bit storage from actual ECU dump — SafetyGuard limits must match**
- **Ignition maps** — separate per cylinder, 3D: RPM x load, values in deg BTDC
- **Idle control** — target RPM by coolant temp, stepper motor duty
- **Lambda targets** — stoich at cruise, rich (0.85-0.88) at WOT
- **Rev limiter** — stock ~8500 RPM hard cut
- **Temperature corrections** — coolant and intake air compensation
- **Acceleration enrichment** — transient fuel based on TPS rate
- **Injector dead time** — battery voltage correction

### IAW 5AM Safety Ranges (Two Tiers)

**Tuning guidance** (stay within these for good results):
- **Fuel:** +/- 10-15% from stock. Target lambda 0.85-0.88 at WOT
- **Ignition:** +/- 2-3 degrees from stock. NEVER >5 degrees advance over stock at high load
- **Idle:** 1100-1400 RPM warm. Timing 10-14 deg BTDC
- **WOT targets:** Lambda 0.85-0.88 (AFR 12.5-13.0)

**Hard limits** (exceeding these risks hardware damage — SafetyGuard enforces):
- **Fuel map raw values:** 0-255 (scaling: value * conversion_factor = milliseconds; factor defined in `schemas/map-definitions.json`)
- **Ignition advance absolute max:** 45 deg BTDC (detonation risk on 95 RON)
- **Idle RPM range:** 1100-1500
- **Lambda target at WOT:** minimum 0.82 (below = fouling), maximum 1.05 (above = lean misfire)
- **Rev limiter:** 8000-9500 RPM (stock ~8500)
- **Injector duration max:** 12.0 ms

**Note:** `schemas/safe-ranges.json` is the single source of truth. Both the CLI tool and skill reference this file. Tuning guidance and hard limits are separate fields per parameter.

### Key Torque Specifications (Nm) — verify against service manual

| Component | Torque (Nm) |
|-----------|------------|
| Spark plugs | 12 |
| Oil drain plug | 30 |
| Cardan shaft flange bolts | verify from manual |
| Exhaust manifold nuts | 20-25 |
| Wheel axle nut | 120 |
| Throttle body clamps | hand-tight + 1/4 turn |

**Note:** Full torque specs must be populated in `knowledge/reference/torque-specs.md` from the service manual. The above are approximate starting values.

### GP800 vs SRV850 Key Differences
- **ABS:** SRV850 has 2-channel Continental ABS; GP800 does not
- **ECU calibration:** Different fuel/ignition maps for different exhaust/intake
- **Bodywork:** Completely different styling
- **Dashboard:** Different instrument cluster
- **Parts interchangeability:** Most mechanical parts are direct-fit; ECU/sensors may differ in calibration

### Common IAW 5AM Error Codes

| Code | Description |
|------|-------------|
| 11 | ECT sensor open/short |
| 12 | IAT sensor open/short |
| 13 | MAP sensor out of range |
| 14 | TPS out of range |
| 21 | O2 sensor no activity |
| 22/23 | Injector 1/2 circuit |
| 24/25 | Ignition coil 1/2 circuit |
| 33 | CKP sensor no signal |
| 42 | Side-stand switch circuit |
| 44 | Immobilizer communication error |

---

## 10. IAW 5AM File Format (Implementation Reference)

**Note:** Exact memory offsets and scaling factors must be derived from the owner's actual ECU dump using IAW5xReader's map identification output, or from community-sourced definition files (.xdf for TunerPro, .a2l for WinOLS). The values below are approximate based on known IAW 5xx family characteristics.

### Binary Format (.bin)
- **Expected file size:** 256KB or 512KB (depends on flash chip revision — SafetyGuard must verify)
- **Byte order:** Little-endian (Intel format)
- **Map storage:** Maps stored as arrays of 8-bit or 16-bit unsigned integers at fixed addresses
- **Fuel map values:** 16-bit unsigned, divided by scaling constant to yield milliseconds
- **Ignition values:** 8-bit or 16-bit signed, scaled to yield degrees BTDC
- **Checksum:** Located at a known fixed offset (typically end of flash region). Algorithm must be reverse-engineered from IAW5xReader behavior or community documentation. **Implementation note:** IAW5xWriter handles checksum recalculation on write — the CLI tool should verify checksums match after round-trip but does not need to recalculate them.

### Text Format (.txt — IAW5xReader/Writer export)
- **Encoding:** Windows-1252 or UTF-8 (detect and normalize)
- **Decimal separator:** May be comma or period depending on system locale (CRITICAL — must detect and normalize)
- **Structure:**
  ```
  [Map Name / Description Header]
  X-axis values (RPM breakpoints): 750, 1000, 1500, 2000, ..., 8500
  Y-axis values (TPS% or load): 0, 5, 10, 20, 30, 50, 75, 100
  Data grid: rows of numeric values (one row per Y-axis value)
  [Next map...]
  ```
- **Typical map dimensions:** 16x16 or 16x12 cells (RPM x load) — verify from actual export

### Implementation Strategy
1. Parse the owner's existing .txt files to discover the actual format
2. Build the parser iteratively from real data, not from assumptions
3. Store discovered format details in `schemas/map-definitions.json`
4. Validate by round-trip testing: parse → export → parse → diff must be empty

---

## 11. Physical Inspection Requirements (Cannot Be Software-Validated)

**Note:** Sections 11-14 are renumbered from the original spec to eliminate duplicate section numbers.

Items that CANNOT be validated by software — must be physically inspected:

1. **Injector part numbers** — read physically off the injectors
2. **Wiring integrity** — verify ECU swap wiring pin-by-pin
3. **Fuel pressure** — measured with physical gauge
4. **Exhaust system** — visual inspection for leaks, cracks, catalyst condition
5. **Spark plug reading** — pull and inspect (tan=good, white=lean, black=rich)
6. **Coolant system pressure test** — head gasket integrity
7. **Compression test** — both cylinders, 11-14 bar expected, min 10.5 bar serviceable
8. **Sensor identification** — verify which sensors are installed (GP800 or SRV850?)
9. **Battery voltage under load** — affects injector dead time
10. **Fire extinguisher present** — required for any engine start with modified maps

---

## 12. Emergency Workflow

**Hardware constraint:** The IAW 5AM uses K-Line at 10.4 kbaud. There is no automated real-time engine control or instant rollback capability. All emergency procedures are **human-executed**.

**Scenario: Post-flash, exhaust begins glowing red or flames appear**

```
STEP 1: OWNER KILLS ENGINE IMMEDIATELY (ignition off or kill switch)
        DO NOT wait. DO NOT try to "let it settle." OFF immediately.

STEP 2: DO NOT RESTART for at least 10 minutes (let exhaust cool)

STEP 3: Report symptoms to Diagnostician agent
        → Agent determines: was this a map problem or mechanical?

STEP 4: If map problem suspected:
        → Connect IAW5xWriter
        → Flash the verified pre-flash backup
        → Verify via read-back (byte comparison)
        → Estimated time: 5-10 minutes for flash

STEP 5: After successful rollback:
        → Restart engine with caution (same post-flash checklist)
        → If symptoms persist after rollback to known-good map:
          problem is MECHANICAL, not ECU → Diagnostician re-evaluates

STEP 6: If rollback flash FAILS (write error, checksum mismatch):
        → DO NOT attempt to start engine
        → ECU may need recovery via BDM/boot mode
        → PROFESSIONAL HELP REQUIRED
```

**Owner must memorize before ANY flash session:**
1. Kill switch location (instant engine off)
2. Fire extinguisher location (within arm's reach)
3. "If exhaust glows or flames appear: OFF immediately, no exceptions"

---

## 13. Knowledge Base Growth Strategy

1. **Foundation (NOW):** Create directory structure, populate schemas from research
2. **Population (Weeks 1-4):** Owner creates ECU backup, extract service manual specs, document wiring
3. **Enrichment (Ongoing):** Web research harvests forum data, community maps validated and indexed
4. **Self-Improvement:** After every session, log knowledge gaps for future filling

---

## 14. Success Criteria

The system is complete when:
- [ ] Owner can start the bike reliably (hot and cold)
- [ ] Idle is stable, no stalling at traffic lights
- [ ] No exhaust glowing or flames
- [ ] Smooth progressive power delivery
- [ ] No detonation under load
- [ ] Full throttle sustained without power loss
- [ ] Temperature remains stable
- [ ] No DTCs
- [ ] All map files backed up and versioned
- [ ] Owner understands what was done and has all files

---

*This specification was developed through 2 iterations of multi-agent review involving 12 specialized agent perspectives. All findings have been synthesized and validated for internal consistency.*
