/**
 * SOTA Hunter - Popup Settings
 */

const modelSelect = document.getElementById("cat-model");
const portInput = document.getElementById("cat-port");
const baudInput = document.getElementById("cat-baud");
const callsignInput = document.getElementById("my-callsign");
const gridsquareInput = document.getElementById("my-gridsquare");
const logPortInput = document.getElementById("log-port");
const saveBtn = document.getElementById("save-btn");
const testBtn = document.getElementById("test-btn");
const statusDiv = document.getElementById("status");

const BAUD_DEFAULTS = {
  "FT-DX10":   38400,
  "FTX-1":     38400,
  "FT-710":    38400,
  "FTDX101MP": 38400,
  "FT-991A":   4800,
  "FT-891":    9600,
  "FTDX3000":  4800,
  "FTDX1200":  4800,
};

// Auto-fill baud rate when radio model changes
modelSelect.addEventListener("change", () => {
  const baud = BAUD_DEFAULTS[modelSelect.value];
  if (baud) baudInput.value = baud;
});

// Load saved settings
chrome.storage.sync.get(
  { cat_model: "FT-DX10", cat_port: "COM7", cat_baud: 38400, my_callsign: "", my_gridsquare: "", log_port: 2333 },
  (settings) => {
    modelSelect.value = settings.cat_model;
    portInput.value = settings.cat_port;
    baudInput.value = settings.cat_baud;
    callsignInput.value = settings.my_callsign;
    gridsquareInput.value = settings.my_gridsquare;
    logPortInput.value = settings.log_port;
  }
);

// Save settings
saveBtn.addEventListener("click", () => {
  const model = modelSelect.value;
  const port = portInput.value.trim() || "COM7";
  const baud = parseInt(baudInput.value, 10) || 38400;
  const myCallsign = callsignInput.value.trim().toUpperCase();
  const myGridsquare = gridsquareInput.value.trim();
  const logPort = parseInt(logPortInput.value, 10) || 2333;

  chrome.storage.sync.set(
    { cat_model: model, cat_port: port, cat_baud: baud, my_callsign: myCallsign, my_gridsquare: myGridsquare, log_port: logPort },
    () => {
      saveBtn.textContent = "Saved!";
      setTimeout(() => {
        saveBtn.textContent = "Save Settings";
      }, 1500);
    }
  );
});

// Test connection
testBtn.addEventListener("click", () => {
  testBtn.disabled = true;
  testBtn.textContent = "Testing...";
  statusDiv.className = "status";
  statusDiv.style.display = "none";

  chrome.runtime.sendMessage({ type: "testConnection" }, (response) => {
    testBtn.disabled = false;
    testBtn.textContent = "Test Connection";

    if (chrome.runtime.lastError) {
      showStatus(false, chrome.runtime.lastError.message);
      return;
    }

    if (response && response.success) {
      showStatus(
        true,
        `Connected - Freq: ${response.frequency || "?"}, Mode: ${response.mode || "?"}`
      );
    } else {
      showStatus(false, response?.error || "Connection failed");
    }
  });
});

function showStatus(connected, message) {
  statusDiv.className = "status " + (connected ? "connected" : "disconnected");
  statusDiv.innerHTML = `<span class="status-indicator"></span>${message}`;
  statusDiv.style.display = "block";
}
