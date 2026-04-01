# Current Bike State & Active Symptoms

**Date:** 2026-03-21
**Safety Status:** DO NOT RIDE — Severity 5 Fire Risk

## Engine Running Symptoms

### Idle & Start Behavior
- **Rough idle** with noticeable vibration and instability
- **Stalling after start** — engine dies within seconds of cold start
- **Stalling at traffic lights** — cannot maintain idle at stops
- **Difficulty restarting** after stall

### Load & Throttle Response
- **Power loss at full throttle** after ~2 minutes of sustained acceleration
- Symptoms suggest fuel mixture issue or ignition cut-off
- Cannot reach redline without power cut

### Exhaust & Fuel Mixture Indicators
- **Red-hot muffler** visible during operation
- **Flames from exhaust** observed when idling at home
- These symptoms are classic indicators of **excessively rich fuel mixture** (running too much fuel, not enough air)

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

## Next Steps

1. Obtain baseline ECU maps for SRV850 (Aprilia OEM or Gilera GP800 equivalent)
2. Perform baseline measurements to verify sensors are reading correctly
3. Flash correct maps to ECU
4. Test idle and light throttle operation before any load testing
5. Verify all wiring from SRV850 installation is correct (see `srv850-to-gp800-wiring.md`)
