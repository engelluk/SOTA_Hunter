# AI Assistant Instructions - SOTA Chaser

**READ THIS FIRST when starting a new session on this project.**

This document provides quick-start instructions for AI assistants working on SOTA Chaser.

---

## Quick Start for New Sessions

### 1. First Actions (ALWAYS DO THIS)

Before making any changes:

```
1. config.py - Check current version
2. extension/manifest.json - Verify version matches config.py
3. RELEASE_NOTES.md - Read latest 2-3 versions (if exists)
4. CONTRIBUTING.md - Understand workflow
5. This file (AI_INSTRUCTIONS.md)
```

### 2. Understand Current State

```python
# Check current version
from config import VERSION
print(f"Current version: {VERSION}")
```

Look at recent git commits:
```bash
git log -3 --oneline
```

### 3. Before Making Changes

**ALWAYS:**
- Create a TODO list for tracking
- Ask user about version increment (MAJOR/MINOR/PATCH)
- Clarify requirements if ambiguous
- Plan the changes before implementing

**NEVER:**
- Make changes without reading project documentation first
- Skip version updates
- Skip testing
- Commit without updating RELEASE_NOTES.md (if used)

---

## Project Architecture

This is a **hybrid Python + JavaScript** project with three components:

```
SOTAwatch page          Chrome Extension           Native Host (Python)       HRD Rig Control
+--------------+       +------------------+       +--------------------+     +--------------+
| Spot rows    |  DOM  | content.js       |  msg  | bridge.py          | TCP | Port 7809    |
| + injected   |<----->| (inject buttons, |<----->| (auto-launched by  |---->| Set freq/mode|
|   Tune btns  |       |  dedup spots)    |       |  Chrome on demand) |     | on FT-DX10   |
+--------------+       | background.js    |       +--------------------+     +--------------+
                       | (native messaging)|
                       +------------------+
```

### Key Files by Component

**Chrome Extension (JavaScript):**
- `extension/manifest.json` - Extension manifest (Manifest V3)
- `extension/background.js` - Service worker, native messaging hub
- `extension/content.js` - DOM injection, dedup logic, tune buttons
- `extension/content.css` - Injected UI styles
- `extension/popup.html` / `popup.js` - Settings popup

**Native Host (Python):**
- `native-host/bridge.py` - Chrome native messaging stdin/stdout bridge
- `native-host/hrd_client.py` - HRD Rig Control TCP protocol client
- `native-host/bridge.bat` - Launcher script
- `native-host/com.sotachaser.bridge.json` - Native messaging manifest
- `native-host/install.bat` - Windows registry setup

**Project Root:**
- `config.py` - Version and configuration constants
- `README.md` - User documentation

---

## Standard Workflow (EVERY CHANGE)

### Phase 1: Planning
```
1. Read user request
2. Ask clarifying questions
3. Decide version number (ask user if unsure)
4. Create TODO list
```

### Phase 2: Implementation
```
1. Update VERSION in config.py
2. Update "version" in extension/manifest.json (keep in sync!)
3. Make code changes
4. Update RELEASE_NOTES.md (add new version section) - if used
5. Update README.md (if applicable)
6. Update any other affected docs
```

### Phase 3: Testing
```
1. Python syntax check: python -m py_compile native-host/bridge.py native-host/hrd_client.py config.py
2. Python import test: python -c "from config import VERSION; print(VERSION)"
3. Verify manifest.json is valid JSON
4. Manual browser test if DOM/UI changes were made
```

### Phase 4: Git
```
1. git status
2. git add [files]
3. git commit -m "Release vX.Y.Z: ..." (use full format)
4. git log -1 --stat (verify)
```

---

## Version Decision Quick Reference

**User adds/changes something:**

| Type of Change | Version | Example |
|----------------|---------|---------|
| New major feature, breaking change | MAJOR | 1.0.0 -> 2.0.0 |
| New feature, backward-compatible | MINOR | 1.0.0 -> 1.1.0 |
| Bug fix | PATCH | 1.0.0 -> 1.0.1 |
| Code refactor (no behavior change) | PATCH | 1.0.0 -> 1.0.1 |
| UI/text/style changes | PATCH | 1.0.0 -> 1.0.1 |

**When uncertain:** Ask user "Should this be MAJOR, MINOR, or PATCH?"

---

## Required File Updates

For **EVERY** change:

### 1. config.py
```python
VERSION = "X.Y.Z"  # Always update this
```

### 2. extension/manifest.json
```json
"version": "X.Y.Z"  // Must match config.py
```

### 3. RELEASE_NOTES.md (if used)
```markdown
## Version X.Y.Z (Month Year)

### [Type] Release - Title

Description

#### [Sections as needed]
- Change 1
- Change 2
```

### 4. README.md (if applicable)
```markdown
**Current Version:** X.Y.Z
```

---

## Testing Commands for SOTA Chaser

Run these before committing:

