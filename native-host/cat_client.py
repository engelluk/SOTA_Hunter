"""Direct Yaesu CAT serial client for the FT-DX10."""

import serial
import logging
import time

logger = logging.getLogger("sotachaser.cat")

DEFAULT_PORT = "COM7"
DEFAULT_BAUD = 38400
TIMEOUT = 2

# Yaesu FT-DX10 MD0 mode codes
_MODE_TO_CAT = {
    "LSB":      "1",
    "USB":      "2",
    "CW":       "3",
    "FM":       "4",
    "AM":       "5",
    "RTTY-LSB": "6",
    "CW-L":     "7",
    "DATA-L":   "8",
    "RTTY-USB": "9",
    "DATA-FM":  "A",
    "FM-N":     "B",
    "DATA-U":   "C",
    "AM-N":     "D",
}

_CAT_TO_MODE = {v: k for k, v in _MODE_TO_CAT.items()}


class CATClient:
    """Controls a Yaesu FT-DX10 via direct serial CAT commands.

    The FT-DX10 uses Yaesu's CAT protocol over a USB serial connection
    (Silicon Labs CP2105 Enhanced COM Port). Commands are ASCII strings
    terminated with a semicolon. Set commands have no response; query
    commands return the current value terminated with a semicolon.
    """

    def __init__(self, port=DEFAULT_PORT, baud=DEFAULT_BAUD):
        self.port = port
        self.baud = baud
        self._ser = None

    def _ensure_open(self):
        """Open the serial port if not already open."""
        if self._ser is None or not self._ser.is_open:
            self._ser = serial.Serial(self.port, self.baud, timeout=TIMEOUT)
            time.sleep(0.1)
            logger.info("Opened %s at %d baud", self.port, self.baud)

    def _set(self, cmd):
        """Send a CAT set command. Set commands have no response on the FT-DX10."""
        self._ensure_open()
        self._ser.reset_input_buffer()
        self._ser.write(cmd.encode("ascii"))
        logger.debug("CAT> %s", cmd)
        time.sleep(0.05)  # Let the radio process before the next command

    def _query(self, cmd):
        """Send a CAT query command and return the response."""
        self._ensure_open()
        self._ser.reset_input_buffer()
        self._ser.write(cmd.encode("ascii"))
        logger.debug("CAT> %s", cmd)
        resp = self._ser.read_until(b";").decode("ascii", errors="replace")
        if resp:
            logger.debug("CAT< %s", resp)
        return resp

    def close(self):
        """Close the serial port."""
        if self._ser and self._ser.is_open:
            self._ser.close()
            self._ser = None
            logger.info("Closed serial port")

    # ── Radio commands ───────────────────────────────────────────────

    def set_frequency(self, freq_hz):
        """Set VFO-A frequency in Hz."""
        cmd = f"FA{int(freq_hz):09d};"
        self._set(cmd)
        logger.info("Set frequency to %d Hz", freq_hz)

    def set_mode(self, mode):
        """Set operating mode by name (USB, LSB, CW, FM, AM, DATA-U, etc.)."""
        cat_code = _MODE_TO_CAT.get(mode.upper())
        if cat_code is None:
            raise ValueError(f"Unknown mode: {mode}")
        cmd = f"MD0{cat_code};"
        self._set(cmd)
        logger.info("Set mode to %s (MD0%s)", mode, cat_code)

    def get_frequency(self):
        """Read VFO-A frequency in Hz as a string."""
        resp = self._query("FA;")
        # Response: FA014285000;
        if resp.startswith("FA") and resp.endswith(";"):
            return str(int(resp[2:-1]))
        return resp

    def get_mode(self):
        """Read current operating mode as a string."""
        resp = self._query("MD0;")
        # Response: MD02;
        if resp.startswith("MD0") and resp.endswith(";"):
            code = resp[3:-1]
            return _CAT_TO_MODE.get(code, f"UNKNOWN({code})")
        return resp

    # ── High-level API ───────────────────────────────────────────────

    def tune(self, freq_mhz, mode):
        """Set frequency and mode from SOTAwatch spot data.

        Args:
            freq_mhz: Frequency in MHz as a string (e.g., "14.285")
            mode: Mode as reported by SOTAwatch (e.g., "SSB", "CW", "FM")

        Returns:
            dict with success status and details
        """
        try:
            freq_hz = int(float(freq_mhz) * 1_000_000)
        except (ValueError, TypeError) as e:
            return {"success": False, "error": f"Invalid frequency: {freq_mhz} ({e})"}

        cat_mode = self._map_mode(mode, freq_hz)

        try:
            # Set mode BEFORE frequency to minimise VFO drift on band changes.
            # Then set frequency (which may trigger a band recall that overrides
            # the mode), then set mode AGAIN to correct whatever the band recall
            # may have restored.
            self.set_mode(cat_mode)
            self.set_frequency(freq_hz)
            self.set_mode(cat_mode)  # Correct mode after band recall

            # Verify
            actual_freq = self.get_frequency()
            actual_mode = self.get_mode()

            return {
                "success": True,
                "frequency": freq_mhz,
                "mode": cat_mode,
                "freq_hz": freq_hz,
                "actual_mode": actual_mode,
            }
        except (serial.SerialException, OSError, ValueError) as e:
            return {"success": False, "error": str(e)}

    def test_connection(self):
        """Test that the radio is reachable and return current freq/mode."""
        try:
            freq = self.get_frequency()
            mode = self.get_mode()
            return {
                "success": True,
                "message": f"Connected to FT-DX10 on {self.port}",
                "frequency": freq,
                "mode": mode,
            }
        except (serial.SerialException, OSError) as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _map_mode(sota_mode, freq_hz):
        """Map SOTAwatch mode strings to FT-DX10 mode names.

        Args:
            sota_mode: Mode from SOTAwatch (SSB, CW, FM, AM, DATA, etc.)
            freq_hz: Frequency in Hz, used for SSB sideband selection
        """
        sota_mode = (sota_mode or "SSB").upper().strip()

        if sota_mode == "SSB":
            return "USB" if freq_hz > 7_300_000 else "LSB"
        if sota_mode in ("CW", "CW-R"):
            return "CW"
        if sota_mode == "FM":
            return "FM"
        if sota_mode == "AM":
            return "AM"
        if sota_mode in ("DATA", "DATA-FT8", "FT8", "FT4", "JS8", "PSK"):
            return "DATA-U"
        # Unrecognized mode: default to USB/LSB based on band plan
        return "USB" if freq_hz > 7_300_000 else "LSB"
