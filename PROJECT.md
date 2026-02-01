# SOTA Hunter - Project Information

**Current Version:** 1.0.0
**Status:** Active Development
**Last Updated:** February 2026

---

## IMPORTANT FOR AI ASSISTANTS

**This project has strict development standards. You MUST read these files before making changes:**

1. **[AI_INSTRUCTIONS.md](AI_INSTRUCTIONS.md)** - START HERE (quick guide)
2. **[config.py](config.py)** - Check current VERSION
3. **[RELEASE_NOTES.md](RELEASE_NOTES.md)** - Review recent changes (if exists)

**DO NOT make changes without following the documented workflow.**

---

## Project Overview

SOTA Hunter is a Chrome extension + native messaging bridge that adds "Tune" buttons to SOTAwatch spots, deduplicates activators to show only the latest frequency, and controls the Yaesu FT-DX10 (or any HRD-supported radio) via HRD Rig Control's TCP interface.

**Key Features:**
- Inline Tune buttons on SOTAwatch spot rows
- Activator deduplication (latest spot per callsign)
- Automatic SSB sideband selection based on frequency
- Mode mapping (SOTAwatch modes to HRD modes)
- Visual feedback on tune success/failure
- Settings popup for HRD host/port configuration

---

## Development Workflow (Summary)

### Every Change Must Include:

1. **Version Update** - Update VERSION in config.py AND extension/manifest.json
2. **Release Notes** - Add entry to RELEASE_NOTES.md (if used)
3. **Testing** - Run all tests (Python syntax + JSON validation)
4. **Git Commit** - Follow commit message template
5. **Documentation** - Update README.md if needed

### Version Increment Rules:

- **MAJOR (X.0.0)** - Breaking changes, major features, new paradigms
- **MINOR (0.X.0)** - New features, backward-compatible additions
- **PATCH (0.0.X)** - Bug fixes, minor improvements

**When uncertain, ask the user which version increment to use.**

---

## Documentation Structure

### For AI Assistants & Developers
- **AI_INSTRUCTIONS.md** - Quick start, workflow, checklist
- **CONTRIBUTING.md** - Detailed development workflow
- **PROJECT.md** - This file

### For Users
- **README.md** - User guide, setup, and troubleshooting
- **RELEASE_NOTES.md** - Version history (if used)

---

## Key Project Files

```
SOTA_Hunter/
├── config.py                              Version and configuration
├── .claude-instructions                   AI assistant discovery file
├── AI_INSTRUCTIONS.md                     AI assistant guide
├── CONTRIBUTING.md                        Development workflow
├── PROJECT.md                             This file
├── README.md                              User documentation
├── .gitignore                             Git ignore patterns
│
├── extension/                             Chrome Extension (Manifest V3)
│   ├── manifest.json                      Extension manifest
│   ├── background.js                      Service worker
│   ├── content.js                         Content script (DOM injection, dedup)
│   ├── content.css                        Injected styles
│   ├── popup.html                         Settings popup
│   ├── popup.js                           Popup logic
│   └── icons/                             Extension icons (16/48/128 px)
│
└── native-host/                           Python Native Messaging Host
    ├── bridge.py                          stdin/stdout JSON bridge
    ├── bridge.bat                         Launcher for bridge.py
    ├── hrd_client.py                      HRD TCP protocol client
    ├── com.sotahunter.bridge.json         Native messaging manifest
    └── install.bat                        Windows registry setup
```

---

## Required Tests Before Commit

```bash
# 1. Python syntax check
python -m py_compile native-host/bridge.py
python -m py_compile native-host/hrd_client.py
python -m py_compile config.py

# 2. Version import test
python -c "from config import VERSION; print('Version:', VERSION)"

# 3. Validate JSON manifests
python -c "import json; json.load(open('extension/manifest.json')); print('manifest.json: OK')"
python -c "import json; json.load(open('native-host/com.sotahunter.bridge.json')); print('native manifest: OK')"

# 4. Manual browser test (when UI changes are made)
# Reload extension, open SOTAwatch, verify Tune buttons
```

---

## Git Commit Format

```
Release vX.Y.Z: Brief description

Detailed description.

New Features:
- Feature 1

Technical Improvements:
- Improvement 1

Bug Fixes:
- Fix 1

Documentation:
- Doc update 1

File Changes:
- Modified: file
- Added: file

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Quality Checklist

Before committing, verify:

- [ ] VERSION updated in config.py
- [ ] VERSION updated in extension/manifest.json (must match)
- [ ] RELEASE_NOTES.md has new version section (if used)
- [ ] README.md version number updated (if applicable)
- [ ] All Python syntax checks passed
- [ ] JSON manifests are valid
- [ ] No venv/, __pycache__, or bridge.log in staged files
- [ ] Commit message follows template
- [ ] Co-Authored-By line included

---

## Quick Commands

```bash
# Python syntax check
python -m py_compile native-host/bridge.py native-host/hrd_client.py config.py

# Version check
python -c "from config import VERSION; print(VERSION)"

# Git status
git status

# View recent commits
git log --oneline -5
```

---

**Remember:** Quality over speed. Follow the workflow completely.

**Last Updated:** February 2026
