# CLAUDE.md — SOTA Hunter Project Instructions

## What This Project Is

A Chrome extension (Manifest V3) for [SOTAwatch](https://sotawatch.sota.org.uk/) that adds:
- **Tune** buttons (blue) — tunes a Yaesu FT-DX10 via direct serial CAT on COM7
- **Log** buttons (purple) — sends SOTA chase QSOs to HRD Logbook via UDP ADIF on port 2333

## Architecture

```
SOTAwatch DOM  →  content.js  →  background.js  →  bridge.py  →  cat_client.py (serial CAT)
                                                                →  adif_logger.py (UDP ADIF)
```

- **extension/** — Chrome extension (JS, CSS, HTML)
- **native-host/** — Python native messaging host (stdin/stdout JSON with 4-byte LE length prefix)
- Chrome auto-launches `bridge.bat` → `bridge.py` on first message

## Key Files

| File | Role |
|---|---|
| `extension/content.js` | DOM injection, spot parsing, dedup, Tune/Log buttons, summit API cache |
| `extension/background.js` | Message hub — routes tune/log/test between content script and native host |
| `extension/popup.html` + `popup.js` | Settings UI (COM port, baud, callsign, grid, log port) |
| `extension/content.css` | Button styles and state classes |
| `extension/manifest.json` | Manifest V3 config — permissions, content scripts, popup |
| `native-host/bridge.py` | Native messaging entry point — routes tune/test/log actions |
| `native-host/cat_client.py` | Direct Yaesu CAT serial client (COM7, 38400 baud) |
| `native-host/adif_logger.py` | ADIF record builder + UDP sender for HRD Logbook |
| `native-host/hrd_client.py` | Legacy HRD TCP client — mode setting broken, kept as reference |
| `native-host/test_cat.py` | 30-case test suite for CAT client |
| `config.py` | VERSION constant — must stay in sync with manifest.json |

## Hardware & Connectivity

- **Radio:** Yaesu FT-DX10 via USB (Silicon Labs Dual CP2105)
  - **COM7:** Enhanced COM Port — CAT control at 38400 baud
  - **COM8:** Standard COM Port — data/audio, NOT for CAT
- **Logbook:** HRD Logbook — UDP port 2333 (QSO Forwarding)

## Critical Technical Knowledge

### Do NOT attempt HRD TCP mode setting
HRD v6 TCP protocol (port 7809) has a broken rig definition for the FT-DX10. `Set Frequency-Hz` works but ALL other write commands (`Set Dropdown`, `Set Mode`, `Set Button-select`, sliders) are silently ignored. This was tested exhaustively with 34 different approaches — mode setting via HRD TCP is a dead end.

### CAT command ordering matters
Always **set mode BEFORE frequency** to prevent VFO drift on band changes. The FT-DX10 can shift frequency when switching bands if mode is set after.

### SSB sideband follows band plan
- LSB at/below 7.3 MHz, USB above
- Digital modes (FT8, FT4, JS8, PSK, DATA) → DATA-U (MD0C)

### Native messaging is FIFO
background.js tracks requests with a counter and routes responses by action type (`tuneResponse` or `logResponse`). The `action` field in `pendingRequests` determines the response type.

## Settings (chrome.storage.sync)

| Key | Default | Used by |
|---|---|---|
| `cat_port` | `"COM7"` | Tune — serial CAT |
| `cat_baud` | `38400` | Tune — serial CAT |
| `my_callsign` | `""` | Log — STATION_CALLSIGN in ADIF |
| `my_gridsquare` | `""` | Log — MY_GRIDSQUARE in ADIF |
| `log_port` | `2333` | Log — UDP destination port |

## Code Conventions

- Content script: IIFE with `"use strict"`, no globals leaking
- Async request/response: `pendingCallbacks` Map keyed by `requestCounter`
- Visual feedback on buttons: pending (orange) → success (green) / error (red), auto-revert 3-5s
- Python: standard logging to `bridge.log`, `logger = logging.getLogger("sotahunter.xxx")`
- No frameworks — vanilla JS in the extension, stdlib Python in native host (only dependency: `pyserial`)

## Version Management

Version lives in **two places** that must stay in sync:
- `config.py` → `VERSION = "X.Y.Z"`
- `extension/manifest.json` → `"version": "X.Y.Z"`

## Commit Style

- Imperative mood, explain "why" not "what"
- 1-2 sentence summary on first line
- Detailed body for multi-file changes
- End with `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

## Testing

```bash
# Python syntax
python -m py_compile native-host/bridge.py
python -m py_compile native-host/cat_client.py
python -m py_compile native-host/adif_logger.py

# CAT client test suite (30 cases)
python native-host/test_cat.py

# JSON manifests valid
python -c "import json; json.load(open('extension/manifest.json')); print('OK')"
python -c "import json; json.load(open('native-host/com.sotahunter.bridge.json.template')); print('OK')"
```

