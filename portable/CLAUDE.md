# GP800 Tool — Portable ECU Diagnostics

Draagbare versie van het Gilera GP800 ECU diagnostiek systeem.
Draait vanaf USB stick op de laptop, naast de motor.

## Quick Start

```bash
# Verbind USB-KKL adapter met motor (3-pin connector)
# Zet contactsleutel op AAN, motor UIT

gp800-tool connect COM3              # Windows (of /dev/ttyUSB0 op Linux)
gp800-tool read COM3 backup.bin      # Lees ECU → backup
gp800-tool bindump backup.bin        # Analyseer
gp800-tool dtc COM3                  # Foutcodes lezen
gp800-tool live COM3                 # Live sensor data

# Bewerken
gp800-tool bin2txt backup.bin maps.txt
# Edit maps.txt
gp800-tool txt2bin maps.txt backup.bin modified.bin
gp800-tool validate modified.bin     # Safety check
gp800-tool flash COM3 modified.bin   # Flash (met safety gate)

# EEPROM (CO trim, TPS, immobilizer)
gp800-tool eeprom COM3 eeprom_backup.eep
```

## Safety Rules
- **ALTIJD backup maken voor je iets wijzigt**
- Flash weigert automatisch bij safety violations (BLOCKER)
- Batterij moet >12.0V zijn bij flashen
- Contactsleutel AAN, motor UIT bij alle ECU communicatie

## Hardware
- USB-KKL adapter (FTDI chip) + 3-pin Piaggio/Aprilia kabel
- K-Line ISO 9141-2 @ 10.4 kbaud
