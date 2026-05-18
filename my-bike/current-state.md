# Current Bike State & Active Symptoms

**Date:** 2026-05-18
**Safety Status:** CAUTION — Severity 2 (warm idle stall, niet rijklaar)

## Engine Running Symptoms

### Huidige symptomen (2026-05-18)
- **Warm stationair uitvallen** — motor valt uit bij stationair draaien wanneer warm
- **Gas geven bij afremmen vereist** — zonder gas geven valt motor uit bij afremmen
- Koud starten en draaien werkt normaal

### Opgeloste symptomen
- ~~Roodgloeiende uitlaat~~ — opgelost
- ~~Vlammen uit uitlaat~~ — opgelost
- ~~Stalling direct na koud starten~~ — opgelost

## ECU & Map Status

**Huidige ECU:** Aprilia SRV850 IAW 5AM (vervanging voor defecte GP800 ECU)
- **Uitlezing:** `map-files/working/vandaaggp800.bin` (SHA256: `481bdc70...`)
- **Software:** 34225GAA2 | **Homologatie:** 5AME2A

**Originele GP800 ECU:** Defect — zijstandschakelaar-fout heeft de ECU gewist. Originele dump is verloren.

**Referentie:** `map-files/original/Gilera_GP800_original.bin` — stock GP800 dump (niet van deze motor)

**Gemodificeerde maps (V2–V6.1):** Verloren. De bestanden die onder die namen bestonden waren allemaal identieke kopieën van de stock GP800 dump — de echte modificaties zijn niet bewaard gebleven.

## Root Cause Assessment

**Primary cause:** Scrambled ECU maps from failed ChatGPT-assisted tuning attempt
- No backup of pre-ChatGPT maps available
- Maps require complete reconstruction or baseline replacement
- Original GP800 ECU wiped itself (side-stand switch fault) — original dump lost

**Secondary potential issues:**
- Cardan shaft replacement may have shifted power distribution or torque curve expectations
- Sensor readings need baseline verification (see `baseline-measurements.md`)

## Safety Rating

**Severity: 5 (Critical)**
- Fire risk from excessively hot exhaust and backfiring
- Cannot control idle or throttle reliably
- Not fit for any riding until resolved

## Volgende stappen

1. **Huidige ECU map uitlezen** via `gp800-tool read COM3` en opslaan als nieuwe baseline
2. **DTC's uitlezen** — zoek Code 32 (ISC), 11 (ECT), 14 (TPS)
3. **Live data loggen** bij warm stationair — RPM, lambda, TPS analyseren
4. **Warm idle cellen finetunen** met Claude op basis van live lambda data

## Notities map bestanden
- `map-files/working/vandaaggp800.bin` — VEROUDERD, niet gebruiken
- `map-files/original/Gilera_GP800_original.bin` — stock GP800 referentie (niet van deze motor)
- Nieuwe baseline wordt volgende sessie uitgelezen en opgeslagen
