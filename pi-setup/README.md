# GP800 Pi Setup

Raspberry Pi 4 als on-bike ECU gateway — USB-KKL → Pi → Tailscale → iPhone.

## Architectuur

```
iPhone (Safari)
    │  Tailscale + 4G
    ▼
Raspberry Pi 4
    │  FastAPI :8000  (gp800-tool serve)
    │  SSE live data  /live/stream
    │  REST API       /dtcs  /validate  /logs
    │
    │  USB (FTDI)
    ▼
ECU  IAW 5AM  (K-Line ISO 9141-2 @ 10.4 kbaud)
```

## Snelle installatie

```bash
# 1. Repo clonen op de Pi
git clone https://github.com/arlayni/gilera-gp800.git
cd gilera-gp800

# 2. USB-KKL adapter inprikken en poort controleren
ls /dev/ttyUSB*

# 3. Setup draaien (als niet-root)
#    Zet eventueel de juiste poort vooraf:
export GP800_PORT=/dev/ttyUSB0
bash pi-setup/setup.sh

# 4. Herstart voor dialout groep
sudo reboot
```

## Handmatig starten (zonder systemd)

```bash
source ~/gp800-venv/bin/activate
gp800-tool serve /dev/ttyUSB0
# → Dashboard: http://localhost:8000
```

## API endpoints

| Method | Pad | Omschrijving |
|--------|-----|--------------|
| GET | `/` | iPhone dashboard (HTML) |
| GET | `/status` | Verbindingsstatus + ECU info |
| POST | `/connect` | Verbind met ECU |
| POST | `/disconnect` | Verbreek verbinding |
| GET | `/live` | Huidig sensor frame (JSON) |
| GET | `/live/stream` | SSE stream (1Hz) |
| GET | `/dtcs` | Lees foutcodes |
| DELETE | `/dtcs` | Wis foutcodes |
| POST | `/validate` | Upload + valideer map file |
| GET | `/logs` | Lijst data logs |
| GET | `/logs/{file}` | Download log JSONL |
| GET | `/docs` | Swagger UI |

## Tailscale

```bash
# Installeer op Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Daarna bereikbaar op iPhone via:
http://<pi-hostname>:8000
```

## Systemd beheer

```bash
sudo systemctl status gp800-api
sudo systemctl restart gp800-api
sudo journalctl -u gp800-api -f
```
