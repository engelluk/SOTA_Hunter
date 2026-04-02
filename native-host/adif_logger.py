"""ADIF record builder and UDP sender for HRD Logbook integration.

Builds a standard ADIF record from QSO fields and sends it as a UDP
datagram to HRD Logbook's QSO Forwarding port (default 2333).
"""

import socket
import logging

logger = logging.getLogger("sotachaser.adif_logger")

# Band plan: (lower MHz, upper MHz, band label)
BAND_PLAN = [
    (0.1357, 0.1378, "2200m"),
    (0.472, 0.479, "630m"),
    (1.8, 2.0, "160m"),
    (3.5, 4.0, "80m"),
    (5.3515, 5.3665, "60m"),
    (7.0, 7.3, "40m"),
    (10.1, 10.15, "30m"),
    (14.0, 14.35, "20m"),
    (18.068, 18.168, "17m"),
    (21.0, 21.45, "15m"),
    (24.89, 24.99, "12m"),
    (28.0, 29.7, "10m"),
    (50.0, 54.0, "6m"),
    (144.0, 148.0, "2m"),
    (420.0, 450.0, "70cm"),
]


def freq_to_band(freq_mhz):
    """Convert a frequency in MHz to an ADIF band string.

    >>> freq_to_band(7.146)
    '40m'
    >>> freq_to_band(14.285)
    '20m'
    """
    try:
        freq = float(freq_mhz)
    except (ValueError, TypeError):
        return ""
    for low, high, band in BAND_PLAN:
        if low <= freq <= high:
            return band
    return ""


def default_rst(mode):
    """Return the default RST report for a given mode.

    SSB/FM/AM -> "59", CW -> "599", digital modes -> "+00"
    """
    if not mode:
        return "59"
    mode_upper = mode.upper()
    if mode_upper in ("CW", "CW-R"):
        return "599"
    if mode_upper in ("FT8", "FT4", "JS8", "PSK", "DATA", "RTTY", "JT65", "JT9"):
        return "+00"
    # SSB, FM, AM, USB, LSB, etc.
    return "59"


def _adif_field(tag, value):
    """Format a single ADIF field: <TAG:len>value"""
    val = str(value)
    return f"<{tag}:{len(val)}>{val}"


def build_adif_record(call, qso_date, time_on, freq, band, mode,
                      rst_sent, rst_rcvd, sota_ref="", comment="",
                      station_callsign="", my_gridsquare=""):
    """Build a complete ADIF record string with header.

    Returns a string ready to send as a UDP datagram.
    """
    parts = [
        "<adif_ver:5>3.1.1",
        "<programid:11>SOTA Chaser",
        "<EOH>",
        _adif_field("CALL", call),
        _adif_field("QSO_DATE", qso_date),
        _adif_field("TIME_ON", time_on),
        _adif_field("FREQ", freq),
        _adif_field("BAND", band),
        _adif_field("MODE", mode),
        _adif_field("RST_SENT", rst_sent),
        _adif_field("RST_RCVD", rst_rcvd),
    ]

    if sota_ref:
        parts.append(_adif_field("SOTA_REF", sota_ref))
        parts.append(_adif_field("SIG", "SOTA"))
        parts.append(_adif_field("SIG_INFO", sota_ref))

    if comment:
        parts.append(_adif_field("COMMENT", comment))

    if station_callsign:
        parts.append(_adif_field("STATION_CALLSIGN", station_callsign))

    if my_gridsquare:
        parts.append(_adif_field("MY_GRIDSQUARE", my_gridsquare))

    parts.append("<EOR>")

    return "\n".join(parts) + "\n"


def send_to_hrd(adif_record, host="127.0.0.1", port=2333):
    """Send an ADIF record to HRD Logbook via UDP.

    Returns (True, message) on success, (False, error) on failure.
    """
    try:
        data = adif_record.encode("utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(data, (host, int(port)))
        finally:
            sock.close()
        logger.info("Sent ADIF record to %s:%s (%d bytes)", host, port, len(data))
        return True, f"QSO logged via UDP to {host}:{port}"
    except Exception as e:
        logger.error("Failed to send ADIF: %s", e)
        return False, str(e)
