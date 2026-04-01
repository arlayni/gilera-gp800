# GSD Roadmap — Gilera GP800

## Active Projects

### ECU Recovery
**Goal:** Motor veilig rijdbaar maken (Severity 5 → Severity 0)
**Status:** Diagnose fase

#### Phase 1: Baseline
- [ ] Stock map verkrijgen (OEM Gilera GP800)
- [ ] Huidige map dumpen en analyseren
- [ ] Cell-by-cell vergelijking (stock vs current)
**Verification:** `gp800-tool compare` rapport zonder BLOCKER findings

#### Phase 2: Safe Flash
- [ ] Safety Guard validatie op stock map
- [ ] Mechanical pre-check (11 punten)
- [ ] Flash stock map met rollback plan
**Verification:** `gp800-tool quickcheck` = GREEN

#### Phase 3: Test Ride
- [ ] Stationair: stabiel idle, geen vlammen
- [ ] Lage toeren: soepel gas geven
- [ ] Temperatuur: normaal bereik na 10 min
**Verification:** Diagnostician rapport: alle symptomen resolved

#### Phase 4: Conservative Tuning (optioneel)
- [ ] Baseline meting (dyno of GPS)
- [ ] Max 5% per stap wijzigingen
- [ ] Elke stap: validate → flash → test → measure
**Verification:** Betere performance zonder nieuwe symptoms

---

*Update dit bestand met nieuwe projecten via `/gsd`*