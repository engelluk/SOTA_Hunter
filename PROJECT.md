# SOTA Chaser — Project Information

**Current Version:** 1.0.0
**Status:** Active Development
**Last Updated:** March 2026

---

## IMPORTANT FOR AI ASSISTANTS

**This project has strict development standards. Read these files before making changes:**

1. **[CLAUDE.md](CLAUDE.md)** - Key files, critical technical knowledge, conventions
2. **[AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md)** - Quick-start workflow and checklist
3. **[config.py](config.py)** - Check current VERSION

**DO NOT make changes without following the documented workflow.**

---

## Project Overview

SOTA Chaser is a Chrome extension + Python native messaging host that adds **Tune** and **Log** buttons to every spot row on [SOTAwatch](https://sotawatch.sota.org.uk/).

- **Tune** (blue) — sets the Yaesu FT-DX10's VFO frequency and mode via direct serial CAT on COM7
- **Log** (purple) — sends a complete SOTA chase QSO to HRD Logbook via UDP ADIF (port 2333)

Chrome auto-launches the Python native host on demand — no manual process startup required.

**Key Features:**
- Inline Tune and Log buttons on every SOTAwatch spot row
- Activator deduplication — always on, shows only the most recent spot per callsign
- RST dialog before logging — pre-fills 59/599/+00 based on mode, user confirms before sending
- Summit enrichment — fetches name and altitude from the SOTA API, included in the ADIF COMMENT field; results cached to avoid repeated lookups
- Automatic SSB sideband selection (LSB ≤ 7.3 MHz, USB above); digital modes → DATA-U
- Mode mapping: SOTAwatch labels → correct Yaesu CAT mode codes
- Visual feedback: blue/purple (idle) → orange (pending) → green (success) / red (error)
- Settings popup: COM port, baud rate, callsign, grid square, HRD log port, Test Connection

---

## Architecture

```
SOTAwatch DOM  →  content.js  →  background.js  →  bridge.py  →  cat_client.py  (serial CAT → FT-DX10)
                                                                →  adif_logger.py (UDP ADIF → HRD Logbook)
```

- `extension/` — Chrome extension (Manifest V3): content script, service worker, popup
- `native-host/` — Python bridge: native messaging stdin/stdout (4-byte LE length prefix + JSON)

---

## Key Project Files

```
SOTA_Hunter/
├── config.py                              VERSION constant (must match manifest.json)
├── CLAUDE.md                              AI assistant quick reference
├── AI_INSTRUCTIONS.md                     AI assistant workflow guide
├── CONTRIBUTING.md                        Development workflow and standards
├── PROJECT.md                             This file
├── README.md                              User documentation
├── .claude-instructions                   AI assistant discovery file
├── .gitignore
│
├── extension/                             Chrome Extension (Manifest V3)
│   ├── manifest.json                      Extension manifest
│   ├── background.js                      Service worker — native messaging hub
│   ├── content.js                         Content script — DOM injection, dedup, buttons
│   ├── content.css                        Styles for injected UI elements
│   ├── popup.html                         Settings popup
│   ├── popup.js                           Popup logic
│   └── icons/                             Extension icons (16/48/128 px)
│
└── native-host/                           Python Native Messaging Host
    ├── bridge.py                          stdin/stdout JSON bridge (entry point)
    ├── bridge.bat                         Launcher for bridge.py
    ├── cat_client.py                      Direct Yaesu FT-DX10 CAT serial client
    ├── adif_logger.py                     ADIF record builder + UDP sender
    ├── hrd_client.py                      Legacy HRD TCP client (kept as reference)
    ├── test_cat.py                        30-case CAT client test suite
    ├── com.sotachaser.bridge.json.template  Native host manifest template
    └── install.bat                        One-time Windows registry setup
```

---

## Development Workflow

### Every Change Must Include:

1. **Version Update** — update `VERSION` in `config.py` AND `"version"` in `extension/manifest.json` (must match)
2. **Testing** — run all tests (see below)
3. **Git Commit** — imperative mood, explain *why* not *what*; body for multi-file changes
4. **Documentation** — update README.md if user-visible behaviour changes

### Version Increment Rules:

- **MAJOR (X.0.0)** — breaking changes, major new features
- **MINOR (0.X.0)** — new features, backward-compatible additions
- **PATCH (0.0.X)** — bug fixes, minor improvements

---

## Required Tests Before Commit

```bash
# Python syntax
python -m py_compile native-host/bridge.py
python -m py_compile native-host/cat_client.py
python -m py_compile native-host/adif_logger.py
python -m py_compile config.py

# CAT client test suite (30 cases)
python native-host/test_cat.py

# Validate JSON manifests
python -c "import json; json.load(open('extension/manifest.json')); print('OK')"
python -c "import json; json.load(open('native-host/com.sotachaser.bridge.json.template')); print('OK')"

# Version consistency check
python -c "from config import VERSION; print('Version:', VERSION)"
```

---

## Commit Message Format

```
Short imperative summary explaining why (not what)

Longer body for multi-file changes — describe the problem being solved
and why this approach was chosen.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## Quality Checklist

Before committing, verify:

- [ ] `VERSION` updated in `config.py`
- [ ] `"version"` updated in `extension/manifest.json` (must match config.py)
- [ ] All Python syntax checks passed
- [ ] `test_cat.py` passes (if CAT client changed)
- [ ] JSON manifests are valid
- [ ] `README.md` updated if user-visible behaviour changed
- [ ] No `__pycache__/`, `bridge.log`, or `com.sotachaser.bridge.json` in staged files
- [ ] Commit message is imperative, explains *why*, includes Co-Authored-By line

---

**Remember:** Quality over speed. Follow the workflow completely.
