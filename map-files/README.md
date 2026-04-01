# Map Files — Inventaris

## Bestanden

### `original/Gilera_GP800_original.bin`
- **Platform:** Gilera GP800 (IAW 5AM)
- **Software:** 3225AGA41 | **Drawing:** 3584806
- **SHA256:** `53ccb34f1b4cc513...`
- **Bron:** Stock GP800 ECU dump (referentie-baseline)
- **Status:** Dit is NIET de originele dump van deze specifieke motor — die is verloren gegaan toen de originele ECU zichzelf wiste (zijstandschakelaar-defect)

### `working/vandaaggp800.bin`
- **Platform:** Aprilia SRV850 (IAW 5AM)
- **Software:** 34225GAA2 | **Homologatie:** 5AME2A
- **SHA256:** `481bdc70b7cb8199...`
- **Bron:** Uitlezing van de huidige ECU in de GP800
- **Status:** Dit is wat er NU op de motor staat. SRV850 ECU als vervanging voor de defecte GP800 ECU.

### `stock/Gilera_GP800_917cc.ddg`
- **Formaat:** DDG (MelcoDiag/IAW5Writer formaat)
- **Bron:** Stock map voor 917cc variant

### `stock/Gilera_GP800_stock_originale.ddg`
- **Formaat:** DDG
- **Bron:** Stock originele GP800 map

## Opmerking over "modified" bestanden

Eerder stonden hier 7 bestanden met namen als V2, V3, V4, V6, V6.1_lambda_actief, etc.
Deze waren allemaal **byte-identiek** aan `original/Gilera_GP800_original.bin` — geen echte
modificaties. De echte gemodificeerde maps zijn verloren gegaan. De `modified/` map is
beschikbaar voor toekomstige tuning-iteraties.

## Mappenstructuur

```
map-files/
├── original/    # Ongewijzigde ECU dumps (referentie)
├── stock/       # OEM baseline maps (.ddg formaat)
├── working/     # Huidige analyse-kopieën
└── modified/    # Gemodificeerde maps (momenteel leeg)
```
