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

## Root Cause Assessment

**Primary cause:** Scrambled ECU maps from failed ChatGPT-assisted tuning attempt
- No backup of pre-ChatGPT maps available
- Maps require complete reconstruction or baseline replacement

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
