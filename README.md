# SOTA Hunter

🌐 [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md)

**One click to tune. One click to log. Never leave SOTAwatch.**

SOTA Hunter is a Chrome extension that adds **Tune** and **Log** buttons directly into the [SOTAwatch3](https://sotawatch.sota.org.uk/) spots table — so you can work a summit activation without touching your keyboard or switching windows.

---

## Before / After

| Without SOTA Hunter | With SOTA Hunter |
|---|---|
| ![SOTAwatch without extension](screenshots/without%20extension.png) | ![SOTAwatch with extension](screenshots/with%20enxtension.png) |

---

## What happens when you click

### Tune (blue button)
Sets your **Yaesu FT-DX10** VFO frequency and mode in one click via direct serial CAT — no intermediate software, no CAT-to-TCP bridges.

Correct sideband is chosen automatically:
- SSB → LSB below 7.3 MHz, USB above
- FT8 / FT4 / JS8 / DATA → DATA-U
- CW, FM, AM pass through unchanged

### Log (purple button)
Opens a quick RST dialog, then fires a **complete ADIF QSO record** into HRD Logbook via UDP — exactly the same protocol used by WSJT-X, so no extra configuration is needed beyond enabling QSO Forwarding in HRD.

![RST dialog before logging](screenshots/log.png)

The logged record includes callsign, frequency, band, mode, **SOTA_REF**, summit name and altitude (fetched live from the SOTA API), and your station callsign and grid square.

---

## Features at a glance

| Feature | Detail |
|---|---|
| Direct CAT tuning | Serial port (default COM7, 38400 baud) — no intermediate software |
| HRD Logbook integration | UDP ADIF to port 2333 — same as WSJT-X/JTDX |
| Activator deduplication | Shows only the latest spot per activator — cuts clutter |
| Summit enrichment | Fetches name & altitude from SOTA API, cached for speed |
| RST dialog | Pre-filled 59/599/+00 based on mode, editable before sending |
| Visual feedback | Orange → pending, green → success, red → error with tooltip |
| Settings popup | Configure COM port, callsign, grid, log port, test connection |

---

## Requirements

- **Windows** + **Google Chrome**
- **Python 3.6+** with `pyserial` on your `PATH`
- **Yaesu FT-DX10** on a serial/USB port (tested on COM7 via Silicon Labs CP2105)
- **HRD Logbook** (optional) with UDP QSO Forwarding enabled on port 2333

---

## Quick Setup

### 1 — Register the native host
Double-click `native-host\install.bat`. This writes one registry key so Chrome can find the Python bridge.

### 2 — Load the extension
1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder
4. Note the extension ID shown on the card

### 3 — Configure the native host manifest
Copy the template:
```
native-host\com.sotahunter.bridge.json.template  →  native-host\com.sotahunter.bridge.json
```
Open the `.json` file and set:
```json
"path": "C:\\Users\\YourName\\SOTA_Hunter\\native-host\\bridge.bat",
"allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID/"]
```

### 4 — Set your callsign and grid
Click the SOTA Hunter toolbar icon → fill in your callsign, grid square, and COM port → **Save**.

### 5 — Enable HRD QSO Forwarding (if using Log)
HRD Logbook → **Tools → Configure → QSO Forwarding** → enable *"Receive QSO notifications using UDP from other applications (WSJT-X)"*.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Tune button goes red | Check COM port in settings; use **Test Connection**; check `native-host\bridge.log` |
| Log button goes red | Check HRD Logbook is running with UDP forwarding enabled |
| No buttons appear | Reload SOTAwatch; check `chrome://extensions/` for errors |
| "Cannot connect to native host" | Re-run `install.bat`; verify the `.json` manifest has the correct path and extension ID; restart Chrome |

---

## Architecture

```
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → FT-DX10 (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome auto-launches the Python bridge on demand — no manual process to start, no open localhost ports.

---

## License

MIT — see [LICENSE](LICENSE).

---

*73 de DM6LE — built for chasers who don't want to fumble with VFO knobs while a rare summit is on air.*
