# HRD Protocol Investigation Report
## SOTA Hunter Project - Detailed Chronological Account

---

## Executive Summary

This report documents the extensive investigation into Ham Radio Deluxe (HRD) protocols for the SOTA Hunter project. The investigation spanned multiple phases, involved 174 recorded activities (116 Bash commands, 19 web searches, 13 web page fetches, and 26 Python scripts created), and ultimately led to a hybrid solution using direct CAT control for rig operations and UDP ADIF for logging.

**Key Findings:**
- HRD v6 TCP API (port 7809) is **broken** for mode setting despite accepting commands
- Direct Yaesu CAT serial control successfully replaced HRD for rig operations
- HRD Logbook UDP ADIF (port 2333) works reliably for QSO logging

---

## Phase 1: Initial Setup & TCP Protocol Investigation

### Objective
Implement rig control for Yaesu FT-DX10 via Ham Radio Deluxe v6 TCP API.

### Packages Installed
1. **pyserial** - For serial port communication (later used for direct CAT)
2. **pywinauto** - For Windows GUI automation experiments

### Web Research Conducted

#### Protocol Documentation Searches
1. "HRD Ham Radio Deluxe rig control TCP protocol port 7809 specification"
   - Searched for official protocol documentation
   - Finding: No official public documentation available

2. "HRD rig control API protocol context get frequency set frequency TCP commands"
   - Looking for command syntax and message format
   - Found community reverse-engineering efforts

3. GitHub searches for existing implementations:
   - "ham radio deluxe TCP client python socket 7809 protocol"
   - "slice-master HRD protocol TCP socket connect"
   - Found several community projects

4. Binary protocol investigation:
   - "HRD IP server protocol C# utf-16 unicode socket send receive message format"
   - "HRD v6 v7 IP server protocol binary 4 byte length header connect python"
   - Discovered: UTF-16LE encoding with 4-byte little-endian length prefix

5. Archive searches for deleted forum posts:
   - "site:web.archive.org forums.hamradiodeluxe.com Rig Control API"
   - Cached forum posts about binary protocol

### Key Web Resources Examined

1. **forums.hamradiodeluxe.com/node/34951**
   - HRD Rig Control API discussion thread

2. **forums.hamradiodeluxe.com/node/40968**
   - Rig Control API Documentation (binary protocol details)

3. **github.com/krisp/MiniDeluxe**
   - C# implementation of HRD client - excellent reference

4. **github.com/K1DBO/slice-master-6000**
   - Another HRD protocol implementation for FlexRadio

5. **sivantoledotech.wordpress.com**
   - "Reverse Engineering the HRD Remote Serial Protocol"
   - Detailed blog post about protocol analysis

6. **remotehams.com/forums**
   - Community HRD protocol discussions

7. **manualzz.com**
   - HRD Rig Control v6.3 Server Installation Manual

8. **support.hamradiodeluxe.com**
   - QSO Forwarding documentation

### Key Technical Discoveries

**HRD TCP Protocol (Port 7809):**
- Binary protocol using UTF-16LE encoding
- 4-byte little-endian length prefix before each message
- Command format: text-based commands in UTF-16LE
- Basic commands: "get context", "get frequency-hz", "set frequency-hz"

---

## Phase 2: Initial HRD_CLIENT.PY Implementation

### Script Created: `hrd_client.py`

**Initial Implementation Features:**
- TCP socket connection to localhost:7809
- Binary protocol with UTF-16LE encoding
- 4-byte length prefix (little-endian)
- Command support:
  - `get context` - Retrieve rig state
  - `get frequency-hz` - Read current frequency
  - `set frequency-hz` - Change frequency
  - `set dropdown mode` - Change operating mode

### Initial Testing Results
- ✅ Connection successful to HRD server
- ✅ Frequency reading worked correctly
- ✅ Frequency setting worked
- ❌ Mode detection unreliable
- ❌ **Mode setting FAILED** (commands accepted but no effect)

---

## Phase 3: Mode Setting Investigation (The Big Problem)

### Problem Statement
The "Set Dropdown Mode" command was accepted by HRD (returned OK response) but **did not actually change the radio's operating mode**. This critical functionality was essential for SOTA operations where different modes are used.

### Systematic Investigation Scripts Created

#### 1. probe_mode.py (Line 865)
**Purpose:** Test basic mode dropdown commands

**Tested:**
- `Set Dropdown Mode USB`
- `Set Dropdown Mode LSB`
- Various syntax variations

**Result:** Commands accepted (OK response) but mode did not change

---

#### 2. probe_mode2.py (Line 891)
**Purpose:** Try {Mode} curly-brace syntax found in some documentation

**Tested:**
- `Set Dropdown {Mode} USB`
- Curly-brace variable substitution

**Result:** Still no change to actual radio mode

---

