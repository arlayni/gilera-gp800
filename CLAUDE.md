# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gilera GP800 ECU Diagnostics** — A safety-critical knowledge base and tooling system for diagnosing and recovering a Gilera GP800 motorcycle with a scrambled ECU (Magneti Marelli IAW 5AM). The bike was incorrectly tuned using ChatGPT-generated map values, resulting in dangerous symptoms.

**Status:** Knowledge base complete, Python CLI tool implemented, Claude Code skill framework designed (implementation pending).

## Safety-First Principle

**CRITICAL:** This project deals with motorcycle ECU flashing. Incorrect maps can destroy the engine or cause rider injury. The core design principle is: **make it harder to flash a dangerous map than a safe one.**

### Flash Blockers (ABSOLUTE — no override)

These conditions MUST prevent any map from being flashed:
1. Fuel map contains all-zero row (lean seizure)
2. Fuel map contains all-255 row (hydro-lock)
3. Ignition advance > 45 deg or < -10 deg at any cell
4. Lambda target > 1.05 at WOT or < 0.82 at any cell
5. Injector dead-time not monotonically decreasing with voltage
6. Checksum mismatch after edit
7. File size != expected IAW 5AM binary size
8. No verified backup exists
9. Immobilizer PIN not confirmed available
10. Mechanical pre-check not passed
11. Battery voltage < 12.0V at time of flash

## Architecture

```
knowledge/
├── reference/        # Static technical facts (engine, ECU, fuel, ignition, sensors)
├── procedures/       # Step-by-step diagnostic and tuning workflows
└── schemas/          # JSON schemas — single source of truth for all limits and specs

my-bike/              # Owner-specific: current state, history, modifications, measurements

map-files/
├── original/         # Unmodified ECU dumps
├── stock/            # OEM baseline maps
├── working/          # Current analysis copies
└── modified/         # Modified maps with change records

gp800-tool/           # Python CLI tool (setuptools package)
├── src/gp800_tool/   # Parser, validator, comparator, exporter, CLI
└── tests/            # pytest test suite
```

## The Bike

- **Model:** Gilera GP800 (V-twin, 839cc, 75HP, twin-spark)
- **Original ECU:** Magneti Marelli IAW 5AM (failed — side-stand switch fault)
- **Current ECU:** Aprilia SRV850 IAW 5AM (electrically compatible)
- **Communication:** K-Line ISO 9141-2 @ 10.4 kbaud (NOT standard OBD2)
- **Current state:** DO NOT RIDE (Severity 5) — red-hot exhaust, flames, stalling, rough idle

## Commands

### Run CLI tool
```bash
cd ~/Desktop/"Gilera GP800"/gp800-tool
pip install -e .
gp800-tool parse <file>           # Parse and summarize map file
gp800-tool validate <file>        # Run pre-flash safety validation
gp800-tool quickcheck <file>      # Quick go/no-go (GREEN/YELLOW/RED)
gp800-tool compare <file1> <file2> # Cell-by-cell comparison
gp800-tool export <file> <output>  # Export to .txt format
```

### Run tests
```bash
cd ~/Desktop/"Gilera GP800"/gp800-tool
pip install -e ".[dev]"
pytest
```

## Tech Stack

- **Knowledge base:** Markdown + JSON schemas
- **CLI tool:** Python 3.10+, Click CLI framework, setuptools
- **Dependencies:** `click>=8.0`, `pytest>=7.0` (dev), `matplotlib>=3.5` (optional viz)
- **Testing:** pytest with fixtures in conftest.py
- **Version control:** Git

## Key Schemas (knowledge/schemas/)

| Schema | Purpose |
|--------|---------|
| safe-ranges.json | Hard limits for all tunable parameters — the safety authority |
| map-definitions.json | Map names, axes, dimensions |
| sensor-specs.json | All sensor specifications (20.5KB) |
| error-codes.json | IAW 5AM DTC codes |
| immobilizer.json | REDACTED — key codes never shared |
| diagnostic-report.schema.json | Inter-agent communication protocol |

## Python Code Structure (gp800-tool/src/gp800_tool/)

| Module | Purpose |
|--------|---------|
| cli.py | Click-based CLI with 6 commands |
| models.py | Dataclasses: MapTable, MapFile, ValidationResult, ComparisonCell |
| parser.py | IAW5xReader/Writer .txt format parser |
| schemas.py | Schema loader — reads safe-ranges.json as source of truth |
| validator.py | Pre-flash safety validation engine |
| comparator.py | Cell-by-cell map comparison with severity ranking |
| exporter.py | Export to IAW5xWriter-compatible .txt format |

## Expert Agent System (Planned)

```
COORDINATOR (router, workflow enforcer)
├── SafetyGuard (VETO AUTHORITY — validation, risk scoring)
├── FlashMonitor (post-flash checklist, manual rollback)
├── Diagnostician (symptom analysis, root cause)
├── ECU Engineer (map analysis, tuning recommendations)
├── Mechanical Advisor (pre-flight checks, mechanical issues)
└── Knowledge Service (schema queries, documentation)
```

## Coding Conventions

- **Python:** Type hints, dataclasses, pathlib.Path, modern f-strings
- **Testing:** pytest with fixtures; sample data in conftest.py
- **Git commits:** Conventional format (feat/docs/fix prefixes)
- **Documentation:** Markdown with tables and code blocks
- **Safety:** Explicit severity levels (INFO, WARNING, BLOCKER) in all validation
- **Tuning philosophy:** Stock first, conservative changes (max 5% per step)

## Key Rules

1. **Diagnose before tuning** — never tune blindly
2. **Mechanical before ECU** — rule out mechanical issues first
3. **Backup before flash** — always, no exceptions
4. **Stock first** — start from known-good baseline
5. **Never share immobilizer data** — codes are redacted in all files
6. **Schemas are the authority** — safe-ranges.json is the single source of truth for limits
