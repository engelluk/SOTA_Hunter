# HRD Rig Control TCP Protocol - Investigation Notes

## Overview

This document records all findings from investigating Ham Radio Deluxe (HRD) Rig Control's TCP protocol on port 7809, specifically for controlling a **Yaesu FT-DX10**. The goal was to set both frequency and operating mode from a Chrome extension via a Python native messaging bridge.

**Conclusion: HRD's TCP protocol for the FT-DX10 is effectively read-only for all controls except frequency.** Mode setting does not work through any discovered command. This appears to be a limitation of HRD's rig definition for the FT-DX10, not a protocol-level issue.

## Protocol Details

### HRD v6 Binary Message Framing

HRD v6 uses a binary TCP protocol (NOT the text-based protocol described in older documentation):

```
Offset  Size    Description
0       4       Little-endian message length (includes these 4 bytes)
4       8       Signature: CD AB 34 12 34 12 CD AB
12      4       Zero bytes
16      N       UTF-16LE encoded command/response text
16+N    6       Trailing zero bytes
```

- **Total wire bytes** = 4 (length) + 8 (signature) + 4 (zeros) + N (payload) + 6 (trailing zeros)
- The 4-byte length field value = 8 + 4 + N + 6 (everything after the length field)
- **Critical:** When receiving, read 4 bytes for the length, then read `length - 4` more bytes for the body

### Connection Model

- **One command per TCP connection.** HRD processes exactly one command, sends one reply, then the connection is done. A new TCP socket must be opened for each subsequent command.
- Using `SO_LINGER` with `l_onoff=1, l_linger=0` sends RST on close, preventing CLOSE_WAIT buildup on the HRD side.
- Rapid connection attempts can overwhelm HRD with zombie connections. A short delay (300-500ms) between commands is recommended.

### Context System

Most commands require a "context" prefix obtained via `Get Context`:

```
Send: Get Context
Recv: 244
```

Subsequent commands are prefixed with `[context_number]`:

```
Send: [244] Get Frequency
Recv: 14285000
```

The context number can be cached across connections. It appears to remain stable for the lifetime of an HRD session.

## Working Commands (FT-DX10)

### Read Commands (all work correctly)

| Command | Response | Notes |
|---------|----------|-------|
| `Get Context` | `244` | No context prefix needed |
| `[ctx] Get Radio` | `FTDX-10` | Radio model identifier |
| `[ctx] Get Frequency` | `14285000` | Current VFO frequency in Hz |
| `[ctx] Get Mode` | `USB` | Current operating mode |
| `[ctx] Get Dropdowns` | `Mode,Ant. A #,...` | Comma-separated list of dropdown names |
| `[ctx] Get Dropdown-list {Mode}` | `LSB,USB,CW,...` | Dropdown items (curly braces required!) |
| `[ctx] Get Dropdown-text {Mode}` | `Mode: USB` | Current dropdown display text |
| `[ctx] Get Buttons` | `ATU,Tune,...` | Comma-separated list of button names |
| `[ctx] Get Sliders` | `AF gain,...` | Comma-separated list of slider names |
| `[ctx] Get Button-select Split` | `0` | Button state (0/1) |

### Write Commands

| Command | Response | Actually Works? |
|---------|----------|----------------|
| `[ctx] Set Frequency-Hz 14285000` | `OK` | **YES** - frequency changes on radio |
| `[ctx] Set Dropdown {Mode} N` | `OK` | **NO** - accepted but ignored |
| `[ctx] Set Dropdown Mode N` | `OK` | **NO** - always sets to LSB (index 0) |
| `[ctx] Set Mode USB` | (empty) | **NO** - no effect |
| `[ctx] Set Button-select Split 1` | `OK` | **NO** - accepted but ignored |
| `[ctx] Set Button-select Band + 1` | `OK` | **NO** - accepted but ignored |
| `[ctx] Set Slider-pos {RF gain} 50` | `OK` | **NO** - accepted but ignored |

