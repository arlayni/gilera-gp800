# Gilera GP800 — ECU Diagnostics & Safety-Critical Knowledge Base

Motorcycle ECU diagnostiek en herstel voor een Gilera GP800 met scrambled Magneti Marelli IAW 5AM.

## 1. Wat is dit?

Safety-critical kennisbank + Python CLI tool voor ECU map analyse, validatie, en vergelijking. 7 sub-agents met Safety Guard VETO authority.

## Context Management
**GEEN compactie — NOOIT.** Compactie vernietigt data. Bij hoge context → dump ALLES naar brein (brain.jsonl) + checkpoint → start nieuwe sessie. Het brein logt ELKE actie automatisch. Geldt voor main session EN alle agents/subagents.

## 2. Hoe draai je het?

```bash
# CLI tool installeren
cd ~/Gilera\ GP800/gp800-tool
pip install --user --no-build-isolation -e ".[dev]"

# Commands
gp800-tool parse <file>              # Map file samenvatten
gp800-tool validate <file>           # Pre-flash safety validatie (.txt map files)
gp800-tool quickcheck <file>         # GO/NO-GO (GREEN/YELLOW/RED) (.txt map files)
gp800-tool compare <file1> <file2>   # Cell-by-cell vergelijking
gp800-tool bindump <file.bin>        # Binary ECU dump inspecteren (.bin files)
gp800-tool bindiff <file1> <file2>   # Binary diff tussen twee .bin files

# Opmerking: validate/quickcheck werken op .txt map files.
#             bindump/bindiff werken op .bin (raw ECU binary) files.

# Tests
pytest

# Beschikbare slash commands
/plan [taak]        — Research eerst, dan uitvoeren
/gsd [project]      — Fased werk met voortgang tracking
/ralph [prd.json]   — Autonome batch-executie
/review [scope]     — Code review (security + quality)
/status             — System health check
```

## 3. Regels & Principes

### SAFETY-FIRST (ABSOLUUT)
**Incorrect maps kunnen de motor vernietigen of de berijder verwonden.**

### 11 Flash Blockers (GEEN override mogelijk)
1. Fuel map bevat all-zero row (lean seizure)
2. Fuel map bevat all-255 row (hydro-lock)
3. Ignition advance > 45° of < -10° bij enige cel
4. Lambda target > 1.05 bij WOT of < 0.82 bij enige cel
5. Injector dead-time niet monotoon dalend met voltage
6. Checksum mismatch na edit
7. File size ≠ verwachte IAW 5AM binary size
8. Geen geverifieerde backup aanwezig
9. Immobilizer PIN niet bevestigd beschikbaar
10. Mechanische pre-check niet gepasseerd
11. Batterijspanning < 12.0V bij flash

### Key Rules
1. **Diagnose voor tuning** — nooit blind tunen
2. **Mechanisch voor ECU** — sluit mechanische issues eerst uit
3. **Backup voor flash** — altijd, geen uitzonderingen
4. **Stock eerst** — start vanuit known-good baseline
5. **Nooit immobilizer data delen** — codes zijn geredacteerd
6. **Schemas zijn autoriteit** — `safe-ranges.json` is single source of truth

### Tuning Filosofie
Stock eerst, conservatieve wijzigingen (max 5% per stap).

## 4. Edge Cases & Bekende Issues

- **Huidige staat: DO NOT RIDE** (Severity 5) — roodgloeiende uitlaat, vlammen, stalling
- **Originele ECU:** Magneti Marelli IAW 5AM (defect — zijstandschakelaar)
- **Huidige ECU:** Aprilia SRV850 IAW 5AM (elektrisch compatibel)
- **Communicatie:** K-Line ISO 9141-2 @ 10.4 kbaud (NIET standaard OBD2)
- **Immobilizer:** REDACTED — codes nooit in output

## 5. Hoe we werken

### Architectuur
```
knowledge/
├── reference/        # Statische technische feiten
├── procedures/       # Stap-voor-stap workflows
└── schemas/          # JSON schemas (single source of truth)

my-bike/              # Owner-specifiek: staat, historie, metingen
map-files/            # original/, stock/, working/, modified/
gp800-tool/           # Python CLI (setuptools package)
```

### Tech Stack
- **Knowledge:** Markdown + JSON schemas
- **CLI:** Python 3.10+, Click, setuptools
- **Testing:** pytest met fixtures
- **Safety:** Expliciete severity levels (INFO/WARNING/BLOCKER)

### Coding Conventions
- Python: type hints, dataclasses, pathlib.Path, f-strings
- Git: conventional commits (feat/docs/fix)
- Tuning: stock first, max 5% per stap

---

## Inventaris

### Agents (7) — `.claude/agents/`
| Agent | Rol | Bijzonder |
|-------|-----|-----------|
| **safety-guard** | Pre-flash validatie, risk scoring | **VETO AUTHORITY** |
| flash-monitor | Post-flash checklist, rollback | |
| diagnostician | Symptoomanalyse, root cause | |
| ecu-engineer | Map analyse, tuning aanbevelingen | |
| mechanical-advisor | Mechanische checks, pre-flight | |
| knowledge-service | Schema queries, documentatie | |
| tuning-advisor | Incrementeel tuning advies | |

### Key Schemas
| Schema | Doel |
|--------|------|
| safe-ranges.json | Hard limits — de safety authority |
| map-definitions.json | Map namen, assen, dimensies |
| sensor-specs.json | Alle sensor specificaties |
| error-codes.json | IAW 5AM DTC codes |
| immobilizer.json | REDACTED |

### Planning
- `planning/roadmap.md` — Project fases en afhankelijkheden
- `planning/state.md` — Voortgang per fase/taak
- Gebruik `/gsd` voor fased werk, `/ralph` voor batch-executie