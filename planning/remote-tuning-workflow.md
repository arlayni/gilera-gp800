# Remote Tuning Workflow — Claude Code op Laptop + Raspberry Pi

## Overzicht

Claude Code draait op je laptop en communiceert via SSH met de Pi. De Pi is verbonden met de ECU via USB-KKL. Je iPhone toont het live dashboard.

```
ECU ──USB-KKL──► Raspberry Pi ◄──SSH──► Laptop (Claude Code)
                      │
                      └──WiFi──► iPhone (dashboard)
```

---

## Eenmalige Setup

### 1. Pi installeren
```bash
# Op de Pi (via SSH of scherm):
git clone <repo> ~/gilera-gp800
cd ~/gilera-gp800/pi-setup
./setup.sh
sudo reboot
```

### 2. Laptop configureren
```bash
# Op je laptop, vanuit de project map:
./pi-setup/laptop-setup.sh raspberrypi.local pi
```
Dit doet: SSH key aanmaken, kopiëren naar Pi, alias instellen, tune-session.sh installeren.

### 3. Claude Code installeren
```bash
npm install -g @anthropic-ai/claude-code
```

---

## Tuning Sessie Starten

### Stap 1 — Live data starten
```bash
# Terminal 1: live data op Pi starten
ssh gp800-pi './tune-session.sh start'

# Terminal 2: live data bekijken op laptop
ssh gp800-pi './tune-session.sh log'
```

### Stap 2 — Claude Code starten
```bash
# In de gilera-gp800 project map:
claude
```

### Stap 3 — ECU map ophalen
Claude voert dit uit:
```bash
ssh gp800-pi './tune-session.sh read'
scp gp800-pi:/tmp/current.bin map-files/working/current_$(date +%Y%m%d_%H%M).bin
```

### Stap 4 — Analyseren
Claude leest:
- De huidige ECU map (`current.bin`)
- De live sensorlogs (lambda, RPM, TPS, watertemperatuur)
- `knowledge/schemas/safe-ranges.json` voor limieten

Claude identificeert welke brandstofcellen te mager of te rijk zijn op basis van lambda-afwijking.

### Stap 5 — Aanpassen en valideren
Claude past de map aan (max 5% per stap) en valideert:
```bash
gp800-tool validate map-files/working/proposed.bin
gp800-tool quickcheck map-files/working/proposed.bin
gp800-tool compare map-files/working/current.bin map-files/working/proposed.bin
```

### Stap 6 — Flashen (motor UIT)
```bash
scp map-files/working/proposed.bin gp800-pi:/tmp/proposed.bin
ssh gp800-pi './tune-session.sh flash /tmp/proposed.bin'
```

### Stap 7 — Testen en herhalen
Motor starten → testrit → live data bekijken → terug naar stap 4.

---

## Handige SSH Commando's

```bash
# Pi status
ssh gp800-pi './tune-session.sh status'

# Foutcodes uitlezen
ssh gp800-pi './tune-session.sh dtc'

# Foutcodes wissen
ssh gp800-pi './tune-session.sh clear-dtc'

# Snel bestand valideren op Pi
ssh gp800-pi './tune-session.sh validate /tmp/proposed.bin'

# Live API dashboard (iPhone of laptop browser)
# http://raspberrypi.local:8000
```

---

## Veiligheidsregels bij Remote Tuning

1. **Motor UIT bij flashen** — nooit flashen terwijl motor draait
2. **Backup altijd eerst** — `read` uitvoeren voor elke wijziging
3. **Max 5% per stap** — kleine stapjes, testen, dan verder
4. **Validatie is verplicht** — tune-session.sh flash blokkeert bij validatiefout
5. **Batterijspanning > 12.0V** — controleer voor flashen
6. **Stock map bewaard** — `map-files/original/` nooit overschrijven

---

## Troubleshooting

| Probleem | Oplossing |
|---------|-----------|
| SSH verbinding weigert | `ping raspberrypi.local` — zelfde netwerk? |
| `/dev/ttyUSB0` niet gevonden | `ls /dev/ttyUSB*` op Pi, andere poort? |
| Pi niet bereikbaar via naam | Gebruik IP-adres: `ssh pi@192.168.1.x` |
| Tailscale onderweg | `ssh pi@<tailscale-ip>` i.p.v. `.local` |
| Validatie blokkeert | Lees de foutmelding — nooit forceren |

---

## Bestandsstructuur tijdens sessie

```
gilera-gp800/
└── map-files/
    ├── original/          ← nooit wijzigen
    │   └── stock.bin
    └── working/
        ├── current_20260511_1400.bin   ← van Pi gelezen
        ├── proposed_v1.bin             ← Claude voorstel
        └── proposed_v1_validated.bin   ← na validatie
```
