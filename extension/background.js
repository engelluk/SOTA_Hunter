/**
 * SOTA Hunter - Background Service Worker
 *
 * Bridges messages between the content script and the native messaging host.
 * Manages the native messaging port lifecycle with reconnection support.
 */

let nativePort = null;
let pendingRequests = new Map(); // requestId -> {resolve, reject, tabId}
let requestCounter = 0;

/**
 * Connect to the native messaging host.
 */
function connectNativeHost() {
  if (nativePort) {
    return nativePort;
  }

  try {
    nativePort = chrome.runtime.connectNative("com.sotahunter.bridge");

    nativePort.onMessage.addListener((response) => {
      console.log("Native host response:", response);

      // Route response back to the appropriate requester
      // Since native messaging is sequential, resolve the oldest pending request
      if (pendingRequests.size > 0) {
        const [requestId, pending] = pendingRequests.entries().next().value;
        pendingRequests.delete(requestId);

        if (pending.tabId !== null) {
          // Response to a content script request — route by action type
          const responseType = pending.action === "log" ? "logResponse" : "tuneResponse";
          chrome.tabs.sendMessage(pending.tabId, {
            type: responseType,
            requestId: pending.originalRequestId,
            ...response,
          });
        } else {
          // Response to a popup test request
          pending.resolve(response);
        }
      }
    });

    nativePort.onDisconnect.addListener(() => {
      const error = chrome.runtime.lastError?.message || "Native host disconnected";
      console.warn("Native host disconnected:", error);

      // Reject all pending requests
      for (const [requestId, pending] of pendingRequests) {
        const errorResponse = { success: false, error };
        if (pending.tabId !== null) {
          const responseType = pending.action === "log" ? "logResponse" : "tuneResponse";
          chrome.tabs.sendMessage(pending.tabId, {
            type: responseType,
            requestId: pending.originalRequestId,
            ...errorResponse,
          });
        } else {
          pending.resolve(errorResponse);
        }
      }
      pendingRequests.clear();
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
      const errorResponse = {
        success: false,
        error: "Cannot connect to native host. Is install.bat run?",
      };
      resolve(errorResponse);
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

    // Fetch CAT serial settings and include them in the message
    chrome.storage.sync.get({ cat_port: "COM7", cat_baud: 38400 }, (settings) => {
      const fullMessage = {
        ...message,
        cat_port: settings.cat_port,
        cat_baud: settings.cat_baud,
      };
      console.log("Sending to native host:", fullMessage);
      port.postMessage(fullMessage);
    });
  });
}

/**
 * Handle messages from content scripts and popup.
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "tune") {
    // From content script: tune to a frequency
    const tabId = sender.tab?.id ?? null;
    sendToNativeHost(
      { action: "tune", frequency: message.frequency, mode: message.mode },
      tabId,
      message.requestId
    );
    // Response will be sent asynchronously via chrome.tabs.sendMessage
    return false;
  }

  if (message.type === "log") {
    // From content script: log a QSO to HRD Logbook via UDP ADIF
    const tabId = sender.tab?.id ?? null;
    // Fetch logging settings and include them in the native host message
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
    // From popup: test the HRD connection
    sendToNativeHost({ action: "test" }, null, null).then((response) => {
      sendResponse(response);
    });
    return true; // Keep the message channel open for async response
  }

  return false;
});
