"""
Configuration and version information for SOTA Chaser
"""

# Application version (Semantic Versioning: MAJOR.MINOR.PATCH)
VERSION = "1.0.0"
APP_NAME = "SOTA Chaser"
APP_TITLE = f"{APP_NAME} v{VERSION}"

# Native messaging host identifier
NATIVE_HOST_NAME = "com.sotachaser.bridge"

# HRD Rig Control defaults
DEFAULT_HRD_HOST = "127.0.0.1"
DEFAULT_HRD_PORT = 7809

# SOTAwatch API
SOTA_API_BASE = "https://api2.sota.org.uk/api"
SOTA_SPOTS_URL = f"{SOTA_API_BASE}/spots/30/all"

# SOTAwatch page
SOTAWATCH_URL = "https://sotawatch.sota.org.uk"
