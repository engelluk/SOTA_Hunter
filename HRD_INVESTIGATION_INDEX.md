# HRD Protocol Investigation - Documentation Index

## Overview

This index provides a guide to all documentation generated from the HRD protocol investigation for the SOTA Hunter project. The investigation involved 174 documented activities extracted from Claude Code conversation transcripts.

---

## Source Transcripts (Raw Data)

### Main Investigation Session
**File:** `C:\Users\X1\.claude\projects\C--Users-X1-Documents-AI-tests-SOTA-Hunter\d97b45e0-bf11-49db-b020-a510bb6e0d56.jsonl`

- **Lines:** 1,926
- **Date:** February 1, 2026
- **Content:** Complete investigation session including all tool calls, web searches, and script creation
- **Key Activities:** Mode setting investigation, CAT control implementation, UDP ADIF logging

### Earlier Session
**File:** `C:\Users\X1\.claude\projects\C--Users-X1-Documents-AI-tests-SOTA-Hunter\42c19785-a1be-4e73-86ae-264f12b167fd.jsonl`

- **Content:** Earlier session with minimal HRD-related activity
- **Activities Extracted:** 1 Bash command

---

## Extracted Activity Data

### Main Activity Log (JSON)
**File:** `C:\Users\X1\Documents\AI tests\SOTA_Hunter\hrd_investigation_activities.json`

- **Format:** JSON array of activity objects
- **Total Activities:** 174
- **Structure:**
  ```json
  {
    "timestamp": "2026-02-01T...",
    "line": 865,
    "tool": "Bash|WebSearch|WebFetch|Write",
    "command|query|file": "...",
    "content": "..." (for Write operations)
  }
  ```

**Activity Breakdown:**
- Bash commands: 116
  - Port scanning/enumeration: 5
  - Python test executions: 75
  - Pip installs: 2
  - Other commands: 34
- Web searches: 19
- Web page fetches: 13
- Python scripts created: 26

### Early Session Activity Log
**File:** `C:\Users\X1\Documents\AI tests\SOTA_Hunter\hrd_investigation_activities_early.json`

- **Total Activities:** 1
- **Note:** Minimal HRD-related activity in this session

---

## Generated Documentation

### 1. Detailed Investigation Report (Comprehensive)
**File:** `HRD_INVESTIGATION_REPORT.md`

**Purpose:** Complete chronological account of the entire investigation

**Contents:**
- Executive Summary
- Phase 1: Initial Setup & TCP Protocol Investigation
  - Package installations
  - Web research conducted
  - Key resources examined
  - Technical discoveries
- Phase 2: Initial HRD_CLIENT.PY Implementation
- Phase 3: Mode Setting Investigation (The Big Problem)
  - 13 systematic probe scripts documented
  - Each script's purpose, approach, and results
- Phase 4: Alternative Approaches
  - COM port discovery
  - GUI automation attempts
- Phase 5: Direct CAT Control Solution
  - CAT protocol research
  - 7 iterations of test_cat.py
  - Production cat_client.py implementation
- Phase 6: HRD Logbook Integration
  - UDP ADIF discovery
  - Implementation details
- Final Architecture
- Statistics Summary
- Key Lessons Learned
- Conclusion

**Length:** ~500 lines, 12,000+ words

**Best For:**
- Understanding the complete investigation process
- Learning what was tried and why
- Technical implementation details
- Future reference for similar projects

---

### 2. Executive Summary (Concise)
**File:** `HRD_INVESTIGATION_SUMMARY.txt`

**Purpose:** High-level overview with key findings and conclusions

**Contents:**
- Investigation scope and statistics
- Problem statement
- Phase summaries (1-6)
- Final architecture diagram (ASCII art)
- Lessons learned
- Key web resources consulted
- Deliverables
- Recommendations
- Conclusion

**Length:** ~350 lines

**Best For:**
- Quick overview of the investigation
- Understanding the problem and solution
- Architectural decisions
- Presenting to others

---

### 3. Scripts Reference Guide (Technical)
**File:** `HRD_INVESTIGATION_SCRIPTS_REFERENCE.md`

**Purpose:** Detailed reference for all 26 scripts created during investigation

**Contents:**
- Production Scripts (ACTIVE)
  - cat_client.py - Usage examples and features
  - bridge.py - Integration details
- Deprecated Scripts (ARCHIVED)
  - hrd_client.py - Why it was deprecated
- Investigation Scripts (ARCHIVED)
  - All 13 probe_*.py scripts
  - Purpose, approach, results for each
  - Key learnings from each script
