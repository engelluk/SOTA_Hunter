#!/usr/bin/env python3
"""Chrome Native Messaging host for SOTA Hunter.

Reads JSON messages from stdin (4-byte LE length prefix + JSON),
forwards tune requests to HRD Rig Control, and returns responses
via stdout using the same framing.
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

from hrd_client import HRDClient


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
    """Handle a tune request by forwarding to HRD."""
    frequency = request.get("frequency")
    mode = request.get("mode", "SSB")
    host = request.get("hrd_host", "127.0.0.1")
    port = request.get("hrd_port", 7809)

    if not frequency:
        return {"success": False, "error": "No frequency specified"}

    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 7809

    client = HRDClient(host=host, port=port)
    result = client.tune(frequency, mode)
    return result


def handle_test(request):
    """Handle a connection test request."""
    host = request.get("hrd_host", "127.0.0.1")
    port = request.get("hrd_port", 7809)

    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 7809

    client = HRDClient(host=host, port=port)
    try:
        client.connect()
        freq = client.get_frequency()
        mode = client.get_mode()
        client.disconnect()
        return {
            "success": True,
            "message": "Connected to HRD",
            "frequency": freq,
            "mode": mode,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


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

    logger.info("SOTA Hunter bridge exiting")


if __name__ == "__main__":
    main()