#### 3. probe_mode3.py (Line 912)
**Purpose:** Text-based dropdown and alternative commands

**Tested:**
- Different command formats
- Alternative syntax variations
- Case sensitivity tests

**Result:** No success with any variation

---

#### 4. probe_mode4.py (Line 951)
**Purpose:** Dynamic dropdown lookup with fresh context

**Approach:**
- Get fresh context before each command
- Add delays between operations
- Verify mode after each attempt

**Result:** Still failing despite fresh state

---

#### 5. probe_mode5.py (Line 978)
**Purpose:** Systematic test of all dropdown indices

**Methodology:**
- Test `Set Dropdown Mode N` for N=0 through 14
- Record actual mode after each attempt
- Try every possible index value

**Result:** Comprehensive test showed NO indices worked

---

#### 6. probe_cat.py (Line 1000)
**Purpose:** Try raw CAT command injection through HRD

**Approach:**
- Attempt to send raw Yaesu CAT commands via HRD API
- Test if HRD would pass through CAT commands

**Result:** CAT commands not supported by HRD TCP API

---

#### 7. probe_vfo.py (Line 1040)
**Purpose:** Check VFO A/B distinction, try VFO-specific commands

**Tested:**
- VFO-A specific commands
- VFO-B specific commands
- VFO selection before mode setting

**Result:** No effect on mode setting capability

---

#### 8. probe_mode_final.py (Line 1206)
**Purpose:** Deep investigation - every unexplored approach

**Comprehensive Testing:**
- Multiple command variations
- Different timing strategies
- Format permutations
- Edge cases

**Result:** Exhaustive testing confirmed mode setting is broken in HRD TCP API

---

#### 9. probe_mode_final2.py (Line 1276)
**Purpose:** Targeted mode tests - context-free, sync commands

**Final Tests:**
- Commands without context requirement
- Synchronous operation tests
- COM port verification checks

**Conclusion:** **Definitively determined the HRD TCP API cannot set mode**

---

## Phase 4: Alternative Approaches

After extensive testing proved HRD TCP API mode setting was fundamentally broken, alternative approaches were investigated.

### 10. probe_alternatives.py (Line 1332)
**Purpose:** Check port 8080 HTTP API and list COM ports

**Actions:**
1. Checked if HRD offers HTTP API on port 8080
2. Enumerated available COM ports for direct serial access
3. Listed all serial devices

**Result:**
- No HTTP API available
- ✅ **Found COM7 available for direct CAT control**

---

### 11. probe_other_dropdowns.py (Line 1361)
**Purpose:** Verify if ANY dropdown commands work in HRD

**Tested:**
- AGC dropdown (safe, reversible)
- Other non-critical dropdowns
- Verify command syntax itself

**Result:**
- ✅ Confirmed `Set Dropdown` command syntax works
- ✅ Other dropdowns can be changed
- ❌ **Mode dropdown specifically is broken** - not a syntax issue

---

### 12. probe_write_test.py (Line 1387)
**Purpose:** Test if ANY Set commands besides frequency work

**Tested:**
- Slider controls
- Button operations
- Safe, reversible operations

**Result:** Most write operations via HRD TCP API are unreliable
- Frequency setting works
- Most other controls fail or behave inconsistently

---

### 13. probe_hrd_gui.py (with pywinauto)
**Purpose:** Explore HRD GUI automation as workaround

**Approach:**
- Use Windows GUI automation to control HRD window
- Simulate button clicks and dropdown selections

**Result:**
- Too fragile (window focus issues)
- Not reliable for production use
- Abandoned this approach

---

## Phase 5: Direct CAT Control Solution

### Decision Point
After exhaustive testing, the decision was made to:
- ✅ **Abandon HRD TCP API for mode setting**
- ✅ **Implement direct serial CAT control** to the radio
- ✅ Keep HRD frequency reading for display purposes

### COM Port Investigation

**Using probe_alternatives.py:**
- Enumerated all COM ports on system
- Identified **COM7** as the FT-DX10 serial interface
- Verified port availability

### CAT Protocol Research

**Yaesu FT-DX10 CAT Protocol:**
- **Baud rate:** 9600
- **Data format:** 8N2 (8 data bits, no parity, 2 stop bits)
- **Command format:** 5-byte commands terminated with semicolon
- **Standard Yaesu CAT commands**

### Scripts Created for Direct CAT Control

#### 14. test_cat.py (First version, Line 1451)
**Purpose:** Test direct Yaesu CAT control on COM7

**Commands Tested:**
- `FA;` - Read VFO-A frequency
- `MD0;` - Set mode to LSB
- `MD1;` - Set mode to USB
- `MD2;` - Set mode to CW

**Result:** ✅ **Direct CAT communication successful!**

---

#### 15. test_cat.py (Enhanced version)
**Purpose:** Test CAT mode and frequency changes