- CAT Control Development Scripts
  - 7 iterations of test_cat.py
  - Progressive improvements documented
- Script execution order (chronological)
- Testing checklist
- Key takeaways (what works, what doesn't)
- File locations

**Length:** ~450 lines

**Best For:**
- Understanding individual scripts
- Reproducing tests
- Learning from the investigation methodology
- Finding specific script examples

---

### 4. Visual Timeline (Chronological Flow)
**File:** `HRD_INVESTIGATION_TIMELINE.txt`

**Purpose:** Visual representation of investigation flow with ASCII art

**Contents:**
- Timeline of key events (ASCII flow chart)
- Phase progression with visual connections
- Decision points highlighted
- Investigation statistics
- Packages installed during investigation
- Key decision points with rationale
- Lessons learned
- Production status
- Success criteria checklist

**Length:** ~500 lines

**Best For:**
- Understanding the investigation flow
- Seeing how conclusions were reached
- Decision point analysis
- Teaching systematic investigation methodology

---

## Quick Reference

### I want to...

**Understand what the investigation was about:**
→ Read: `HRD_INVESTIGATION_SUMMARY.txt`

**Learn all the technical details:**
→ Read: `HRD_INVESTIGATION_REPORT.md`

**Find a specific script and understand what it does:**
→ Read: `HRD_INVESTIGATION_SCRIPTS_REFERENCE.md`

**See the chronological flow of events:**
→ Read: `HRD_INVESTIGATION_TIMELINE.txt`

**Analyze the raw activity data:**
→ Read: `hrd_investigation_activities.json`

**Reproduce the investigation:**
→ Start with Timeline, then Scripts Reference, then detailed Report

**Present findings to someone else:**
→ Use Summary for overview, then specific sections from Report

---

## Key Findings Summary

### Problem Identified
HRD v6 TCP API (port 7809) mode setting is broken:
- Commands accepted (returns OK)
- Radio mode does NOT change
- 9 systematic probe scripts confirmed this
- Other dropdowns work, Mode is uniquely broken

### Solution Implemented
Hybrid architecture:
1. **Rig Control:** Direct Yaesu CAT serial (COM7)
   - Replaced HRD TCP for all rig operations
   - Mode setting works perfectly
   - Frequency control works perfectly

2. **QSO Logging:** UDP ADIF to HRD Logbook (port 2333)
   - Industry standard protocol
   - SOTA reference support (SIG/SIG_INFO)
   - Simple and reliable

### Investigation Statistics
- **Total Activities:** 174
- **Scripts Created:** 26
- **Web Searches:** 19
- **Web Resources Examined:** 13
- **Python Test Executions:** 75
- **Investigation Date:** February 1, 2026

---

## File Locations

### Documentation (Generated)
```
C:\Users\X1\Documents\AI tests\SOTA_Hunter\
├── HRD_INVESTIGATION_REPORT.md (this index)
├── HRD_INVESTIGATION_SUMMARY.txt
├── HRD_INVESTIGATION_SCRIPTS_REFERENCE.md
├── HRD_INVESTIGATION_TIMELINE.txt
├── HRD_INVESTIGATION_INDEX.md
├── hrd_investigation_activities.json
└── hrd_investigation_activities_early.json
```

### Source Transcripts (Raw)
```
C:\Users\X1\.claude\projects\C--Users-X1-Documents-AI-tests-SOTA-Hunter\
├── d97b45e0-bf11-49db-b020-a510bb6e0d56.jsonl (main investigation)
└── 42c19785-a1be-4e73-86ae-264f12b167fd.jsonl (early session)
```

### Production Code (ACTIVE)
```
C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\
├── cat_client.py (Direct CAT control - ACTIVE)
└── bridge.py (Native messaging host - ACTIVE)
```

### Investigation Scripts (ARCHIVED)
```
C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\
├── hrd_client.py (DEPRECATED - mode setting broken)
├── probe_mode.py (Investigation script)
├── probe_mode2.py
├── probe_mode3.py
├── probe_mode4.py
├── probe_mode5.py
├── probe_cat.py
├── probe_vfo.py
├── probe_mode_final.py
├── probe_mode_final2.py
├── probe_alternatives.py
├── probe_other_dropdowns.py
├── probe_write_test.py
├── probe_hrd_gui.py
├── test_cat.py (7 versions exist)
├── quick_test.py (3 versions exist)
└── test_tune.py
```

---

## Tools and Technologies

### Packages Used
- **pyserial** - Serial port communication (CAT control)
- **pywinauto** - Windows GUI automation (tested, not used in production)

### Protocols Investigated
1. **HRD TCP API (port 7809)**
   - Binary protocol, UTF-16LE encoding
   - 4-byte little-endian length prefix
   - Status: Mode setting broken, deprecated for rig control

2. **Yaesu CAT Serial Protocol**
   - 9600 baud, 8N2
   - ASCII commands, semicolon-terminated
   - Status: ACTIVE - Production rig control

3. **UDP ADIF (port 2333)**
   - Industry standard Amateur Data Interchange Format
   - Used by WSJT-X, N1MM+, etc.
   - Status: ACTIVE - Production QSO logging

### Development Tools
- Python 3.x
- Serial communication libraries
- Socket programming (TCP and UDP)
- Chrome Native Messaging

---

## Web Resources Consulted

### Forums & Documentation
1. forums.hamradiodeluxe.com/node/34951 - API discussion
2. forums.hamradiodeluxe.com/node/40968 - Binary protocol docs
3. support.hamradiodeluxe.com - QSO forwarding docs
4. manualzz.com - HRD server installation

### GitHub Projects
5. github.com/krisp/MiniDeluxe - C# HRD client
6. github.com/K1DBO/slice-master-6000 - FlexRadio/HRD

### Technical Resources
7. sivantoledotech.wordpress.com - Reverse engineering HRD
8. remotehams.com/forums - Protocol discussions
9. community.flexradio.com - UDP ADIF examples

### ADIF Research
10. WSJT-X source code and documentation
11. N1MM+ UDP broadcast format
12. ADIF specification (SIG/SIG_INFO fields)
13. Ham radio logging software communities

---

## How This Documentation Was Generated

### Extraction Process
1. Parsed JSONL conversation transcripts (1,926 lines)
2. Extracted tool calls: Bash, WebSearch, WebFetch, Write
3. Filtered for HRD-related activities (python, serial, COM, port, scan, test)
4. Generated JSON activity log (174 entries)
5. Analyzed activity patterns and chronology
6. Created comprehensive documentation

### Extraction Script
```python
# Parse JSONL conversation transcripts
# Extract tool use: Bash, WebSearch, WebFetch, Write
# Filter for keywords: python, serial, COM, port, scan, test, pip, HRD
# Output: JSON array of activities with timestamps and line numbers
```

### Analysis Performed
- Categorized activities by type
- Identified script execution patterns (75 Python tests)
- Tracked script creation order (26 scripts)
- Mapped investigation phases
- Documented decision points
- Extracted key learnings

---

## Recommended Reading Order

### For Quick Understanding:
1. This index (overview)
2. `HRD_INVESTIGATION_SUMMARY.txt` (executive summary)
3. `HRD_INVESTIGATION_TIMELINE.txt` (visual flow)

### For Technical Details:
1. `HRD_INVESTIGATION_REPORT.md` (complete details)
2. `HRD_INVESTIGATION_SCRIPTS_REFERENCE.md` (script details)
3. `hrd_investigation_activities.json` (raw data)

### For Reproducing the Investigation:
1. `HRD_INVESTIGATION_TIMELINE.txt` (chronology)
2. `HRD_INVESTIGATION_SCRIPTS_REFERENCE.md` (what each script does)
3. Actual script files in `native-host/probe_*.py`
4. `HRD_INVESTIGATION_REPORT.md` (detailed methodology)

---

## Documentation Statistics

- **Total Documentation Files:** 6
- **Total Lines of Documentation:** ~2,200+
- **Total Words:** ~20,000+
- **Charts/Diagrams:** 2 ASCII diagrams
- **Code Examples:** 15+
- **Scripts Documented:** 26
- **Web Resources Documented:** 13

---

## Status

**Investigation:** COMPLETE
**Documentation:** COMPLETE
**Production System:** OPERATIONAL
**Problem:** SOLVED

The SOTA Hunter project has a fully functional rig control and logging system using direct CAT serial control and UDP ADIF, bypassing the broken HRD TCP API for mode setting.

---

## Contact & Attribution

**Investigation Date:** February 1, 2026
**Documentation Generated:** February 14, 2026
**Project:** SOTA Hunter (Chrome Extension)
**Investigation Tool:** Claude Code (Anthropic)
**Documentation Source:** Conversation transcript analysis

---

*This index and all associated documentation were generated from 174 documented activities extracted from Claude Code conversation transcripts.*
