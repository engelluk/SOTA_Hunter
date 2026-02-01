"""HRD Rig Control TCP protocol client for Yaesu FT-DX10."""

import socket
import struct
import logging

logger = logging.getLogger("sotahunter.hrd")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7809
TIMEOUT = 5


class HRDClient:
    """Communicates with HRD Rig Control via its TCP protocol.

    Protocol details:
    - Messages are UTF-16LE encoded strings
    - Each message is prefixed with a 4-byte little-endian length (in bytes)
    - The length includes the null terminator (2 bytes for UTF-16LE)
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Connect to HRD and perform initial handshake."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.sock.connect((self.host, self.port))

        # Send initial context string
        self._send("SOTA Hunter")

        # Read the handshake response (radio info)
        response = self._recv()
        logger.info("HRD handshake response: %s", response)
        return response

    def disconnect(self):
        """Close the connection."""
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def _send(self, message):
        """Send a UTF-16LE message with 4-byte LE length prefix."""
        encoded = (message + "\0").encode("utf-16-le")
        length = len(encoded)
        header = struct.pack("<I", length)
        self.sock.sendall(header + encoded)
        logger.debug("Sent: %s (%d bytes)", message, length)

    def _recv(self):
        """Receive a UTF-16LE message with 4-byte LE length prefix."""
        header = self._recv_exact(4)
        length = struct.unpack("<I", header)[0]
        data = self._recv_exact(length)
        message = data.decode("utf-16-le").rstrip("\0")
        logger.debug("Recv: %s", message)
        return message

    def _recv_exact(self, n):
        """Read exactly n bytes from the socket."""
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("HRD connection closed unexpectedly")
            buf.extend(chunk)
        return bytes(buf)

    def set_frequency(self, freq_hz):
        """Set the VFO frequency in Hz.

        Args:
            freq_hz: Frequency in Hz as an integer (e.g., 14285000)
        """
        cmd = f"Set Frequency-Hz {int(freq_hz)}"
        self._send(cmd)
        response = self._recv()
        logger.info("Set frequency to %d Hz: %s", freq_hz, response)
        return response

    def set_mode(self, mode):
        """Set the operating mode.

        Args:
            mode: Mode string as expected by HRD (e.g., "USB", "LSB", "CW", "FM")
        """
        cmd = f"Set Mode {mode}"
        self._send(cmd)
        response = self._recv()
        logger.info("Set mode to %s: %s", mode, response)
        return response

    def get_frequency(self):
        """Read the current VFO frequency."""
        self._send("Get Frequency")
        return self._recv()

    def get_mode(self):
        """Read the current operating mode."""
        self._send("Get Mode")
        return self._recv()

    def tune(self, freq_mhz, mode):
        """High-level tune: set frequency and mode from SOTAwatch spot data.

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
            self.connect()
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
        finally:
            self.disconnect()

    @staticmethod
    def _map_mode(sota_mode, freq_hz):
        """Map SOTAwatch mode strings to HRD mode strings.

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
            return "USB-D"
        # For anything unrecognized, pass through as-is
        return sota_mode
