# Bricked ECU Recovery — BDM / Boot Mode Recovery

## Overview

If the ECU becomes unresponsive via normal K-Line (IAW5xReader/Writer cannot connect), it may be necessary to use BDM (Background Debug Mode) or boot mode to recover the ECU at a lower level.

**This is a last resort.** Before assuming the ECU is bricked, work through the normal connection troubleshooting checklist below.

---

## Is the ECU Actually Bricked?

Most "ECU won't connect" situations are NOT a bricked ECU. Check these first:

| Check | Expected |
|-------|----------|
| Battery voltage | >12.0V |
| K-Line cable connected correctly | |
| IAW5xReader software recognizes adapter | |
| Correct COM port selected | |
| Ignition ON (not just key in) | |
| Engine OFF (some operations require engine off) | |
| No active immobilizer fault (Code 44) | |
| ECU ground connections good | <0.5 Ohm |

If all above are correct and software still cannot connect: proceed to deeper investigation.

---

## Normal Connection Recovery Steps

1. Disconnect battery for 10 minutes (ECU power reset)
2. Reconnect and retry IAW5xReader
3. Try a different K-Line cable if available
4. Verify K-Line connector pin at ECU connector (see [wiring.json](../schemas/wiring.json) when populated)
5. Verify K-Line diagnostic connector location on the bike (TODO: document location)

---

## Failed Flash Recovery (Map Corrupt, ECU Still Responds)

If IAW5xReader can still connect but the ECU has a corrupt map:
1. Attempt to write known-good backup map via IAW5xWriter
2. Verify write by reading back and comparing SHA256
3. This is the most common recovery scenario and does not require BDM

---

## BDM / Boot Mode Recovery

**When required:** ECU firmware is corrupt or unresponsive to K-Line. ECU hardware is functional.

**What it is:** BDM (Background Debug Mode) is a hardware-level debug interface on Motorola/Freescale processors. Boot mode bypasses the application firmware and allows direct flash of the processor.

**Hardware required:**
- BDM adapter (specific to IAW 5AM processor — TODO: document exact adapter type)
- BDM software (TODO: document compatible software)
- Access to ECU board (requires ECU disassembly)

**Procedure:**
TODO — This procedure requires:
1. ECU disassembly to access BDM header pins
2. Correct BDM adapter and software
3. Original firmware binary for the IAW 5AM (not the same as calibration/map files)
4. Documentation of the specific processor variant used in the SRV850 ECU

**WARNING:** Incorrect BDM procedure can permanently destroy the ECU. Do not attempt without verified documentation for this specific ECU variant.

---

## When to Stop and Call a Professional

Stop and get professional help when:

- Normal K-Line recovery does not work after all connection checks
- BDM is required and you do not have verified documentation for this specific ECU
- Only one ECU is available and no backup exists
- The ECU shows signs of physical damage (burned smell, corroded board)
- The immobilizer is involved in the failure (immobilizer bypass has legal implications)

**Professional resources:**
- Authorized Piaggio / Aprilia dealer with IAW 5AM ECU programming capability
- Specialist ECU repair services with experience in Magneti Marelli IAW series
- Aprilia / Gilera forum communities with experienced members

**Note:** Trailering the bike to a professional tuner is always preferred over riding on a suspect map, even if the map appears to be "working well enough."

---

## Backup Strategy (Prevention)

The current situation exists partly because no backup was made before the ChatGPT tuning attempt. Going forward:

1. Before any flash: read current ECU and save file with timestamp and SHA256 hash
2. Keep multiple backup copies in different locations (local + cloud)
3. Document the SHA256 hash in a separate text file alongside the backup
4. Never flash without a verified backup from THIS session (not a weeks-old backup)

---

## File Locations

Map backups should be stored in:
- `map-files/original/` — original dumps, never modified
- `map-files/working/` — current working copy
- `map-files/stock/` — OEM stock maps

---

## Related Files

- [iaw5x-reader-writer.md](iaw5x-reader-writer.md) — normal read/write procedure
- [tuning-workflow.md](tuning-workflow.md) — flash safety sequence
- [electrical.md](../reference/electrical.md) — ECU connector and battery specs
- [ecu-iaw5am.md](../reference/ecu-iaw5am.md) — ECU architecture

---

*TODO: Document BDM adapter type, BDM software, processor variant, ECU board layout, and diagnostic connector location from ECU hardware research.*
