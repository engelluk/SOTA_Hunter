# HRD Investigation Scripts Reference Guide

## Quick Reference for All Scripts Created During Investigation

---

## Production Scripts (ACTIVE)

### cat_client.py
**Location:** `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\cat_client.py`

**Purpose:** Direct Yaesu CAT serial client for FT-DX10 rig control

**Key Features:**
- Serial communication (COM7, 9600 baud, 8N2)
- Mode mapping (LSB/USB/CW/FM/AM/RTTY/DATA/C4FM)
- Frequency control with validation
- Band detection logic

**Usage:**
```python
from cat_client import CATClient

client = CATClient()
client.connect()
client.set_mode("SSB_USB")
client.set_frequency(7040000)  # 7.040 MHz
freq = client.get_frequency()
mode = client.get_mode()
client.disconnect()
```

**Status:** ✅ ACTIVE - Production rig control

---

### bridge.py
**Location:** `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\bridge.py`

**Purpose:** Chrome Native Messaging host with rig control and logging

**Key Features:**
- Native messaging protocol
- CATClient integration for rig control
- UDP ADIF sender for HRD Logbook (port 2333)
- SOTAwatch API integration
- Command handling (tune, get_frequency, log_qso)

**Status:** ✅ ACTIVE - Production native messaging host

---

## Deprecated Scripts (ARCHIVED)

### hrd_client.py
**Location:** `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\hrd_client.py`

**Purpose:** HRD TCP client (port 7809) for rig control

**Why Deprecated:**
- Mode setting doesn't work (HRD API bug)
- Unreliable for write operations
- Replaced by direct CAT control

**What Works:**
- ✅ Frequency reading
- ✅ Frequency setting
- ❌ Mode setting (BROKEN)

**Status:** ❌ DEPRECATED - Do not use for mode control

---

## Investigation Scripts (ARCHIVED)

All investigation scripts are preserved for reference and documentation purposes.

### Mode Setting Investigation Scripts

#### probe_mode.py
**First Used:** Line 865 of investigation transcript

**Purpose:** Test basic mode dropdown commands

**Commands Tested:**
- `Set Dropdown Mode USB`
- `Set Dropdown Mode LSB`
- Various syntax variations

**Result:** Commands accepted but mode did not change

**Key Learning:** Initial discovery that mode setting doesn't work

---

#### probe_mode2.py
**First Used:** Line 891

**Purpose:** Try {Mode} curly-brace syntax

**Commands Tested:**
- `Set Dropdown {Mode} USB`
- Curly-brace variable substitution

**Result:** No change to radio mode

**Key Learning:** Variable substitution syntax doesn't help

---

#### probe_mode3.py
**First Used:** Line 912

**Purpose:** Text-based dropdown and alternative command formats

**Approaches Tested:**
- Different command formats
- Case sensitivity variations
- Alternative syntax

**Result:** No success with any variation

**Key Learning:** Not a syntax formatting issue

---

#### probe_mode4.py
**First Used:** Line 951

**Purpose:** Dynamic dropdown lookup with fresh context

**Approach:**
- Get fresh context before each command
- Add delays between operations
- Verify mode after each attempt

**Result:** Still failing despite fresh state

**Key Learning:** Not a stale context issue

---

#### probe_mode5.py
**First Used:** Line 978

**Purpose:** Systematic test of all dropdown indices

**Methodology:**
```python
# Test Set Dropdown Mode N for N=0..14
for index in range(15):
    send(f"Set Dropdown Mode {index}")
    actual_mode = read_mode()
    log(f"Index {index} → Mode: {actual_mode}")
```

**Result:** NO indices worked - comprehensive negative test

**Key Learning:** Problem is fundamental, not index-related

---

#### probe_cat.py
**First Used:** Line 1000

**Purpose:** Try raw CAT command injection through HRD

**Approach:**
```python
# Attempt to send Yaesu CAT commands via HRD
send("MD01;")  # CAT command for USB
```

**Result:** CAT commands not supported by HRD TCP API

**Key Learning:** HRD doesn't provide CAT pass-through

---

#### probe_vfo.py
**First Used:** Line 1040

**Purpose:** Check VFO A/B distinction

**Commands Tested:**
- VFO-A specific commands
- VFO-B specific commands
- VFO selection before mode setting

