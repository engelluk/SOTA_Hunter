"""Comprehensive test of CATClient - mode mapping, band plan, frequency accuracy."""

import logging
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

from cat_client import CATClient

client = CATClient(port="COM7", baud=38400)

print("=== Connection test ===")
r = client.test_connection()
print(f"  {r}")
assert r["success"], f"Connection failed: {r}"

failures = []


def test_tune(label, freq_mhz, sota_mode, expect_mode, expect_freq_hz):
    r = client.tune(freq_mhz, sota_mode)
    freq_ok = r.get("actual_mode") == expect_mode
    # Allow small frequency tolerance (radio may round to nearest step)
    actual_hz = int(client.get_frequency())
    freq_diff = abs(actual_hz - expect_freq_hz)
    freq_exact = freq_diff <= 10  # 10 Hz tolerance

    status = "PASS" if (freq_ok and freq_exact) else "FAIL"
    print(f"  [{status}] {label}: {freq_mhz} MHz {sota_mode}")
    print(f"         mode: expect={expect_mode} actual={r.get('actual_mode')}")
    print(f"         freq: expect={expect_freq_hz} actual={actual_hz} (diff={freq_diff})")

    if not freq_ok or not freq_exact:
        failures.append(f"{label}: mode={'OK' if freq_ok else 'FAIL'} freq={'OK' if freq_exact else f'FAIL (off by {freq_diff} Hz)'}")


# ── SSB band plan: LSB <= 7.3 MHz, USB > 7.3 MHz ────────────────
print("\n=== SSB band plan (LSB/USB boundary at 7.3 MHz) ===")
test_tune("160m SSB", "1.950", "SSB", "LSB", 1_950_000)
test_tune("80m SSB",  "3.750", "SSB", "LSB", 3_750_000)
test_tune("40m SSB",  "7.090", "SSB", "LSB", 7_090_000)
test_tune("30m SSB",  "10.130", "SSB", "USB", 10_130_000)
test_tune("20m SSB",  "14.285", "SSB", "USB", 14_285_000)
test_tune("17m SSB",  "18.130", "SSB", "USB", 18_130_000)
test_tune("15m SSB",  "21.300", "SSB", "USB", 21_300_000)
test_tune("12m SSB",  "24.950", "SSB", "USB", 24_950_000)
test_tune("10m SSB",  "28.500", "SSB", "USB", 28_500_000)

# ── CW mode (always CW regardless of band) ──────────────────────
print("\n=== CW mode ===")
test_tune("40m CW",  "7.032", "CW", "CW", 7_032_000)
test_tune("20m CW",  "14.062", "CW", "CW", 14_062_000)
test_tune("30m CW",  "10.118", "CW", "CW", 10_118_000)
test_tune("CW-R",    "7.030", "CW-R", "CW", 7_030_000)

# ── FM / AM ──────────────────────────────────────────────────────
print("\n=== FM and AM ===")
test_tune("10m FM",  "29.600", "FM", "FM", 29_600_000)
test_tune("10m AM",  "28.400", "AM", "AM", 28_400_000)

# ── Digital modes → DATA-U ───────────────────────────────────────
print("\n=== Digital modes ===")
test_tune("20m FT8",  "14.074", "FT8", "DATA-U", 14_074_000)
test_tune("40m FT4",  "7.0475", "FT4", "DATA-U", 7_047_500)
test_tune("20m DATA", "14.070", "DATA", "DATA-U", 14_070_000)
test_tune("20m JS8",  "14.078", "JS8", "DATA-U", 14_078_000)
test_tune("20m PSK",  "14.070", "PSK", "DATA-U", 14_070_000)
test_tune("DATA-FT8", "7.074",  "DATA-FT8", "DATA-U", 7_074_000)

# ── Unrecognized modes → fall back to USB/LSB by band plan ──────
print("\n=== Unrecognized modes (should default to USB/LSB) ===")
test_tune("Unknown 40m",  "7.100", "Other", "LSB", 7_100_000)
test_tune("Unknown 20m",  "14.200", "SomeMode", "USB", 14_200_000)
test_tune("C4FM 10m",     "29.250", "C4FM", "USB", 29_250_000)
test_tune("DMR",          "7.050", "DMR", "LSB", 7_050_000)

# ── Band-crossing: verify freq doesn't shift when mode changes ──
print("\n=== Band crossing (freq accuracy after mode change) ===")
# Start on 20m USB, then jump to 40m LSB
client.tune("14.285", "SSB")  # set to USB first
test_tune("20m->40m", "7.090", "SSB", "LSB", 7_090_000)

# Now from 40m LSB to 20m USB
test_tune("40m->20m", "14.285", "SSB", "USB", 14_285_000)

# 20m USB to 80m LSB (big jump)
test_tune("20m->80m", "3.690", "SSB", "LSB", 3_690_000)

# 80m LSB to 15m USB
test_tune("80m->15m", "21.285", "SSB", "USB", 21_285_000)

# ── Restore ──────────────────────────────────────────────────────
client.tune("14.285", "SSB")

client.close()

# ── Summary ──────────────────────────────────────────────────────
print("\n" + "=" * 50)
if failures:
    print(f"FAILURES ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
else:
    print("ALL TESTS PASSED")
print("=" * 50)
