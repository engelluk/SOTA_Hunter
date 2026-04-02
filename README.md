# SOTA Chaser

🌐 [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md)

**One click to tune. One click to log. Never leave SOTAwatch.**

SOTA Chaser is a Chrome extension that adds **Tune** and **Log** buttons directly into the [SOTAwatch3](https://sotawatch.sota.org.uk/) spots table — so you can work a summit activation without touching your keyboard or switching windows.

---

## Before / After

| Without SOTA Chaser | With SOTA Chaser |
|---|---|
| ![SOTAwatch without extension](screenshots/without%20extension.png) | ![SOTAwatch with extension](screenshots/with%20extension.png) |

---

## What happens when you click

### Tune (blue button)
Sets your **Yaesu radio's** VFO frequency and mode in one click via direct serial CAT — no intermediate software, no CAT-to-TCP bridges.

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
| Direct CAT tuning | 8 Yaesu models supported — baud rate auto-configured per model |
| Auto COM port release | Serial port freed automatically when the SOTAwatch tab is closed |
| HRD Logbook integration | UDP ADIF to port 2333 — same as WSJT-X/JTDX |
| Activator deduplication | Shows only the latest spot per activator — cuts clutter |
| Summit enrichment | Fetches name & altitude from SOTA API, cached for speed |
| RST dialog | Pre-filled 59/599/+00 based on mode, editable before sending |
| Visual feedback | Orange → pending, green → success, red → error with tooltip |
| Settings popup | Radio model dropdown, COM port, callsign, grid, log port, test connection |

---

## Supported Radios

Currently supports all Yaesu radios using the standard ASCII CAT protocol. Select your model in the settings popup — the correct baud rate is filled in automatically.

| Radio | Default Baud | Connection |
|---|---|---|
| FT-DX10 | 38400 | USB (Silicon Labs CP2105) |
| FTX-1 | 38400 | USB (Silicon Labs CP2105) |
| FT-710 | 38400 | USB (Silicon Labs CP2105) |
| FTDX101MP/D | 38400 | USB + RS-232C |
| FT-991A | 4800 | USB (Silicon Labs CP210x) |
| FT-891 | 9600 | USB (Silicon Labs CP210x) |
| FTDX3000 | 4800 | RS-232C (USB adapter needed) |
| FTDX1200 | 4800 | RS-232C + USB |

Use **Custom / Other** for any Yaesu radio not listed — set the baud rate manually (typical values: 4800, 9600, 38400).

---

## Requirements

- **Windows** + **Google Chrome**
- **Python 3.6+** with `pyserial` — verify with `python --version` and `pip install pyserial` in Command Prompt
- **Yaesu radio** (see Supported Radios above) connected via USB or RS-232C serial
- **HRD Logbook** (optional) with UDP QSO Forwarding enabled on port 2333

---

## Quick Setup

### 1 — Register the native host
Double-click `native-host\install.bat`. This writes one registry key so Chrome can find the Python bridge.

### 2 — Load the extension
1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder
4. Note the extension ID shown on the card (a string of 32 lowercase letters, e.g. `abcdefghijklmnopqrstuvwxyzabcdef`)

### 3 — Configure the native host manifest
Copy the template:
```
native-host\com.sotachaser.bridge.json.template  →  native-host\com.sotachaser.bridge.json
```
Open the `.json` file and set:
```json
"path": "C:\\Users\\YourName\\SOTA_Hunter\\native-host\\bridge.bat",
"allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID/"]
```

### 4 — Configure settings
Click the SOTA Chaser toolbar icon to open the settings popup:

![Extension settings](screenshots/extension%20settings.png)

- **Radio Model** — select your radio; baud rate is filled in automatically
- **COM Port** — serial port for your radio (check Device Manager if unsure)
- **My Callsign / Grid Square** — included in every logged QSO
- **HRD Log Port** — UDP port for HRD Logbook (default: 2333)

Click **Test Connection** to verify the radio responds.

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
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → Yaesu radio (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome auto-launches the Python bridge on demand — no manual process to start, no open localhost ports.

---

## License

MIT — see [LICENSE](LICENSE).

---

*73 de DM6LE — built for chasers who don't want to fumble with VFO knobs while a rare summit is on air.*
