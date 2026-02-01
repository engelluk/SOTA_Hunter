# SOTA Hunter

A Chrome extension that adds **Tune** buttons to [SOTAwatch](https://sotawatch.sota.org.uk/) spots and tunes your Yaesu FT-DX10 (or any HRD-supported radio) via [HRD Rig Control](https://ham-radio-deluxe.com/).

## What It Does

- **Tune buttons** appear inline next to each spot's frequency on the SOTAwatch page. Click one to instantly set your radio's VFO frequency and mode.
- **Activator deduplication** filters the spot list to show only the most recent spot per activator callsign, reducing clutter. This is togglable with a checkbox above the spots table.
- **Automatic mode mapping** translates SOTAwatch mode labels to the correct radio mode:
  - `SSB` becomes `USB` (above 10 MHz) or `LSB` (below 10 MHz)
  - `CW` stays `CW`
  - `FM`, `AM` pass through unchanged
  - `DATA`, `FT8`, `FT4`, `JS8`, `PSK` become `USB-D`
- **Visual feedback** on each Tune button: blue (idle), orange (pending), green (success), red (error with tooltip).
- **Settings popup** lets you configure the HRD host/port and test the connection without leaving the browser.

## Architecture

```
SOTAwatch page          Chrome Extension           Native Host (Python)       HRD Rig Control
+--------------+       +------------------+       +--------------------+     +--------------+
| Spot rows    |  DOM  | content.js       |  msg  | bridge.py          | TCP | Port 7809    |
| + injected   |<----->| (inject buttons, |<----->| (auto-launched by  |---->| Set freq/mode|
|   Tune btns  |       |  dedup spots)    |       |  Chrome on demand) |     | on FT-DX10   |
+--------------+       | background.js    |       +--------------------+     +--------------+
                       | (native messaging)|
                       +------------------+
```

Chrome auto-launches the Python native host on demand when the extension sends a message. No manual process startup or open localhost ports required.

## Project Structure

```
SOTA_Hunter/
├── extension/                         # Chrome extension (Manifest V3)
│   ├── manifest.json                  # Extension manifest
│   ├── background.js                  # Service worker - native messaging hub
│   ├── content.js                     # Content script - DOM injection, dedup, tune buttons
│   ├── content.css                    # Styles for injected UI elements
│   ├── popup.html                     # Settings popup
│   ├── popup.js                       # Popup logic
│   └── icons/                         # Extension icons (16/48/128 px)
├── native-host/
│   ├── bridge.py                      # Native messaging host (stdin/stdout JSON bridge)
│   ├── bridge.bat                     # Launcher for bridge.py
│   ├── hrd_client.py                  # HRD Rig Control TCP protocol client
│   ├── com.sotahunter.bridge.json     # Native messaging host manifest
│   └── install.bat                    # One-time Windows registry setup
└── README.md
```

## Prerequisites

- **Windows** (the native messaging host uses the Windows registry)
- **Google Chrome**
- **Python 3.6+** installed and available on your system `PATH`
- **HRD Rig Control** (Ham Radio Deluxe) running and connected to your radio, with its TCP server listening on the default port 7809

## Setup

### 1. Register the native messaging host

Double-click `native-host\install.bat`. This writes a registry key under `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.sotahunter.bridge` that tells Chrome where to find the host manifest.

### 2. Load the extension in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder

Chrome will assign the extension an ID (a long string of lowercase letters shown on the extension card).

### 3. Link the extension ID to the native host

1. Copy the extension ID from `chrome://extensions/`
2. Open `native-host\com.sotahunter.bridge.json` in a text editor
3. Replace `EXTENSION_ID_HERE` with your actual extension ID:
   ```json
   "allowed_origins": [
     "chrome-extension://abcdefghijklmnopqrstuvwxyz123456/"
   ]
   ```
4. Verify that the `"path"` value points to the correct absolute path of `bridge.bat` on your system. The default is:
   ```
   C:\Users\X1\Documents\AI tests\SOTA_Hunter\native-host\bridge.bat
   ```
   Update it if your installation is in a different location.

### 4. Configure HRD connection (optional)

Click the SOTA Hunter icon in the Chrome toolbar to open the settings popup. The defaults (`127.0.0.1:7809`) work if HRD Rig Control is running locally with its default TCP port. Click **Test Connection** to verify.

## Usage

1. Make sure HRD Rig Control is running and connected to your radio
2. Open https://sotawatch.sota.org.uk/en/
3. Spots will show a blue **Tune** button next to each frequency
4. Click a Tune button to set your radio to that frequency and mode
5. Use the **Show unique activators only** checkbox above the spots table to toggle deduplication

## Troubleshooting

**Tune button turns red / shows an error:**
- Check that HRD Rig Control is running and its TCP server is enabled on port 7809
- Click the SOTA Hunter toolbar icon and use **Test Connection** to diagnose
- Check `native-host\bridge.log` for detailed error messages

**No Tune buttons appear:**
- Reload the SOTAwatch page
- Check `chrome://extensions/` for any errors on the SOTA Hunter extension card
- Open DevTools (F12) on the SOTAwatch page and look for `SOTA Hunter` messages in the console

**"Cannot connect to native host" error:**
- Verify you ran `install.bat`
- Verify the extension ID in `com.sotahunter.bridge.json` matches your installed extension
- Verify the `"path"` in the manifest points to `bridge.bat` and that Python is on your system `PATH`
- Try restarting Chrome after making changes to the native host manifest or registry

**Deduplication not working as expected:**
- The extension fetches spot data from the SOTA API every 60 seconds. Newly posted spots may take up to a minute to be reflected.
- Toggle the checkbox off and back on to force a re-process of the visible rows.
