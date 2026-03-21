# OBD Diagnostics — NOT Standard OBD2

## Important Warning

**The Gilera GP800 and Aprilia SRV850 with IAW 5AM ECU do NOT use standard OBD2 (SAE J1979 / ISO 15765 CAN).**

Standard OBD2 scanners, ELM327 adapters, and generic OBD2 apps will NOT work with this ECU.

---

## The Actual Protocol

| Parameter | Value |
|-----------|-------|
| Protocol | K-Line ISO 9141-2 |
| Baud rate | 10,400 baud |
| Physical layer | Single-wire K-Line |
| Application layer | Piaggio/Magneti Marelli proprietary |
| Physical connector | Piaggio/Aprilia diagnostic connector (not standard OBD2 16-pin) |

---

## Compatible Tools

### Confirmed Compatible

| Tool | Notes |
|------|-------|
| IAW5xReader/Writer | Owner has this hardware; primary tool for this bike |
| Piaggio Diagnostic System (PDS) | Official dealer tool; expensive but comprehensive |
| Axone diagnostic tools | Piaggio Group compatible; dealer-grade |

### NOT Compatible

| Tool | Why |
|------|-----|
| Standard ELM327 OBD2 adapter | Wrong protocol |
| Generic OBD2 Bluetooth adapters | Wrong protocol |
| Standard OBD2 scan tools | Wrong protocol |
| Any tool requiring CAN bus | IAW 5AM is K-Line, not CAN |

---

## Diagnostic Connector

TODO: Document the location of the K-Line diagnostic connector on the GP800:
- Physical location (under seat? near ECU? behind fairing?)
- Connector type and pin count
- K-Line pin number within the connector
- Whether a separate adapter cable is needed between the bike connector and IAW5x adapter

---

## What You Can Do With IAW5xReader/Writer

- Read and clear DTCs
- Monitor live sensor data (RPM, TPS, MAP, ECT, IAT, lambda, battery, injection time)
- Read full ECU calibration (map tables)
- Write new calibration (flash new maps)

See [iaw5x-reader-writer.md](iaw5x-reader-writer.md) for detailed usage procedures.

---

## K-Line Protocol Notes

- Communication is half-duplex (one direction at a time)
- Full ECU read/write takes several minutes at 10.4 kbaud
- Automated real-time rollback is NOT possible with this hardware
- All rollback requires manually re-flashing a backup file
- Do not interrupt communication mid-operation

---

## Dealer Diagnostics

If IAW5xReader cannot connect or cannot resolve the issue, an Aprilia/Piaggio dealer with PDS (Piaggio Diagnostic System) can:
- Read all fault codes including ABS-related codes
- Reset adaptation values
- Perform throttle body reset / TPS calibration
- Access immobilizer functions

---

## Reading DTCs Without a Computer

The MIL blink code procedure works without any tools. See [error-codes.md](../reference/error-codes.md) for the trigger sequence and how to read blink codes.

---

## Related Files

- [iaw5x-reader-writer.md](iaw5x-reader-writer.md) — full tool usage guide
- [ecu-iaw5am.md](../reference/ecu-iaw5am.md) — ECU and K-Line architecture
- [error-codes.md](../reference/error-codes.md) — DTC reference and MIL blink code procedure

---

*TODO: Document diagnostic connector location, pin diagram, and adapter cable type from physical inspection of the bike.*
