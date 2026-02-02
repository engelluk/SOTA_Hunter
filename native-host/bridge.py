#!/usr/bin/env python3
"""Chrome Native Messaging host for SOTA Hunter.

Reads JSON messages from stdin (4-byte LE length prefix + JSON),
forwards tune requests to the radio via direct serial CAT, and
returns responses via stdout using the same framing.
"""

import json
import struct
import sys
import logging
import os

# Configure logging to a file next to the script
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bridge.log")
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("sotahunter.bridge")

# Windows requires binary mode for stdin/stdout
if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

from cat_client import CATClient

# Keep a single serial connection open across requests
_client = None


def _get_client(request):
    """Get or create a CATClient with the configured serial port."""
    global _client
    port = request.get("cat_port", "COM7")
    baud = request.get("cat_baud", 38400)
    try:
        baud = int(baud)
    except (ValueError, TypeError):
        baud = 38400

    if _client is not None:
        if _client.port == port and _client.baud == baud:
            return _client
        # Settings changed, close old connection
        _client.close()

    _client = CATClient(port=port, baud=baud)
    return _client


def read_message():
    """Read a single native messaging message from stdin."""
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length or len(raw_length) < 4:
        return None
    length = struct.unpack("<I", raw_length)[0]
    data = sys.stdin.buffer.read(length)
    if len(data) < length:
        return None
    message = json.loads(data.decode("utf-8"))
    logger.debug("Received message: %s", message)
    return message


def send_message(message):
    """Send a single native messaging message to stdout."""
    encoded = json.dumps(message).encode("utf-8")
    header = struct.pack("<I", len(encoded))
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()
    logger.debug("Sent message: %s", message)


def handle_tune(request):
    """Handle a tune request via direct CAT."""
    frequency = request.get("frequency")
    mode = request.get("mode", "SSB")

    if not frequency:
        return {"success": False, "error": "No frequency specified"}

    client = _get_client(request)
    return client.tune(frequency, mode)


def handle_test(request):
    """Handle a connection test request."""
    client = _get_client(request)
    return client.test_connection()


def main():
    logger.info("SOTA Hunter bridge started")
    while True:
        message = read_message()
        if message is None:
            logger.info("No more messages, exiting")
            break

        action = message.get("action", "")
        try:
            if action == "tune":
                response = handle_tune(message)
            elif action == "test":
                response = handle_test(message)
            else:
                response = {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception("Error handling message")
            response = {"success": False, "error": str(e)}

        send_message(response)

    # Clean up serial port
    if _client:
        _client.close()
    logger.info("SOTA Hunter bridge exiting")


if __name__ == "__main__":
    main()