**Features Added:**
- Mode setting (MD commands for LSB/USB/CW)
- Frequency setting (FA command with padding)
- Read-back verification

**Result:** ✅ Mode setting works reliably via CAT

---

#### 16. cat_client.py (Production implementation)
**Purpose:** Direct Yaesu CAT serial client for FT-DX10

**Full Implementation:**

**CATClient Class Features:**
- Connection management (COM7, 9600 baud, 8N2)
- Mode mapping:
  - SSB_USB → MD1
  - SSB_LSB → MD2
  - CW → MD3
  - FM → MD4
  - AM → MD5
  - RTTY_LSB → MD6
  - CW_R → MD7
  - DATA_LSB → MD8
  - RTTY_USB → MD9
  - DATA_FM → MD10
  - FM_N → MD11
  - DATA_USB → MD12
  - AM_N → MD13
  - C4FM → MD14

- Frequency control with validation
- Band detection logic (HF/VHF/UHF)
- Error handling and retries

**Result:** ✅ Production-ready CAT client

---

#### 17. test_cat.py (Final comprehensive test)
**Purpose:** Comprehensive test of CATClient

**Test Coverage:**
- Mode mapping accuracy for all modes
- Band plan detection (2m, 70cm, HF)
- Frequency accuracy and padding
- Real-world scenarios (tune to actual SOTA spots)
- Edge cases and error conditions

**Result:**
- ✅ All tests passed
- ✅ Mode setting works reliably
- ✅ Frequency control accurate
- ✅ **Direct CAT successfully replaced HRD for rig control**

---

## Phase 6: HRD Logbook Integration (Separate Investigation)

While HRD rig control was problematic, the logbook functionality was investigated separately for QSO logging.

### Web Research for Logbook

1. **"HRD Logbook API TCP protocol add QSO programmatically"**
   - Looking for programmatic QSO logging API
   - Found limited TCP API support

2. **"HRD Logbook ADIF import command line external logging API"**
   - Checking for command-line ADIF import
   - Manual import only, no CLI

3. **"HRD Logbook UDP port 2333 ADIF record format QSO forwarding WSJT-X"**
   - ✅ **Discovered UDP-based QSO forwarding**
   - Same protocol used by WSJT-X

4. **"N1MM UDP broadcast QSO ADIF format specification port 2333 fields"**
   - Researched standard ADIF UDP format
   - Found field specifications

5. **"WSJT-X ADIF UDP broadcast example record format SIG SIG_INFO"**
   - WSJT-X uses UDP for QSO logging to HRD
   - Excellent documentation and examples

6. **"ADIF specification SIG SIG_INFO SOTA fields format example"**
   - How to encode SOTA references in ADIF
   - SIG="SOTA", SIG_INFO="W7W/LC-001"

7. **"python send ADIF UDP QSO log HRD logbook port 2333 example"**
   - Python implementation examples
   - Socket programming for UDP

### Key Finding: UDP ADIF Protocol

**HRD Logbook UDP ADIF Receiver:**
- **Port:** 2333 (localhost)
- **Protocol:** UDP
- **Format:** ADIF records (Amateur Data Interchange Format)
- **Compatibility:** Same format used by WSJT-X, N1MM+, other logging software

**Advantages:**
- Much simpler than TCP API
- Well-documented standard format
- Widely used and reliable
- Supports SOTA-specific fields (SIG/SIG_INFO)

### Implementation in bridge.py

**Features Added:**
- UDP socket to localhost:2333
- ADIF record formatting
- SOTA-specific fields:
  - `<CALL:>` - Callsign
  - `<QSO_DATE:>` - Date in YYYYMMDD
  - `<TIME_ON:>` - Time in HHMMSS
  - `<BAND:>` - Band (2m, 70cm, etc.)
  - `<MODE:>` - Mode (SSB, CW, FM)
  - `<FREQ:>` - Frequency in MHz
  - `<RST_SENT:>` - Signal report sent
  - `<RST_RCVD:>` - Signal report received
  - `<SIG:4>SOTA` - Special Interest Group
  - `<SIG_INFO:>` - SOTA reference (e.g., W7W/LC-001)
  - `<COMMENT:>` - Additional notes

**"Log QSO" Button:**
- Sends SOTA chase contacts to HRD Logbook
- Automatic field population from SOTAwatch spot
- Real-time QSO logging

**Result:** ✅ QSO logging to HRD works perfectly via UDP ADIF

---

## Final Architecture

### Rig Control: Direct CAT (cat_client.py)
- **Interface:** Serial COM7
- **Protocol:** Yaesu CAT (9600 8N2)
- **Functions:**
  - Set frequency
  - Set mode
  - Read frequency
  - Read mode

**Advantages:**
- ✅ Reliable mode setting
- ✅ Fast response
- ✅ No dependency on HRD bugs
- ✅ Direct hardware control

