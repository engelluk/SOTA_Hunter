/**
 * SOTA Chaser - Background Service Worker
 *
 * Bridges messages between the content script and the native messaging host.
 * Manages the native messaging port lifecycle with reconnection support.
 */

let nativePort = null;
let pendingRequests = new Map(); // requestId -> {resolve, tabId, originalRequestId, action}
let requestCounter = 0;

function completePendingRequest(requestId, response) {
  const pending = pendingRequests.get(requestId);
  if (!pending) {
    return;
  }

  pendingRequests.delete(requestId);

  if (pending.tabId !== null) {
    const responseType = pending.action === "log" ? "logResponse" : "tuneResponse";
    chrome.tabs.sendMessage(pending.tabId, {
      type: responseType,
      requestId: pending.originalRequestId,
      ...response,
    });
  } else {
    pending.resolve(response);
  }
}

/**
 * Connect to the native messaging host.
 */
function connectNativeHost() {
  if (nativePort) {
    return nativePort;
  }

  try {
    nativePort = chrome.runtime.connectNative("com.sotachaser.bridge");

    nativePort.onMessage.addListener((response) => {
      console.log("Native host response:", response);

      // Native messaging is FIFO, so resolve the oldest pending request.
      if (pendingRequests.size > 0) {
        const [requestId] = pendingRequests.entries().next().value;
        completePendingRequest(requestId, response);
      }
    });

    nativePort.onDisconnect.addListener(() => {
      const error = chrome.runtime.lastError?.message || "Native host disconnected";
      console.warn("Native host disconnected:", error);

      for (const requestId of Array.from(pendingRequests.keys())) {
        completePendingRequest(requestId, { success: false, error });
      }
      nativePort = null;
    });

    return nativePort;
  } catch (e) {
    console.error("Failed to connect to native host:", e);
    nativePort = null;
    return null;
  }
}

/**
 * Send a message to the native host and track the pending response.
 */
function sendToNativeHost(message, tabId, originalRequestId) {
  return new Promise((resolve) => {
    const port = connectNativeHost();
    if (!port) {
      resolve({
        success: false,
        error: "Cannot connect to native host. Is install.bat run?",
      });
      return;
    }

    const requestId = ++requestCounter;
    const action = message.action || "tune";
    pendingRequests.set(requestId, {
      resolve,
      tabId,
      originalRequestId,
      action,
    });

    // Fetch CAT serial settings and include them in the message.
    chrome.storage.sync.get({ cat_port: "COM7", cat_baud: 38400 }, (settings) => {
      const fullMessage = {
        ...message,
        cat_port: settings.cat_port,
        cat_baud: settings.cat_baud,
      };
      console.log("Sending to native host:", fullMessage);

      if (port !== nativePort) {
        return;
      }

      try {
        port.postMessage(fullMessage);
      } catch (e) {
        const error = e?.message || "Native host disconnected";
        console.warn("Failed to send to native host:", error);
        completePendingRequest(requestId, { success: false, error });
        if (port === nativePort) {
          nativePort = null;
        }
      }
    });
  });
}

/**
 * Handle messages from content scripts and popup.
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "tune") {
    // From content script: tune to a frequency.
    const tabId = sender.tab?.id ?? null;
    sendToNativeHost(
      { action: "tune", frequency: message.frequency, mode: message.mode },
      tabId,
      message.requestId
    );
    // Response will be sent asynchronously via chrome.tabs.sendMessage.
    return false;
  }

  if (message.type === "log") {
    // From content script: log a QSO to HRD Logbook via UDP ADIF.
    const tabId = sender.tab?.id ?? null;
    chrome.storage.sync.get(
      { my_callsign: "", my_gridsquare: "", log_port: 2333 },
      (settings) => {
        sendToNativeHost(
          {
            action: "log",
            call: message.call,
            frequency: message.frequency,
            mode: message.mode,
            sota_ref: message.sota_ref,
            comment: message.comment,
            rst_sent: message.rst_sent,
            rst_rcvd: message.rst_rcvd,
            my_callsign: settings.my_callsign,
            my_gridsquare: settings.my_gridsquare,
            log_port: settings.log_port,
          },
          tabId,
          message.requestId
        );
      }
    );
    return false;
  }

  if (message.type === "testConnection") {
    // From popup: test the native host and CAT connection.
    sendToNativeHost({ action: "test" }, null, null).then((response) => {
      sendResponse(response);
    });
    return true; // Keep the message channel open for async response.
  }

  return false;
});

/**
 * Release the native host connection (and thereby the serial COM port) when
 * no SOTAwatch tabs remain open. The native host process receives EOF on
 * stdin, exits cleanly, and closes the serial port on the way out.
 */
async function releasePortIfUnused() {
  if (!nativePort) return;
  if (pendingRequests.size > 0) return; // Do not interrupt an in-flight request.
  const tabs = await chrome.tabs.query({ url: "*://sotawatch.sota.org.uk/*" });
  if (tabs.length === 0) {
    nativePort.disconnect(); // Triggers onDisconnect and clears nativePort.
  }
}

// Free the COM port when the last SOTAwatch tab is closed.
chrome.tabs.onRemoved.addListener(() => releasePortIfUnused());

// Free the COM port when the user navigates away from SOTAwatch in all open tabs.
chrome.tabs.onUpdated.addListener((_tabId, changeInfo) => {
  if (changeInfo.url) releasePortIfUnused();
});
