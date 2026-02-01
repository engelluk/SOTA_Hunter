# Contributing to SOTA Hunter

This document outlines the development workflow for SOTA Hunter.

---

## Development Workflow

**IMPORTANT:** All changes must follow this workflow.

### 1. Planning Phase

- Read user request
- Ask clarifying questions
- Decide version number (MAJOR/MINOR/PATCH)
- Create TODO list

### 2. Implementation Phase

**Required steps:**

1. Update `VERSION` in config.py
2. Update `"version"` in extension/manifest.json (must match config.py)
3. Make code changes
4. Update RELEASE_NOTES.md (if project uses it)
5. Update README.md (if needed)
6. Run all tests

### 3. Testing Phase

```bash
# Python syntax check
python -m py_compile native-host/bridge.py
python -m py_compile native-host/hrd_client.py
python -m py_compile config.py

# Version import test
python -c "from config import VERSION; print('Version:', VERSION)"

# JSON manifest validation
python -c "import json; json.load(open('extension/manifest.json')); print('OK')"
python -c "import json; json.load(open('native-host/com.sotahunter.bridge.json')); print('OK')"

# Manual browser testing (when UI/content script changes are made)
# 1. Reload extension at chrome://extensions/
# 2. Open https://sotawatch.sota.org.uk/en/
# 3. Verify Tune buttons, dedup toggle, popup settings
```

### 4. Git Workflow

```bash
# Check status
git status

# Stage changes
git add config.py extension/manifest.json [other changed files]

# Commit
git commit -m "$(cat <<'EOF'
Release vX.Y.Z: Description

[Detailed commit message following template]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Verify
git log -1 --stat
```

---

## Version Management

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** (X.0.0) - Breaking changes, major new features
- **MINOR** (0.X.0) - New features, backward-compatible
- **PATCH** (0.0.X) - Bug fixes, minor improvements

### When to Increment

| Change Type | Version | Example |
|-------------|---------|---------|
| Breaking change | MAJOR | 1.0.0 -> 2.0.0 |
| New feature | MINOR | 1.0.0 -> 1.1.0 |
| Bug fix | PATCH | 1.0.0 -> 1.0.1 |
| Refactor | PATCH | 1.0.0 -> 1.0.1 |

### Version Locations (Must Stay in Sync)

1. `config.py` - `VERSION = "X.Y.Z"`
2. `extension/manifest.json` - `"version": "X.Y.Z"`

---

## Git Commit Format

```
Release vX.Y.Z: Brief description

Detailed description of changes.

New Features:
- Feature 1
- Feature 2

Technical Improvements:
- Improvement 1

Bug Fixes:
- Fix 1

Documentation:
- Updated RELEASE_NOTES.md
- Updated README.md

File Changes:
- Modified: file1
- Added: file2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## Pre-Commit Checklist

- [ ] VERSION updated in config.py
- [ ] VERSION updated in extension/manifest.json (must match)
- [ ] RELEASE_NOTES.md updated (if used)
- [ ] README.md version updated (if applicable)
- [ ] All Python syntax checks passed
- [ ] JSON manifests are valid
- [ ] No venv/, __pycache__, or bridge.log in staged files
- [ ] Commit message follows template
- [ ] Co-Authored-By line included

---

## Project-Specific Guidelines

### Editing Python Code (native-host/)

- `bridge.py` handles Chrome native messaging (stdin/stdout with 4-byte LE length prefix + JSON)
- `hrd_client.py` handles HRD TCP protocol (UTF-16LE with 4-byte LE length prefix)
- Both must work on Windows (binary mode stdin/stdout, backslash paths)
- Log output goes to `native-host/bridge.log` (never commit this file)

### Editing JavaScript Code (extension/)

- `manifest.json` is Manifest V3 format
- `background.js` is a service worker (no DOM access, no persistent state across restarts)
- `content.js` runs in the SOTAwatch page context (Vue.js SPA, dynamic DOM)
- `content.css` styles are injected into the SOTAwatch page
- `popup.js` has access to `chrome.storage` and `chrome.runtime` APIs

### Adding New Features

- If adding a new permission, update `extension/manifest.json`
- If adding a new Python dependency, document it (no requirements.txt needed currently - stdlib only)
- If changing the native messaging protocol, update both `bridge.py` and `background.js`

---

## Troubleshooting Development Issues

### Extension Not Loading
- Check `chrome://extensions/` for error messages
- Validate `extension/manifest.json` is well-formed JSON
- Ensure all referenced files exist (icons, scripts)

### Native Host Not Connecting
- Run `native-host/install.bat` to register the host
- Verify extension ID in `native-host/com.sotahunter.bridge.json`
- Check `native-host/bridge.log` for error output
- Ensure Python is on the system PATH

### Content Script Not Injecting
- Verify URL matches pattern in manifest.json
- Check browser console (F12) on SOTAwatch for errors
- SOTAwatch is a Vue.js SPA - DOM may not be ready immediately

---

## Development Setup

```bash
# 1. Clone repository
git clone [repository-url]
cd SOTA_Hunter

# 2. Verify Python is available
python --version

# 3. Run tests
python -m py_compile native-host/bridge.py
python -m py_compile native-host/hrd_client.py
python -c "from config import VERSION; print(f'Setup complete! Version: {VERSION}')"

# 4. Register native host
# Double-click native-host/install.bat

# 5. Load extension in Chrome
# chrome://extensions/ > Developer mode > Load unpacked > select extension/

# 6. Update extension ID in native-host/com.sotahunter.bridge.json
```

---

**Remember:** Quality over speed. Follow the workflow completely.

**Last Updated:** February 2026