### Logging: HRD Logbook UDP ADIF (bridge.py)
- **Interface:** UDP localhost:2333
- **Protocol:** ADIF records
- **Functions:**
  - Log SOTA chase QSOs
  - Include SOTA reference
  - Standard amateur radio logging format

**Advantages:**
- ✅ Simple, well-documented protocol
- ✅ Industry standard format
- ✅ Reliable delivery
- ✅ SOTA field support

---

## Statistics Summary

### Total Activities Recorded: 174

**Breakdown by Type:**
- **Bash Commands:** 116
  - Port scanning/enumeration: 5
  - Python test executions: 75
  - Pip installs: 2
  - Other commands: 34

- **Web Searches:** 19
  - Protocol documentation: 7
  - Logbook integration: 7
  - Implementation examples: 5

- **Web Page Fetches:** 13
  - Forums and documentation: 6
  - GitHub repositories: 3
  - Archive searches: 2
  - Blog posts: 2

- **Python Scripts Created:** 26
  - HRD TCP client iterations: 6
  - Mode investigation probes: 9
  - Alternative approach tests: 4
  - CAT control implementations: 4
  - Test scripts: 3

### Scripts Created (In Order)

1. **bridge.py** - Chrome Native Messaging host (multiple iterations)
2. **hrd_client.py** - HRD TCP client (6 versions, ultimately deprecated)
3. **config.py** - Configuration and version info
4. **probe_mode.py** - Basic mode dropdown tests
5. **probe_mode2.py** - Curly-brace syntax tests
6. **probe_mode3.py** - Alternative command formats
7. **probe_mode4.py** - Dynamic dropdown with fresh context
8. **probe_mode5.py** - Systematic index testing
9. **probe_cat.py** - CAT command injection attempts
10. **probe_vfo.py** - VFO-specific commands
11. **test_tune.py** - End-to-end tune() method test
12. **quick_test.py** - Quick connection tests (3 versions)
13. **probe_mode_final.py** - Deep investigation
14. **probe_mode_final2.py** - Final targeted tests
15. **probe_alternatives.py** - HTTP API and COM port checks
16. **probe_other_dropdowns.py** - Verify dropdown syntax
17. **probe_write_test.py** - Test other Set commands
18. **probe_hrd_gui.py** - GUI automation experiments
19. **test_cat.py** - Direct CAT testing (7 versions)
20. **cat_client.py** - Production CAT client

---

## Key Lessons Learned

### 1. HRD TCP API Limitations
- Frequency control works
- Mode setting is **broken** (accepts commands but doesn't execute)
- Many write operations are unreliable
- Not suitable for automated rig control

### 2. Direct Hardware Control is Better
- CAT protocol is well-documented
- Direct serial control is more reliable
- No dependency on third-party software bugs
- Faster response times

### 3. UDP ADIF is the Right Protocol for Logging
- Industry standard
- Simple implementation
- Widely supported
- Reliable

### 4. Systematic Investigation Pays Off
- Created 13+ probe scripts to isolate the problem
- Tested every possible variation
- Documented what works and what doesn't
- Led to correct architectural decision

### 5. Community Resources are Invaluable
- GitHub projects provided protocol examples
- Forum posts (even archived) had critical details
- Blog posts about reverse engineering were helpful
- WSJT-X source code showed ADIF implementation

---

## Conclusion

The HRD protocol investigation was extensive and thorough. Through systematic testing and experimentation, the investigation:

1. ✅ Identified HRD TCP API mode setting as fundamentally broken
2. ✅ Developed working direct CAT serial control
3. ✅ Implemented reliable UDP ADIF logging
4. ✅ Created 26 test scripts and tools
5. ✅ Documented everything for future reference

**Final Solution:**
- **Rig Control:** Direct Yaesu CAT via COM7 (cat_client.py)
- **Logging:** HRD Logbook via UDP ADIF on port 2333

This hybrid approach leverages the best of both worlds: reliable direct hardware control for rig operations and standard logging protocols for QSO recording.

---

## Files Generated During Investigation

All investigation scripts and tools are preserved in:
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\`

**Key Files:**
- `cat_client.py` - Production CAT client (ACTIVE)
- `bridge.py` - Native messaging host with UDP ADIF logging (ACTIVE)
- `hrd_client.py` - HRD TCP client (DEPRECATED - mode setting broken)
- `probe_*.py` - Investigation scripts (13 files, ARCHIVED)
- `test_*.py` - Test scripts (4 files, ARCHIVED)

**Activity Logs:**
- `hrd_investigation_activities.json` - Complete activity log (174 entries)

---

*Investigation Period: February 1, 2026*
*Total Investigation Time: Extensive multi-session effort*
*Scripts Created: 26*
*Web Resources Consulted: 13*
*Problem Solved: Yes - Using direct CAT control*
