"""HRD Rig Control TCP protocol client for Yaesu FT-DX10."""

import socket
import struct
import logging
import time

logger = logging.getLogger("sotachaser.hrd")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7809
TIMEOUT = 5

# HRD v6 binary protocol signature
_SIGNATURE = bytes([0xCD, 0xAB, 0x34, 0x12, 0x34, 0x12, 0xCD, 0xAB])


class HRDClient:
    """Communicates with HRD Rig Control via its binary TCP protocol.

    HRD v6 message framing:
      4 bytes  - little-endian body length
      8 bytes  - signature  (cd ab 34 12 34 12 cd ab)
      4 bytes  - zeros
      N bytes  - UTF-16LE payload (the command or response text)
      6 bytes  - zeros

    Body length = 8 (sig) + 4 (zeros) + N (payload) + 6 (zeros)

    HRD only processes one command per TCP connection, so each command
    opens a fresh socket, sends the command, reads the reply, and closes.

    Most commands require a context prefix obtained via 'Get Context'.
    Example: '[240] Set Frequency-Hz 14285000'
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self._context = None
        self._mode_list = None

    # ── Wire protocol ────────────────────────────────────────────────

    def _one_shot(self, text):
        """Open a connection, send one command, read the reply, close.

        HRD processes exactly one command per TCP connection.
        Uses SO_LINGER to send RST on close, preventing CLOSE_WAIT
        buildup on the HRD side.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
        )
        try:
            sock.connect((self.host, self.port))

            # Send
            payload = text.encode("utf-16-le")
            body = _SIGNATURE + b"\x00" * 4 + payload + b"\x00" * 6
            sock.sendall(struct.pack("<I", len(body)) + body)
            logger.debug("Sent: %s", text)

            # Receive: length field includes its own 4 bytes
            raw_len = _recv_exact(sock, 4)
            msg_len = struct.unpack("<I", raw_len)[0]
            remaining = msg_len - 4
            body = _recv_exact(sock, remaining)
            # body layout: sig(8) + zeros(4) + payload(N) + trailing_zeros(6)
            resp = body[12 : remaining - 6].decode("utf-16-le").rstrip("\0")
            logger.debug("Recv: %s", resp)
            return resp
        finally:
            sock.close()

    def _get_context(self):
        """Get the radio context number from HRD (cached)."""
        if self._context is None:
            self._context = self._one_shot("Get Context")
            logger.info("HRD context: %s", self._context)
        return self._context

    def _radio_command(self, text):
        """Send a context-prefixed command, using the cached context."""
        ctx = self._get_context()
        return self._one_shot(f"[{ctx}] {text}")

    # ── Radio commands ───────────────────────────────────────────────

    def _get_mode_list(self):
        """Query HRD for the list of available modes (cached).

        Returns a list like ['LSB', 'USB', 'CW', 'FM', ...] or None.
        Uses the {Mode} dropdown (curly braces required for Get).
        """
        if self._mode_list is None:
            raw = self._radio_command("Get Dropdown-list {Mode}")
            if raw:
                self._mode_list = raw.split(",")
                logger.info("HRD mode list: %s", self._mode_list)
            else:
                logger.warning("Could not get mode list from HRD")
        return self._mode_list

    def set_frequency(self, freq_hz):
        """Set the VFO frequency in Hz."""
        response = self._radio_command(f"Set Frequency-Hz {int(freq_hz)}")
        logger.info("Set frequency to %d Hz: %s", freq_hz, response)
        return response

    def set_mode(self, mode):
        """Set the operating mode.

        NOTE: Mode setting via HRD's TCP protocol is currently broken
        for the FT-DX10.  Both 'Set Dropdown Mode {index}' and
        'Set Mode {name}' force the radio to LSB regardless of the
        requested mode.  Mode setting is therefore disabled to avoid
        overriding the operator's manual mode selection.
        """
        logger.info("Mode setting skipped (requested %s) - "
                     "HRD TCP mode commands not functional for FT-DX10", mode)
        return mode

    def get_frequency(self):
        """Read the current VFO frequency."""
        return self._radio_command("Get Frequency")

    def get_mode(self):
        """Read the current operating mode."""
        return self._radio_command("Get Mode")

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

        hrd_mode = self._map_mode(mode, freq_hz)

        try:
            self.set_frequency(freq_hz)
            self.set_mode(hrd_mode)
            return {
                "success": True,
                "frequency": freq_mhz,
                "mode": hrd_mode,
                "freq_hz": freq_hz,
            }
        except (ConnectionError, OSError, socket.timeout) as e:
            return {"success": False, "error": str(e)}

    def test_connection(self):
        """Test that HRD is reachable and return current freq/mode."""
        try:
            freq = self.get_frequency()
            mode = self.get_mode()
            return {
                "success": True,
                "message": "Connected to HRD",
                "frequency": freq,
                "mode": mode,
            }
        except (ConnectionError, OSError, socket.timeout) as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _map_mode(sota_mode, freq_hz):
        """Map SOTAwatch mode strings to FT-DX10 HRD mode strings.

        Uses the mode names as reported by HRD's dropdown list for
        the FT-DX10: LSB, USB, CW, FM, AM, RTTY-LSB, CW-L, DATA-L,
        RTTY-USB, DATA-FM, FM-N, DATA-U, AM-N, PSK, DATA-FM-N.

        Args:
            sota_mode: Mode from SOTAwatch (SSB, CW, FM, AM, DATA, etc.)
            freq_hz: Frequency in Hz, used for SSB sideband selection
        """
        sota_mode = (sota_mode or "SSB").upper().strip()

        if sota_mode == "SSB":
            return "USB" if freq_hz >= 10_000_000 else "LSB"
        if sota_mode in ("CW", "CW-R"):
            return "CW"
        if sota_mode == "FM":
            return "FM"
        if sota_mode == "AM":
            return "AM"
        if sota_mode in ("DATA", "DATA-FT8", "FT8", "FT4", "JS8", "PSK"):
            return "DATA-U"
        # For anything unrecognized, pass through as-is
        return sota_mode


def _recv_exact(sock, n):
    """Read exactly n bytes from a socket."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("HRD connection closed unexpectedly")
        buf.extend(chunk)
    return bytes(buf)
