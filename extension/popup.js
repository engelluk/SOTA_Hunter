/**
 * SOTA Hunter - Popup Settings
 */

const hostInput = document.getElementById("hrd-host");
const portInput = document.getElementById("hrd-port");
const saveBtn = document.getElementById("save-btn");
const testBtn = document.getElementById("test-btn");
const statusDiv = document.getElementById("status");

// Load saved settings
chrome.storage.sync.get({ hrd_host: "127.0.0.1", hrd_port: 7809 }, (settings) => {
  hostInput.value = settings.hrd_host;
  portInput.value = settings.hrd_port;
});

// Save settings
saveBtn.addEventListener("click", () => {
  const host = hostInput.value.trim() || "127.0.0.1";
  const port = parseInt(portInput.value, 10) || 7809;

  chrome.storage.sync.set({ hrd_host: host, hrd_port: port }, () => {
    saveBtn.textContent = "Saved!";
    setTimeout(() => {
      saveBtn.textContent = "Save Settings";
    }, 1500);
  });
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