**Result:** No effect on mode setting

**Key Learning:** VFO selection doesn't affect mode control

---

#### probe_mode_final.py
**First Used:** Line 1206

**Purpose:** Deep investigation - every unexplored approach

**Comprehensive Tests:**
- Multiple command variations
- Different timing strategies
- Format permutations
- Edge cases

**Result:** Exhaustive testing - mode setting definitively broken

**Key Learning:** Confirmed HRD API bug beyond reasonable doubt

---

#### probe_mode_final2.py
**First Used:** Line 1276

**Purpose:** Final targeted tests

**Final Attempts:**
- Commands without context requirement
- Synchronous operation tests
- COM port verification

**Result:** Definitive conclusion - HRD TCP API cannot set mode

**Key Learning:** Time to abandon HRD and use direct CAT

---

### Alternative Approach Scripts

#### probe_alternatives.py
**First Used:** Line 1332

**Purpose:** Explore alternative control methods

**Actions:**
1. Check for HTTP API on port 8080
2. Enumerate COM ports
3. List serial devices

**Key Code:**
```python
import serial.tools.list_ports

# List all COM ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")
```

**Result:**
- ✅ Found COM7 (FT-DX10)
- ❌ No HTTP API available

**Key Learning:** Direct serial is the solution

---

#### probe_other_dropdowns.py
**First Used:** Line 1361

**Purpose:** Verify if ANY dropdown commands work

**Commands Tested:**
```python
# Test AGC dropdown (safe to change)
send("Set Dropdown AGC Fast")
send("Set Dropdown AGC Slow")

# Test other dropdowns
send("Set Dropdown <other_control> <value>")
```

**Result:**
- ✅ Other dropdowns CAN be changed
- ❌ Mode dropdown specifically is broken

**Key Learning:** Not a general dropdown bug - Mode is uniquely broken

---

#### probe_write_test.py
**First Used:** Line 1387

**Purpose:** Test if ANY Set commands besides frequency work

**Commands Tested:**
```python
# Slider controls
send("Set Slider RF-Gain 50")

# Button operations
send("Set Button Monitor On")
send("Set Button Monitor Off")
```

**Result:** Most write operations are unreliable

**Key Learning:** HRD TCP API has widespread write operation issues

---

#### probe_hrd_gui.py
**First Used:** After Line 1387

**Purpose:** GUI automation as workaround

**Approach:**
```python
from pywinauto import Desktop

# Find HRD window
app = Desktop(backend="win32").window(title_re=".*Ham Radio Deluxe.*")

# Simulate clicking mode dropdown
mode_dropdown = app.child_window(title="Mode", control_type="ComboBox")
mode_dropdown.select("USB")
```

**Result:** Too fragile for production

**Key Learning:** GUI automation not reliable enough

---

### CAT Control Development Scripts

#### test_cat.py (Version 1)
**First Used:** Line 1451

**Purpose:** Initial test of direct CAT control

**Basic Commands:**
```python
import serial

ser = serial.Serial('COM7', 9600, bytesize=8, parity='N', stopbits=2)

# Read frequency
ser.write(b'FA;')
response = ser.read(11)  # FAxxxxxxxxx;

# Set mode to USB
ser.write(b'MD01;')
```

**Result:** ✅ CAT communication successful!

**Key Learning:** Direct CAT works - this is the solution

---

#### test_cat.py (Enhanced Versions)
**Iterations:** 7 total versions

**Progressive Improvements:**
1. Basic commands (FA, MD)
2. Mode setting with verification
3. Frequency setting with padding
4. Error handling
5. Mode mapping
6. Band detection
7. Comprehensive testing

**Final Version Features:**
- Complete mode map (15 modes)
- Frequency validation
- Band plan logic
- Real-world test scenarios

---

### Quick Test Scripts

#### quick_test.py
**Versions:** 3 iterations

**Purpose:** Quick connection and functionality tests

**Usage:**
```bash
cd "C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host"
python quick_test.py
```

**What it Tests:**
- Connection to HRD or radio
- Basic command execution
- Quick verification

---

#### test_tune.py
**First Used:** Line 1093

**Purpose:** End-to-end test of tune() method

