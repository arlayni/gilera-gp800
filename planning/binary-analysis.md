# IAW 5AM Binary Layout Analysis

**Date:** 2026-04-02
**Files analyzed:**
- `map-files/original/Gilera_GP800_original.bin` (GP800, 327,680 bytes, SHA256: 53ccb34f...)
- `map-files/working/vandaaggp800.bin` (SRV850, 327,680 bytes, SHA256: 481bdc70...)

## ECU Identity Block

Located by searching for `b"IAW5AM"` marker (found at ~0x47FB8):
- Hardware ID: 16 bytes at marker offset
- Homologation: 8 bytes at marker+16
- Software ID: 12 bytes at marker-35
- Drawing number: 14 bytes at marker-21

## Confirmed Axes

### Main Tuning Axes
| Name | Offset | Count | Values | Notes |
|------|--------|-------|--------|-------|
| RPM-20 | 0x49AA8 | 20 | [524,730,800,850,950,1050,1150,1260,1400,1580,1700,1850,2200,2500,3000,3700,4500,5500,6800,8200] | Main fuel/injection axis |
| RPM-32 | 0x4CD8E | 32 | [1000..8650] | Most detailed RPM axis |
| RPM-16 | 0x4CDCE | 16 | [1000..8500] | Secondary RPM axis |
| TPS-12 | 0x4A510 | 12 | [0,5,10,20,30,40,50,60,70,80,90,100] | 0-100% throttle |
| TPS-17 | 0x4CEB2 | 17 | [0,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85] | Finer throttle resolution |
| TPS-9 | 0x4C5F2 | 9 | [0,10,30,50,80,110,140,150,170] | Raw TPS values (not %) |

### Other Axes
| Name | Offset | Count | Values | Notes |
|------|--------|-------|--------|-------|
| RPM-21 | 0x4CCF4 | 21 | [0,550,650,750...8200] | Leading 0 + 20 real values |
| RPM-10a | 0x4CD46 | 10 | [540..4200] | Low/mid RPM range |
| RPM-10b | 0x4CD5A | 10 | [1000..8200] | Full RPM range, coarse |
| RPM-16c | 0x4CDEE | 16 | [3500..8500] | High RPM only |
| RPM-16d | 0x4D58E | 16 | [1000..3000] | Idle/low RPM range |

## Confirmed Tables

### Main Fuel Injection Table
- **Offset:** 0x4D106
- **Dimensions:** 20 columns × 50 rows (likely 25 front + 25 rear cylinder)
- **X-axis:** RPM-20 @ 0x49AA8
- **Y-axis:** TBD (need to identify TPS/load axis for this table)
- **Value type:** 16-bit LE, injection pulse width (µs), range 0-8000
- **Ends at:** 0x4D8D6
- **Followed by:** all-500 block (uniform correction/padding)
- **GP800 vs SRV850:** Every cell differs (expected — different engines)

### Idle RPM Target Table
- **Offset:** ~0x4DE00-0x4E100
- **Detected by:** heuristic scan for blocks where all values 500-1500
- **Value type:** RPM

## Biggest Diff Regions (calibration area only)
| Region | Size | Notes |
|--------|------|-------|
| 0x4D7AA-0x4DE5A | 1712 bytes | Inside/after fuel table |
| 0x4D456-0x4D77F | 809 bytes | Inside fuel table |
| 0x4DE6E-0x4E191 | 803 bytes | Idle RPM area |
| 0x4A8D2-0x4AB63 | 657 bytes | Unknown (potential ignition?) |
| 0x4A6C3-0x4A861 | 414 bytes | Unknown (potential ignition?) |
| 0x4E41A-0x4E5C8 | 430 bytes | Post-idle area |
| 0x4F155-0x4F319 | 452 bytes | Late calibration area |

## Open Questions
1. **Front/rear split:** Is 0x4D106 one table (50 rows) or two (25+25)? Value pattern analysis needed.
2. **Ignition tables:** Not yet located. Likely in 0x4A6C3-0x4AB63 region. Values would be 0-500 (degrees × 10).
3. **Lambda target table:** Not yet located.
4. **Y-axis for fuel table:** Which TPS axis (12, 17, or 9-point) pairs with this table?
5. **8-bit vs 16-bit storage:** Confirmed 16-bit LE for fuel table.
6. **Checksum algorithm:** Not yet determined. Location and method unknown.

## DDG Format
- **Encrypted:** Entropy 7.82 bits/byte (near random) vs 5.39 for raw .bin
- **Size:** 327,840 bytes (+160 vs .bin) and 327,871 bytes
- **No simple XOR, no recognizable header**
- **Conclusion:** Proprietary MelcoDiag/IAW5Writer encryption, not feasible to reverse-engineer