**Only `Set Frequency-Hz` actually changes the radio state.** All other Set commands are silently ignored.

## Dropdown Name Syntax: `Mode` vs `{Mode}`

A confusing aspect of the protocol:

- `Get Dropdown-list {Mode}` (with curly braces) → returns the full mode list: `LSB,USB,CW,FM,AM,RTTY-LSB,CW-L,DATA-L,RTTY-USB,DATA-FM,FM-N,DATA-U,AM-N,PSK,DATA-FM-N`
- `Get Dropdown-list Mode` (without curly braces) → returns empty string
- `Set Dropdown {Mode} N` → returns `OK` but **never changes anything**
- `Set Dropdown Mode N` → returns `OK` and **always sets mode to LSB** regardless of N

The curly-brace syntax `{Mode}` works for reading dropdown data but is completely non-functional for writing. The non-brace syntax `Mode` partially interacts with the radio (it does change the mode) but always selects the first item (LSB), ignoring the index parameter.

## FT-DX10 Mode Dropdown Values

Index-to-mode mapping from `Get Dropdown-list {Mode}`:

| Index | Mode |
|-------|------|
| 0 | LSB |
| 1 | USB |
| 2 | CW |
| 3 | FM |
| 4 | AM |
| 5 | RTTY-LSB |
| 6 | CW-L |
| 7 | DATA-L |
| 8 | RTTY-USB |
| 9 | DATA-FM |
| 10 | FM-N |
| 11 | DATA-U |
| 12 | AM-N |
| 13 | PSK |
| 14 | DATA-FM-N |

## FT-DX10 Available Buttons

From `Get Buttons`:

```
ATU, Tune, Band +, Band -, CW Spot, DNF A, DNF B, Bk-in, CTCSS,
Chan +, Pre 2 B, Chan -, Con A, Con B, APF A, APF B, Moni, Fast,
Keyer, TX Clar, NB A, NB B, DNR A, DNR B, Scan Up, Split, MN A,
MOX, MN B, RCL, Nar, V > M, M > V, STO, Q-Split, Scan Dn,
Pre 1 A, Pre 2 A, Pre 1 B, TX, VOX, TUN, TXW, Lock, Proc,
RX Clar, Mic Eq, Power, TX tone, A <> B, TX A, TX B, B > A, A > B
```

Note: Mode names (CW, USB, LSB, etc.) are NOT in the button list, but `Get Button-select CW` still returns `0` - HRD returns `0` as a default for any button name, even non-existent ones.

## FT-DX10 Available Sliders

From `Get Sliders` (partial list):

```
AF gain, RF gain, RF Power, Squelch, Mic gain, CW Pitch, Key Speed,
IF Shift, Contour, Monitor, Noise blanker, Noise reduction, VOX gain,
SSB HCUT Freq, SSB LCUT Freq, CW HCUT Freq, CW LCUT Freq, ...
```

Slider values read as `4294967295,` (0xFFFFFFFF) which indicates the slider interface is not properly implemented for the FT-DX10.

## Other HRD Interfaces Tested

| Interface | Result |
|-----------|--------|
| OmniRig COM (`OmniRig.OmniRigX`) | Installed but "Port is not available" (COM port held by HRD) |
| HRD COM (`HRDInterface.HRDInterface`) | Not registered |
| HRD Logbook COM (`HRDLog.Logbook`) | Not registered |
| HTTP API on port 8080 | Port open but returns 404 on all paths (not HRD) |
| Ports 7810-7815 | Not open |

## What Was Tried (Exhaustive List)

### Protocol Discovery Phase
1. **Text-based UTF-16LE protocol** (initial implementation) - HRD never responded
2. **Various text protocols**: newline-terminated ASCII, CR+LF, UTF-16LE with CRLF - all timed out
3. **Binary protocol with signature** - discovered from HRD forum post, this is the correct protocol

