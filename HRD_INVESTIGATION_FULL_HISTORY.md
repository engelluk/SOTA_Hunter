# Full Investigation History

## Phase 1: Initial HRD TCP Protocol Research

**The problem:** No official public documentation for HRD's TCP protocol on port 7809 exists.

**19 web searches** were performed across:
- HRD forums (`forums.hamradiodeluxe.com` — 2 threads found)
- GitHub repos — found **MiniDeluxe** (C# HRD client by krisp) and **slice-master-6000** (K1DBO's FlexRadio HRD integration)
- Sivan Toledo's blog (`sivantoledotech.wordpress.com`) — reverse-engineering HRD's serial protocol
- `remotehams.com` forums
- `manualzz.com` — HRD v6.3 Server Installation Manual
- Web Archive searches for deleted forum posts
- 13 web pages fetched and analyzed in total

**Key discovery:** Older documentation described a simple text-based UTF-16LE protocol, but HRD v6 actually uses a **binary protocol** with an 8-byte signature (`CD AB 34 12 34 12 CD AB`), zero padding, and a length field that includes itself.

## Phase 2: HRD Client — 6 Iterations of `hrd_client.py`

**Version 1 (initial commit):** Simple text-based UTF-16LE protocol — HRD never responded. Used persistent TCP connection with handshake.

**Version 2:** Discovered the binary framing from forum posts. Rewrote with signature-based message framing. Hit the **one-command-per-connection** problem — HRD only processes a single command per TCP socket, then goes silent.

**Version 3:** Switched to one-shot TCP connections. Hit **CLOSE_WAIT zombie buildup** — HRD's side kept accumulating dead connections. Fixed with `SO_LINGER` socket option to send RST on close.

**Version 4:** Discovered the **context system** — most commands need a numeric prefix from `Get Context`. Cached the context number. Reading worked perfectly: frequency, mode, radio model, dropdown lists, button lists, slider lists.

**Version 5:** Added dropdown-based mode setting with `Set Dropdown Mode {index}`, readback verification, and fallback to `Set Mode {name}`. **Mode setting still broken.**

**Version 6 (final):** Disabled mode setting entirely with a comment explaining it's non-functional, to stop the code from forcing the radio to LSB.

## Phase 3: The Mode Setting Investigation — 13 Probe Scripts

This was the most intensive phase. **75 Python test executions** were run across 13 purpose-built probe scripts:

| Script | Purpose | What it tested |
|---|---|---|
| `probe_mode.py` | Basic dropdown commands | `Set Dropdown Mode USB/LSB/CW` |
| `probe_mode2.py` | Curly-brace syntax | `Set Dropdown {Mode} USB` |
| `probe_mode3.py` | Alternative command formats | Case variations, different separators |
| `probe_mode4.py` | Fresh context per command | New context before each Set, with delays |
| `probe_mode5.py` | Systematic index sweep | `Set Dropdown Mode N` for N=0..14 — all 15 FT-DX10 modes |
| `probe_cat.py` | CAT injection through HRD | `MD03;`, `CAT MD03;`, `Rig MD03;`, `Serial MD03;` |
| `probe_vfo.py` | VFO-specific commands | VFO-A/B specific mode setting |
| `probe_mode_final.py` | Every unexplored approach | Format permutations, timing strategies, edge cases |
| `probe_mode_final2.py` | Context-free & sync commands | Commands without `[ctx]` prefix, `Sync`/`Update`/`Apply` after Set |
| `probe_alternatives.py` | HTTP API + COM port scan | Port 8080 check, enumerated serial ports |
| `probe_other_dropdowns.py` | Other dropdowns (AGC, Meter) | Verified `Set Dropdown` is broken for ALL dropdowns, not just Mode |
| `probe_write_test.py` | All other Set commands | Buttons (`Split`, `NB A`, `Band+`), sliders (`RF gain`, `AF gain`) — all broken |
| `probe_hrd_gui.py` | GUI automation (pywinauto) | Window automation of HRD's UI — too fragile, abandoned |

**Packages installed on the fly:** `pyserial`, `pywinauto`

**The 34 specific attempts** documented in `HRD_PROTOCOL_NOTES.md` include:
- 6 different `Set Dropdown` syntax variations (with/without braces, text vs index)
- `Set Dropdown-text`, `Set Dropdown-select` variants
- `Set Button-select` for mode names
- Comma-separated, pipe-separated formats
- `Set {Mode}`, `Set Rig-Mode`, `Set Rig Mode`, `Set Frequency-Mode`
- Raw CAT passthrough (`MD03;`, `CAT MD03;`, `Rig MD03;`)
- Macro/Script/Run command injection
- Post-set `Sync`, `Update`, `Apply`, `Refresh` commands
- Context-free (no `[ctx]` prefix) variants

**Conclusion:** `Set Frequency-Hz` is the ONLY write command that works. Everything else — dropdowns, buttons, sliders — is accepted but silently ignored. Slider reads return `0xFFFFFFFF`. This is specific to the FT-DX10 rig definition in HRD.

## Phase 4: Alternative Interfaces Tested

| Interface | How tested | Result |
|---|---|---|
| OmniRig COM (`OmniRig.OmniRigX`) | Python COM automation | "Port is not available" — COM7 locked by HRD |
| HRD COM interface (`HRDInterface.HRDInterface`) | Registry lookup | Not registered |
| HRD Logbook COM (`HRDLog.Logbook`) | Registry lookup | Not registered |
| HTTP API on port 8080 | `probe_alternatives.py` | Port open but 404 on all paths — not HRD |
| Ports 7810–7815 | Port scanning | Not open |
| COM8 (Standard port) | Serial probe | No response (it's the data/audio port) |
| COM7 (Enhanced port) with HRD running | Serial probe | `PermissionError: Access denied` — HRD holds the lock |

## Phase 5: Direct CAT — 7 iterations of `test_cat.py`

Once HRD was closed to release COM7, direct serial CAT was tested:

| Version | What was tested | Result |
|---|---|---|
| v1 | Basic `FA;` frequency read | Works |
| v2 | `MD0;` mode read | Works |
| v3 | `FA014285000;` frequency set | Works |
| v4 | `MD02;` mode set (USB) | Works |
| v5 | Mode-before-frequency ordering | Prevents VFO drift on band changes |
| v6 | Full mode mapping table (all 15 FT-DX10 modes) | All correct |
| v7 | Comprehensive test suite — 30 test cases | All passing |

This led to the production `cat_client.py` (183 lines) with SSB sideband by band plan, digital mode mapping, and readback verification.

## Phase 6: QSO Logging Research

**7 web searches** for logbook integration:
- HRD Logbook TCP API — poorly documented, used only by QSO Relay
- ADIF file import — manual GUI process, not automatable
- **UDP ADIF on port 2333** — discovered this is the same protocol WSJT-X uses
- ADIF SIG/SIG_INFO fields for SOTA references
- Python UDP socket examples

Led to `adif_logger.py` and the Log button feature.

## By the Numbers

| Metric | Count |
|---|---|
| Total recorded activities | 174 |
| Bash commands executed | 116 |
| Python test script executions | 75 |
| Web searches | 19 |
| Web pages fetched and analyzed | 13 |
| Python scripts created on the fly | 26 |
| HRD mode setting approaches tried | 34 |
| Versions of `hrd_client.py` | 6 |
| Probe scripts for mode investigation | 13 |
| Versions of `test_cat.py` | 7 |
| Forums/resources consulted | 8 |
