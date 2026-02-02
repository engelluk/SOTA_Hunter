/**
 * SOTA Hunter - Content Script for SOTAwatch
 *
 * Observes the SOTAwatch SPA DOM for spot rows, deduplicates activators
 * (showing only the latest spot per callsign), and injects "Tune" buttons
 * that control the radio via the native messaging bridge.
 */

(function () {
  "use strict";

  const SPOT_API_URL = "https://api2.sota.org.uk/api/spots/30/all";
  const POLL_INTERVAL = 60000; // Re-check spots every 60s
  const PROCESS_DEBOUNCE = 500; // Debounce DOM mutations

  let dedupEnabled = true;
  let spotsData = []; // Parsed from API
  let pendingCallbacks = new Map(); // requestId -> callback
  let requestCounter = 0;
  let processTimeout = null;

  // ── API Data Fetching ──────────────────────────────────────────────

  async function fetchSpots() {
    try {
      const response = await fetch(SPOT_API_URL);
      if (!response.ok) return;
      spotsData = await response.json();
    } catch (e) {
      console.warn("SOTA Hunter: Failed to fetch spots from API", e);
    }
  }

  /**
   * Build a lookup from activator callsign to their latest spot.
   */
  function getLatestSpotsByActivator() {
    const latest = new Map();
    // API returns newest first, so the first occurrence per callsign is the latest
    for (const spot of spotsData) {
      const key = spot.activatorCallsign?.toUpperCase();
      if (key && !latest.has(key)) {
        latest.set(key, spot);
      }
    }
    return latest;
  }

  // ── DOM Processing ─────────────────────────────────────────────────

  /**
   * Find spot rows in the DOM. SOTAwatch renders spots as table rows
   * in various table layouts. We look for <tr> elements inside the
   * main spots area.
   */
  function findSpotRows() {
    // SOTAwatch uses a table with spot data. Rows are <tr> elements
    // within the main content area. Each row typically has cells for:
    // time, callsign, frequency/mode, summit, etc.
    const rows = document.querySelectorAll("table tbody tr");
    return Array.from(rows);
  }

  /**
   * Extract spot info from a DOM table row.
   * Returns { callsign, frequency, mode, summitRef, element } or null.
   */
  function parseSpotRow(tr) {
    const cells = tr.querySelectorAll("td");
    if (cells.length < 3) return null;

    // SOTAwatch table columns vary but typically include these fields.
    // We search the cell text content to identify the frequency and callsign.
    let callsign = null;
    let frequency = null;
    let mode = null;
    let summitRef = null;

    const allText = tr.textContent;

    // Try to extract frequency: a number with decimal point like "14.285" or "7.032"
    const freqMatch = allText.match(/\b(\d{1,4}\.\d{1,6})\b/);
    if (freqMatch) {
      frequency = freqMatch[1];
    }

    // Try to find the frequency cell more precisely for button injection
    let freqCell = null;

    for (const cell of cells) {
      const text = cell.textContent.trim();

      // Summit ref pattern: letter(s)/letter(s)-NNN
      if (!summitRef && /^[A-Z\d]+\/[A-Z]{2}-\d{3}$/i.test(text)) {
        summitRef = text;
        continue;
      }

      // Frequency: digits with decimal
      if (!freqCell && /^\d{1,4}\.\d{1,6}$/.test(text)) {
        freqCell = cell;
        frequency = text;
        continue;
      }

      // Mode: short uppercase string
      if (
        !mode &&
        /^(SSB|CW|FM|AM|DATA|FT8|FT4|JS8|PSK|C4FM|DMR|USB|LSB|CW-R)$/i.test(text)
      ) {
        mode = text.toUpperCase();
        continue;
      }

      // Callsign: typical amateur radio callsign pattern
      // Look for cells containing a link (SOTAwatch wraps callsigns in links)
      const link = cell.querySelector("a");
      if (link) {
        const linkText = link.textContent.trim();
        if (/^[A-Z\d]{1,3}\d[A-Z\d]{1,4}(\/[A-Z\d]+)?$/i.test(linkText)) {
          if (!callsign) {
            callsign = linkText.toUpperCase();
          }
        }
      }

      // Callsign without link
      if (!callsign && /^[A-Z\d]{1,3}\d[A-Z\d]{1,4}(\/[A-Z\d]+)?$/i.test(text)) {
        callsign = text.toUpperCase();
      }
    }

    // Also check if frequency and mode are combined in one cell like "14.285 USB"
    if (!mode && freqCell) {
      const combined = freqCell.textContent.trim();
      const parts = combined.split(/\s+/);
      if (parts.length >= 2) {
        mode = parts[1].toUpperCase();
      }
    }

    // Fallback: try to match from the API data if we have a callsign
    if (callsign && (!frequency || !mode)) {
      const apiSpot = spotsData.find(
        (s) => s.activatorCallsign?.toUpperCase() === callsign
      );
      if (apiSpot) {
        if (!frequency) frequency = apiSpot.frequency;
        if (!mode) mode = apiSpot.mode;
      }
    }

    if (!frequency) return null;

    return {
      callsign: callsign || "UNKNOWN",
      frequency,
      mode: mode || "SSB",
      summitRef,
      element: tr,
      freqCell: freqCell || cells[0],
    };
  }

  /**
   * Main processing: parse rows, deduplicate, inject buttons.
   */
  function processSpots() {
    const rows = findSpotRows();
    if (rows.length === 0) return;

    const latestByActivator = getLatestSpotsByActivator();
    const seenActivators = new Set();

    for (const row of rows) {
      // Skip rows we've already fully processed (unless re-processing)
      const spot = parseSpotRow(row);
      if (!spot) continue;

      const activatorKey = spot.callsign.toUpperCase();

      // Deduplication
      if (dedupEnabled && seenActivators.has(activatorKey)) {
        row.classList.add("sota-hunter-duplicate");
        row.style.display = "none";
        continue;
      }

      seenActivators.add(activatorKey);
      row.classList.remove("sota-hunter-duplicate");
      row.style.display = "";

      // If we have API data, use the latest spot's frequency/mode
      if (latestByActivator.has(activatorKey)) {
        const latest = latestByActivator.get(activatorKey);
        spot.frequency = latest.frequency || spot.frequency;
        spot.mode = latest.mode || spot.mode;
      }

      // Inject tune button if not already present
      if (!row.querySelector(".sota-hunter-tune-btn")) {
        injectTuneButton(spot);
      }
    }
  }

  /**
   * Inject a Tune button into the spot row.
   */
  function injectTuneButton(spot) {
    const btn = document.createElement("button");
    btn.className = "sota-hunter-tune-btn";
    btn.title = `Tune to ${spot.frequency} MHz ${spot.mode}`;
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
    </svg> Tune`;

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      tuneToSpot(spot, btn);
    });

    // Insert the button into the frequency cell or the last cell
    spot.freqCell.appendChild(btn);
  }

  /**
   * Send a tune request to the background service worker.
   */
  function tuneToSpot(spot, btn) {
    const requestId = ++requestCounter;
    btn.classList.remove("sota-hunter-tune-success", "sota-hunter-tune-error");
    btn.classList.add("sota-hunter-tune-pending");

    pendingCallbacks.set(requestId, (response) => {
      btn.classList.remove("sota-hunter-tune-pending");
      if (response.success) {
        if (response.mode_warning) {
          // Frequency set OK but mode didn't change
          btn.classList.add("sota-hunter-tune-warning");
          btn.title = response.mode_warning;
          setTimeout(() => {
            btn.classList.remove("sota-hunter-tune-warning");
            btn.title = `Tune to ${spot.frequency} MHz ${spot.mode}`;
          }, 5000);
        } else {
          btn.classList.add("sota-hunter-tune-success");
          setTimeout(() => btn.classList.remove("sota-hunter-tune-success"), 3000);
        }
      } else {
        btn.classList.add("sota-hunter-tune-error");
        btn.title = `Error: ${response.error}`;
        setTimeout(() => {
          btn.classList.remove("sota-hunter-tune-error");
          btn.title = `Tune to ${spot.frequency} MHz ${spot.mode}`;
        }, 5000);
      }
    });

    chrome.runtime.sendMessage({
      type: "tune",
      requestId,
      frequency: spot.frequency,
      mode: spot.mode,
    });
  }

  // ── Message Handling ───────────────────────────────────────────────

  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === "tuneResponse" && message.requestId) {
      const callback = pendingCallbacks.get(message.requestId);
      if (callback) {
        pendingCallbacks.delete(message.requestId);
        callback(message);
      }
    }
  });

  // ── Filter Toggle UI ──────────────────────────────────────────────

  function injectFilterBar() {
    // Don't inject twice
    if (document.getElementById("sota-hunter-filter-bar")) return;

    // Find the spots container - look for the main content area
    const container =
      document.querySelector(".spots-table")?.parentElement ||
      document.querySelector("table")?.parentElement ||
      document.querySelector("main") ||
      document.querySelector("#app > div");

    if (!container) return;

    const bar = document.createElement("div");
    bar.id = "sota-hunter-filter-bar";
    bar.innerHTML = `
      <label class="sota-hunter-filter-label">
        <input type="checkbox" id="sota-hunter-dedup-toggle" ${dedupEnabled ? "checked" : ""} />
        Show unique activators only
      </label>
      <span class="sota-hunter-badge">SOTA Hunter</span>
    `;

    container.insertBefore(bar, container.firstChild);

    document.getElementById("sota-hunter-dedup-toggle").addEventListener("change", (e) => {
      dedupEnabled = e.target.checked;
      // Re-show all rows first, then re-process
      document.querySelectorAll(".sota-hunter-duplicate").forEach((row) => {
        row.classList.remove("sota-hunter-duplicate");
        row.style.display = "";
      });
      processSpots();
    });
  }

  // ── Initialization ─────────────────────────────────────────────────

  function debouncedProcess() {
    if (processTimeout) clearTimeout(processTimeout);
    processTimeout = setTimeout(() => {
      processSpots();
    }, PROCESS_DEBOUNCE);
  }

  function init() {
    // Fetch API data first, then process the DOM
    fetchSpots().then(() => {
      injectFilterBar();
      processSpots();
    });

    // Observe DOM mutations for SPA navigation and spot updates
    const observer = new MutationObserver((mutations) => {
      // Check if any mutations affect the spots area
      let relevant = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0) {
          relevant = true;
          break;
        }
      }
      if (relevant) {
        injectFilterBar();
        debouncedProcess();
      }
    });

    const target = document.querySelector("#app") || document.body;
    observer.observe(target, { childList: true, subtree: true });

    // Periodically refresh spot data from the API
    setInterval(async () => {
      await fetchSpots();
      // Re-show all rows and reprocess to handle updated data
      document.querySelectorAll(".sota-hunter-duplicate").forEach((row) => {
        row.classList.remove("sota-hunter-duplicate");
        row.style.display = "";
      });
      // Remove old tune buttons so they get refreshed data
      document.querySelectorAll(".sota-hunter-tune-btn").forEach((btn) => btn.remove());
      processSpots();
    }, POLL_INTERVAL);
  }

  // Start when the DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
