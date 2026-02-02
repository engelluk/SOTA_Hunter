/**
 * SOTA Hunter - Popup Settings
 */

const portInput = document.getElementById("cat-port");
const baudInput = document.getElementById("cat-baud");
const saveBtn = document.getElementById("save-btn");
const testBtn = document.getElementById("test-btn");
const statusDiv = document.getElementById("status");

// Load saved settings
chrome.storage.sync.get({ cat_port: "COM7", cat_baud: 38400 }, (settings) => {
  portInput.value = settings.cat_port;
  baudInput.value = settings.cat_baud;
});

// Save settings
saveBtn.addEventListener("click", () => {
  const port = portInput.value.trim() || "COM7";
  const baud = parseInt(baudInput.value, 10) || 38400;

  chrome.storage.sync.set({ cat_port: port, cat_baud: baud }, () => {
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