**Test Scenario:**
```python
# Simulate tuning to SOTA spot
client.tune(
    frequency=7040000,  # 7.040 MHz
    mode="SSB_USB"
)

# Verify
assert client.get_frequency() == 7040000
assert client.get_mode() == "SSB_USB"
```

---

## How to Use This Reference

### For Future Development

1. **Need rig control?** → Use `cat_client.py` (ACTIVE)
2. **Need to log QSOs?** → Use UDP ADIF in `bridge.py` (ACTIVE)
3. **Don't use** → `hrd_client.py` for mode control (BROKEN)

### For Understanding the Investigation

1. **What was tried?** → Read probe_*.py scripts in order
2. **Why did it fail?** → Check Results section of each script
3. **What was learned?** → See Key Learning for each script

### For Similar Projects

1. **Testing third-party APIs?** → Use systematic probe script approach
2. **API not working?** → Consider direct hardware control (CAT/serial)
3. **Need logging?** → Look for industry standards (ADIF, UDP)

---

## Script Execution Order (Chronological)

```
Phase 1: Initial Implementation
├── bridge.py (v1-4)
├── hrd_client.py (v1-6)
└── config.py

Phase 2: Mode Investigation (The Big Problem)
├── probe_mode.py
├── probe_mode2.py
├── probe_mode3.py
├── probe_mode4.py
├── probe_mode5.py
├── probe_cat.py
├── probe_vfo.py
├── probe_mode_final.py
└── probe_mode_final2.py

Phase 3: Alternative Approaches
├── probe_alternatives.py
├── probe_other_dropdowns.py
├── probe_write_test.py
└── probe_hrd_gui.py

Phase 4: CAT Solution
├── test_cat.py (v1)
├── test_cat.py (v2)
├── test_cat.py (v3)
├── test_cat.py (v4)
├── test_cat.py (v5)
├── test_cat.py (v6)
├── test_cat.py (v7)
├── cat_client.py
└── test_tune.py

Phase 5: Integration
└── bridge.py (final with CAT + UDP ADIF)
```

---

## Testing Checklist

If you need to verify the investigation findings:

### HRD TCP API Tests (Should Fail)
```bash
cd "C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host"

# Test mode setting (WILL FAIL)
python probe_mode.py

# Test other dropdowns (SHOULD WORK)
python probe_other_dropdowns.py

# Verify mode is broken, other controls work
```

### CAT Control Tests (Should Succeed)
```bash
# Test direct CAT (WILL WORK)
python test_cat.py

# Expected output:
# ✅ Connected to COM7
# ✅ Current frequency: 7040000
# ✅ Set mode to USB
# ✅ Mode verified: USB
# ✅ All tests passed
```

### UDP ADIF Tests (Should Succeed)
```python
# Test QSO logging
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
adif = "<CALL:5>W1AW <QSO_DATE:8>20260201 <TIME_ON:6>120000 <BAND:3>40m <MODE:3>SSB <eor>"
sock.sendto(adif.encode('utf-8'), ('127.0.0.1', 2333))

# Check HRD Logbook - QSO should appear
```

---

## Key Takeaways

### What Works ✅
- Direct CAT serial control (cat_client.py)
- UDP ADIF logging (bridge.py → port 2333)
- HRD TCP frequency reading
- HRD TCP frequency setting

### What Doesn't Work ❌
- HRD TCP mode setting (broken in HRD v6)
- HRD TCP most write operations
- GUI automation (too fragile)
- CAT pass-through via HRD (not supported)

### Best Practices Learned
1. Test systematically (create probe scripts)
2. Document negative results
3. Consider direct hardware control
4. Use industry standards when available
5. Don't rely on proprietary APIs for critical functions

---

## File Locations

**Production Code:**
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\cat_client.py`
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\bridge.py`

**Investigation Scripts:**
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\probe_*.py`
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\test_*.py`

**Documentation:**
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\HRD_INVESTIGATION_REPORT.md`
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\HRD_INVESTIGATION_SUMMARY.txt`
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\HRD_INVESTIGATION_SCRIPTS_REFERENCE.md` (this file)

**Activity Logs:**
- `C:\Users\X1\Documents\AI tests\SOTA_Hunter\hrd_investigation_activities.json`

---

*Scripts Reference Guide*
*Generated: February 14, 2026*
*Investigation Period: February 1, 2026*
*Total Scripts: 26*
