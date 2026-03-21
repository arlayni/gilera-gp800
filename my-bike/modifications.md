# Bike Modifications & Deviations from Stock

This document lists all deviations from the original GP800 factory configuration.

## Engine Control Unit (ECU)

**Stock Configuration:**
- Gilera GP800 ECU (OEM, failed)

**Current Configuration:**
- **Aprilia SRV850 ECU** (replacement from dealer)
- Same IAW 5AM platform, so electrically compatible
- SRV850 variant includes ABS module integration

**Status:**
- Maps are currently scrambled from failed ChatGPT tuning attempt
- Maps require reconstruction or replacement with known-good baseline
- Key chip codes re-linked by friend after memory loss

## Drivetrain

**Stock Configuration:**
- Original cardan shaft (failed)

**Current Configuration:**
- **Cardan shaft replaced** with new unit by owner
- Installation performed by owner (not independently verified for alignment, balance, or fitment)
- No documentation of replacement source, specifications, or installation procedure

**Status:**
- Bike feels less performant after replacement
- May indicate: incorrect alignment, wrong ratio, balance issue, or torque curve change
- Requires verification and baseline measurements

## Immobilizer System

**Stock Configuration:**
- Original Gilera GP800 immobilizer with factory key codes

**Current Configuration:**
- Key chip codes re-linked to SRV850 ECU by friend
- No second key available (only current key is linked)

**Status:**
- System functional (bike can start with current key)
- No backup key or code recovery documentation available

## Summary of Non-Stock Items

| Component | Stock | Current | Status |
|-----------|-------|---------|--------|
| ECU | GP800 OEM | SRV850 (maps corrupted) | Needs map fix |
| Cardan Shaft | Original | Replaced (unknown source/spec) | Needs verification |
| Immobilizer Codes | Factory linked | Re-linked by friend | Functional, no backup |

## Known Issues from Modifications

1. **ECU Maps:** Scrambled from failed ChatGPT tuning; no backup available
2. **Cardan Replacement:** Owner-installed; not verified for alignment/balance; performance degradation observed
3. **Wiring:** SRV850 ECU may require wiring differences (see `srv850-to-gp800-wiring.md` for investigation checklist)