```bash
# 1. Python syntax check
python -m py_compile native-host/bridge.py
python -m py_compile native-host/hrd_client.py
python -m py_compile config.py

# 2. Version import test
python -c "from config import VERSION; print('Version:', VERSION)"

# 3. HRD client module import test
python -c "import sys; sys.path.insert(0, 'native-host'); from hrd_client import HRDClient; print('HRDClient: OK')"

# 4. Validate manifest.json is well-formed
python -c "import json; json.load(open('extension/manifest.json')); print('manifest.json: OK')"

# 5. Validate native host manifest
python -c "import json; json.load(open('native-host/com.sotachaser.bridge.json')); print('native manifest: OK')"
```

### Manual Browser Testing (when UI changes are made)

1. Reload extension at `chrome://extensions/`
2. Open https://sotawatch.sota.org.uk/en/
3. Verify Tune buttons appear on spot rows
4. Verify dedup toggle works
5. Click Tune button (requires HRD running) or verify error feedback appears
6. Check popup settings and Test Connection button

---

## Git Commit Template

```bash
git commit -m "$(cat <<'EOF'
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
EOF
)"
```

---

## Critical Reminders

### Files to ALWAYS Update
1. config.py (VERSION)
2. extension/manifest.json ("version" - must match config.py)
3. RELEASE_NOTES.md (if project uses it)
4. README.md (version number if present)

### Files to NEVER Commit
1. venv/ (Python virtual environment)
2. __pycache__/* (cached Python files)
3. *.pyc, *.pyo (compiled Python)
4. native-host/bridge.log (runtime log)
5. .env (environment variables)
6. .DS_Store, Thumbs.db (OS files)

### Testing is MANDATORY
- Run ALL tests before committing
- No exceptions, even for "small" changes

### Documentation is MANDATORY
- Update RELEASE_NOTES.md for EVERY change (if used)
- Update README.md version number
- Write clear commit messages

---

## Common Scenarios

### Scenario 1: User Reports a Bug

```
1. Understand the bug
2. Decide: PATCH version (bug fix)
3. Fix the bug
4. Update VERSION in config.py AND manifest.json
5. Add to RELEASE_NOTES.md under "Bug Fixes" (if used)
6. Test the fix
7. Commit with "Release vX.Y.Z: Fix [bug description]"
```

### Scenario 2: User Wants New Feature

```
1. Understand feature requirements
2. Ask: Should this be MAJOR or MINOR?
3. Implement feature
4. Update VERSION in config.py AND manifest.json
5. Add to RELEASE_NOTES.md under "New Features" (if used)
6. Update README.md with feature description
7. Test feature
8. Commit with detailed feature description
```

### Scenario 3: User Wants to Improve Code

```
1. Understand what to improve
2. Decide: PATCH version (if behavior unchanged)
3. Make improvements
4. Update VERSION in config.py AND manifest.json
5. Add to RELEASE_NOTES.md under "Technical Improvements" (if used)
6. Test that behavior hasn't changed
7. Commit with improvement description
```

---

## Project-Specific Notes

### Dual-Language Considerations
- Python changes: test with `py_compile` and import checks
- JavaScript changes: validate JSON manifests, manual browser test
- Version lives in TWO places: `config.py` and `extension/manifest.json`

### HRD Protocol
- TCP connection to port 7809 (configurable)
- UTF-16LE encoding with 4-byte little-endian length prefix
- Commands: `Set Frequency-Hz`, `Set Mode`, `Get Frequency`, `Get Mode`

### SOTAwatch DOM
- Vue.js SPA - DOM updates dynamically
- Content script uses MutationObserver to detect changes
- Spots also fetched directly from API for reliable data

### Native Messaging
- Chrome auto-launches bridge.py via bridge.bat on demand
- Messages: 4-byte LE length prefix + UTF-8 JSON (Chrome protocol)
- Registry key at HKCU\Software\Google\Chrome\NativeMessagingHosts\com.sotachaser.bridge

---

## Pre-Commit Checklist

Before running `git commit`, verify:

```
[ ] VERSION updated in config.py
[ ] VERSION updated in extension/manifest.json (must match)
[ ] RELEASE_NOTES.md has new version section (if used)
[ ] README.md version number updated (if applicable)
[ ] All Python syntax checks passed
[ ] manifest.json validates as JSON
[ ] git status shows only intended files
[ ] No venv/, __pycache__, or bridge.log in staged files
[ ] Commit message follows template
[ ] Co-Authored-By line included
```

---

## Success Criteria

A change is complete when:

- Version number is incremented in both config.py and manifest.json
- All documentation is updated
- All tests pass
- Git commit is created with proper message
- User can see the change working
- No errors or warnings

---

**Last Updated:** February 2026
**Current Version:** 1.0.0
**Languages:** Python 3.6+, JavaScript (Chrome Manifest V3)

**Quick Access:**
- Full workflow: CONTRIBUTING.md
- Current version: config.py
- Extension version: extension/manifest.json
- Version history: RELEASE_NOTES.md (if used)