### Connection Issues Fixed
4. **Multi-command per connection** - discovered HRD only processes ONE command per TCP connection
5. **CLOSE_WAIT zombie connections** - fixed with SO_LINGER socket option
6. **Length field off-by-4 bug** - the 4-byte length field includes itself; must subtract 4 when reading the body

### Mode Setting Attempts (All Failed)
7. `Set Mode USB` / `Set Mode CW` / `Set Mode LSB` - returns empty, no effect
8. `Set Dropdown Mode N` (indices 0-14) - returns OK, always sets LSB
9. `Set Dropdown {Mode} N` (indices 0-14) - returns OK, no effect
10. `Set Dropdown Mode CW` / `Set Dropdown Mode USB` (text values) - returns OK, no effect
11. `Set Dropdown {Mode} CW` / `Set Dropdown {Mode} USB` (text values) - returns OK, no effect
12. `Set Dropdown-text {Mode} CW` - returns empty, no effect
13. `Set Dropdown-text Mode CW` - returns empty, no effect
14. `Set Dropdown-select {Mode} 2` - returns empty, no effect
15. `Set Dropdown-select Mode 2` - returns empty, no effect
16. `Set Button-select CW 1` / `Set Button-select USB 1` etc. - returns OK, no effect
17. `Set Dropdown Mode,CW` (comma-separated) - returns OK, no effect
18. `Set Dropdown {Mode}|CW` (pipe-separated) - returns OK, no effect
19. `Set {Mode} CW` / `Set {Mode} 2` - returns empty, no effect
20. Raw CAT attempts: `MD03;`, `CAT MD03;`, `Rig MD03;`, `Serial MD03;` etc. - no effect
21. `Macro Set Mode CW`, `Script Set Mode CW`, `Run Set Mode CW` - no effect
22. `Set Frequency-Mode 14285000 CW` - returns empty, no effect
23. `Set Rig-Mode CW`, `Set Rig Mode CW` - returns empty, no effect
24. `Select Dropdown {Mode} CW` / `Select Dropdown {Mode} 2` - no effect
25. `Sync`, `Update`, `Apply`, `Refresh` after Set Dropdown - no effect
26. Context-free (no `[ctx]` prefix) dropdown commands - same results
27. Verified with other dropdowns (AGC A, Meter) - **Set Dropdown is broken for ALL dropdowns, not just Mode**
28. Verified buttons (Split, NB A, Band+) - **Set Button-select is broken for ALL buttons**
29. Verified sliders (RF gain, AF gain) - **Slider values read as 0xFFFFFFFF, Set has no effect**

### Alternative Interfaces Tested
30. OmniRig COM automation - installed but port unavailable (locked by HRD)
31. HRD COM/DDE interfaces - not registered
32. HTTP API on port 8080 - not HRD's server
33. Direct serial CAT on COM8 (Standard port) - no response (not the CAT port)
34. Direct serial CAT on COM7 (Enhanced port) - `PermissionError: Access denied` (locked by HRD)

## Hardware Details

- **Radio:** Yaesu FT-DX10
- **Connection:** USB (Silicon Labs Dual CP2105 USB to UART Bridge)
  - COM7: Enhanced COM Port (CAT control - used by HRD)
  - COM8: Standard COM Port (data/audio)
- **HRD Version:** v6 (exact version not queried)
- **HRD TCP Port:** 7809 (default)

## Conclusion

The HRD TCP protocol's write functionality is not implemented for the FT-DX10 rig definition, with the sole exception of `Set Frequency-Hz`. This makes it unsuitable for full rig control (frequency + mode) via the TCP interface.

**Recommended alternative:** Direct serial CAT control via the FT-DX10's USB COM port (COM7), bypassing HRD entirely. This requires HRD to release the COM port (either by closing HRD or configuring it to not use the port). The FT-DX10 CAT command for mode is `MD0X;` where X is: 1=LSB, 2=USB, 3=CW, 4=FM, 5=AM, 6=RTTY-LSB, 7=CW-L, 8=DATA-L, 9=RTTY-USB, A=DATA-FM, B=FM-N, C=DATA-U, D=AM-N.
