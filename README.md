# SOTA Hunter

> **FOR AI ASSISTANTS: Read [AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md) BEFORE making any changes to this project.**

A Chrome extension that adds **Tune** and **Log** buttons to [SOTAwatch](https://sotawatch.sota.org.uk/) spots. Tunes your Yaesu FT-DX10 via direct serial CAT and logs SOTA chase QSOs to [HRD Logbook](https://ham-radio-deluxe.com/) via UDP ADIF.

**Current Version:** 1.0.0

## What It Does

- **Tune buttons** appear inline next to each spot's frequency on the SOTAwatch page. Click one to instantly set your radio's VFO frequency and mode.
- **Log buttons** appear next to each Tune button. Click one to send a complete SOTA chase QSO record to HRD Logbook via UDP ADIF (port 2333) — the same protocol used by WSJT-X, JTDX, and JS8Call. The record includes callsign, frequency, band, mode, SOTA_REF, SIG/SIG_INFO, summit name and altitude in COMMENT, and your station callsign and grid square.
- **Summit enrichment** — when logging, the extension fetches summit details (name, altitude) from the SOTA API and includes them in the ADIF COMMENT field. Results are cached to avoid repeated lookups.
- **Activator deduplication** filters the spot list to show only the most recent spot per activator callsign, reducing clutter. This is togglable with a checkbox above the spots table.
- **Automatic mode mapping** translates SOTAwatch mode labels to the correct radio mode:
  - `SSB` becomes `USB` (above 10 MHz) or `LSB` (below 10 MHz)
  - `CW` stays `CW`
  - `FM`, `AM` pass through unchanged
  - `DATA`, `FT8`, `FT4`, `JS8`, `PSK` become `USB-D`
- **Visual feedback** on each button: blue/purple (idle), orange (pending), green (success), red (error with tooltip).
- **Settings popup** lets you configure the COM port/baud rate, your callsign and grid square, the HRD log port, and test the radio connection.

## Architecture

```
SOTAwatch page          Chrome Extension           Native Host (Python)       Radio / Logbook
+--------------+       +------------------+       +--------------------+     +--------------+
| Spot rows    |  DOM  | content.js       |  msg  | bridge.py          | CAT | FT-DX10      |
| + injected   |<----->| (inject buttons, |<----->| (auto-launched by  |---->| Set freq/mode|
|   Tune/Log   |       |  dedup spots)    |       |  Chrome on demand) |     +--------------+
|   buttons    |       | background.js    |       |                    | UDP | HRD Logbook  |
+--------------+       | (native messaging)|       | adif_logger.py     |---->| Port 2333    |
                       +------------------+       +--------------------+     +--------------+
```

Chrome auto-launches the Python native host on demand when the extension sends a message. No manual process startup or open localhost ports required.

## Project Structure

```
SOTA_Hunter/
├── extension/                         # Chrome extension (Manifest V3)
│   ├── manifest.json                  # Extension manifest
│   ├── background.js                  # Service worker - native messaging hub
│   ├── content.js                     # Content script - DOM injection, dedup, tune buttons
│   ├── content.css                    # Styles for injected UI elements
│   ├── popup.html                     # Settings popup
│   ├── popup.js                       # Popup logic
│   └── icons/                         # Extension icons (16/48/128 px)
├── native-host/
│   ├── bridge.py                      # Native messaging host (stdin/stdout JSON bridge)
│   ├── bridge.bat                     # Launcher for bridge.py
│   ├── cat_client.py                  # Direct Yaesu FT-DX10 CAT serial client
│   ├── adif_logger.py                 # ADIF record builder + UDP sender for HRD Logbook
│   ├── hrd_client.py                  # HRD Rig Control TCP protocol client (legacy)
│   ├── com.sotahunter.bridge.json     # Native messaging host manifest
│   └── install.bat                    # One-time Windows registry setup
├── config.py                          # Version and configuration
├── AI_INSTRUCTIONS.md                 # AI assistant quick-start guide
├── CONTRIBUTING.md                    # Development workflow
├── PROJECT.md                         # Project overview
├── .claude-instructions               # AI assistant discovery file
├── .gitignore                         # Git ignore patterns
└── README.md                          # This file
```

## Prerequisites

- **Windows** (the native messaging host uses the Windows registry)
- **Google Chrome**
- **Python 3.6+** installed and available on your system `PATH` (with `pyserial` for CAT control)
- **Yaesu FT-DX10** (or compatible radio) connected via USB/serial for CAT control
- **HRD Logbook** (optional, for QSO logging) with UDP QSO Forwarding enabled on port 2333

## Setup

### 1. Register the native messaging host

Double-click `native-host\install.bat`. This writes a registry key under `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.sotahunter.bridge` that tells Chrome where to find the host manifest.

### 2. Load the extension in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder

Chrome will assign the extension an ID (a long string of lowercase letters shown on the extension card).

### 3. Link the extension ID to the native host

1. Copy the extension ID from `chrome://extensions/`
2. Open `native-host\com.sotahunter.bridge.json` in a text editor
3. Replace `EXTENSION_ID_HERE` with your actual extension ID:
   ```json
   "allowed_origins": [
     "chrome-extension://abcdefghijklmnopqrstuvwxyz123456/"
   ]
   ```
4. Verify that the `"path"` value points to the correct absolute path of `bridge.bat` on your system. The default is:
   ```
   C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\bridge.bat
   ```
   Update it if your installation is in a different location.

### 4. Configure settings

Click the SOTA Hunter icon in the Chrome toolbar to open the settings popup:

- **COM Port / Baud Rate** — serial port for your radio (default: COM7 / 38400)
- **My Callsign / Grid Square** — included in logged QSOs as STATION_CALLSIGN and MY_GRIDSQUARE
- **HRD Log Port** — UDP port for HRD Logbook QSO Forwarding (default: 2333)

Click **Test Connection** to verify the radio is responding on the configured port.

### 5. Enable HRD Logbook UDP receive (for QSO logging)

In HRD Logbook, go to **Tools > Configure > QSO Forwarding** and enable **"Receive QSO notifications using UDP from other applications (WSJT-X)"**. This allows SOTA Hunter to send logged QSOs directly into your logbook.

## Usage

1. Make sure your radio is connected and powered on
2. Open https://sotawatch.sota.org.uk/en/
3. Each spot shows a blue **Tune** button and a purple **Log** button next to the frequency
4. Click **Tune** to set your radio's VFO frequency and mode
5. After working the station, click **Log** to send the QSO to HRD Logbook — the ADIF record includes the callsign, frequency, band, mode, SOTA reference, summit name/altitude, and your station details
6. Use the **Show unique activators only** checkbox above the spots table to toggle deduplication

## Troubleshooting

**Tune button turns red / shows an error:**
- Check that your radio is powered on and connected to the configured COM port
- Click the SOTA Hunter toolbar icon and use **Test Connection** to diagnose
- Check `native-host\bridge.log` for detailed error messages

**Log button turns red / shows an error:**
- Check that HRD Logbook is running with UDP QSO Forwarding enabled (Tools > Configure > QSO Forwarding)
- Verify the HRD Log Port in settings matches the port HRD Logbook is listening on (default 2333)
- Check `native-host\bridge.log` for the ADIF record that was sent

**No Tune/Log buttons appear:**
- Reload the SOTAwatch page
- Check `chrome://extensions/` for any errors on the SOTA Hunter extension card
- Open DevTools (F12) on the SOTAwatch page and look for `SOTA Hunter` messages in the console

**"Cannot connect to native host" error:**
- Verify you ran `install.bat`
- Verify the extension ID in `com.sotahunter.bridge.json` matches your installed extension
- Verify the `"path"` in the manifest points to `bridge.bat` and that Python is on your system `PATH`
- Try restarting Chrome after making changes to the native host manifest or registry

**Deduplication not working as expected:**
- The extension fetches spot data from the SOTA API every 60 seconds. Newly posted spots may take up to a minute to be reflected.
- Toggle the checkbox off and back on to force a re-process of the visible rows.

## Contributing & Development

This project follows strict version management and quality standards.

**Essential reading for contributors:**

1. **[AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md)** - Quick start guide (READ THIS FIRST)
2. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Complete development workflow
3. **[PROJECT.md](PROJECT.md)** - Project overview and quick reference

### Version Management

Version is tracked in two places that must stay in sync:
- `config.py` - `VERSION = "X.Y.Z"`
- `extension/manifest.json` - `"version": "X.Y.Z"`

Follows semantic versioning:
- **MAJOR** (X.0.0) - Breaking changes, major features
- **MINOR** (0.X.0) - New features, backward-compatible
- **PATCH** (0.0.X) - Bug fixes, minor improvements

---

**Last Updated:** February 2026
