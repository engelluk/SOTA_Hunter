# SOTA Hunter

**Ein Klick zum Abstimmen. Ein Klick zum Loggen. SOTAwatch nie verlassen.**

SOTA Hunter ist eine Chrome-Erweiterung, die **Tune**- und **Log**-Schaltflächen direkt in die [SOTAwatch3](https://sotawatch.sota.org.uk/)-Spotstabelle einfügt — damit du eine Gipfelaktivierung arbeiten kannst, ohne die Tastatur anzufassen oder das Fenster zu wechseln.

---

## Vorher / Nachher

| Ohne SOTA Hunter | Mit SOTA Hunter |
|---|---|
| ![SOTAwatch ohne Erweiterung](screenshots/without%20extension.png) | ![SOTAwatch mit Erweiterung](screenshots/with%20enxtension.png) |

---

## Was beim Klicken passiert

### Tune (blauer Button)
Stellt Frequenz und Betriebsart deines **Yaesu FT-DX10** mit einem Klick per direktem seriellen CAT ein — keine Zwischensoftware, keine CAT-zu-TCP-Brücken.

Das richtige Seitenband wird automatisch gewählt:
- SSB → LSB unterhalb 7,3 MHz, USB darüber
- FT8 / FT4 / JS8 / DATA → DATA-U
- CW, FM, AM werden unverändert übernommen

### Log (lila Button)
Öffnet einen kurzen RST-Dialog und sendet dann einen **vollständigen ADIF-QSO-Datensatz** per UDP an das HRD Logbook — genau das gleiche Protokoll wie WSJT-X, sodass keine zusätzliche Konfiguration außer der Aktivierung der QSO-Weiterleitung in HRD erforderlich ist.

![RST-Dialog vor dem Loggen](screenshots/log.png)

Der geloggte Datensatz enthält Rufzeichen, Frequenz, Band, Betriebsart, **SOTA_REF**, Gipfelname und Höhe (live von der SOTA-API abgerufen) sowie dein Stationsrufzeichen und Locator.

---

## Funktionen auf einen Blick

| Funktion | Details |
|---|---|
| Direktes CAT-Abstimmen | Serieller Port (Standard COM7, 38400 Baud) — keine Zwischensoftware |
| HRD Logbook-Integration | UDP ADIF auf Port 2333 — wie WSJT-X/JTDX |
| Aktivierer-Deduplizierung | Zeigt nur den neuesten Spot pro Aktivierer — weniger Unübersichtlichkeit |
| Gipfelanreicherung | Ruft Name & Höhe von der SOTA-API ab, wird gecacht |
| RST-Dialog | Vorausgefüllt 59/599/+00 je nach Betriebsart, vor dem Senden bearbeitbar |
| Visuelle Rückmeldung | Orange → ausstehend, Grün → Erfolg, Rot → Fehler mit Tooltip |
| Einstellungs-Popup | COM-Port, Rufzeichen, Locator, Log-Port und Verbindungstest konfigurieren |

---

## Voraussetzungen

- **Windows** + **Google Chrome**
- **Python 3.6+** mit `pyserial` im System-`PATH`
- **Yaesu FT-DX10** an einem seriellen/USB-Port (getestet auf COM7 via Silicon Labs CP2105)
- **HRD Logbook** (optional) mit aktivierter UDP-QSO-Weiterleitung auf Port 2333

---

## Schnelleinrichtung

### 1 — Native Host registrieren
`native-host\install.bat` doppelklicken. Dies schreibt einen Registry-Schlüssel, damit Chrome die Python-Bridge findet.

### 2 — Erweiterung laden
1. `chrome://extensions/` öffnen
2. **Entwicklermodus** aktivieren
3. **Entpackt laden** klicken → Ordner `extension/` auswählen
4. Die auf der Karte angezeigte Erweiterungs-ID notieren

### 3 — Native-Host-Manifest konfigurieren
Vorlage kopieren:
```
native-host\com.sotahunter.bridge.json.template  →  native-host\com.sotahunter.bridge.json
```
Die `.json`-Datei öffnen und einstellen:
```json
"path": "C:\\Users\\DeinName\\SOTA_Hunter\\native-host\\bridge.bat",
"allowed_origins": ["chrome-extension://DEINE_ERWEITERUNGS_ID/"]
```

### 4 — Rufzeichen und Locator einstellen
SOTA Hunter-Toolbar-Symbol klicken → Rufzeichen, Locator und COM-Port eintragen → **Speichern**.

### 5 — HRD QSO-Weiterleitung aktivieren (für Log)
HRD Logbook → **Tools → Konfigurieren → QSO-Weiterleitung** → *"QSO-Benachrichtigungen per UDP von anderen Anwendungen empfangen (WSJT-X)"* aktivieren.

---

## Fehlerbehebung

| Symptom | Lösung |
|---|---|
| Tune-Button wird rot | COM-Port in den Einstellungen prüfen; **Verbindung testen** verwenden; `native-host\bridge.log` prüfen |
| Log-Button wird rot | Prüfen ob HRD Logbook läuft und UDP-Weiterleitung aktiviert ist |
| Keine Buttons erscheinen | SOTAwatch neu laden; `chrome://extensions/` auf Fehler prüfen |
| „Verbindung zum Native Host nicht möglich" | `install.bat` erneut ausführen; `.json`-Manifest auf korrekten Pfad und Erweiterungs-ID prüfen; Chrome neu starten |

---

## Architektur

```
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → FT-DX10 (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome startet die Python-Bridge bei Bedarf automatisch — kein manueller Prozessstart, keine offenen localhost-Ports.

---

## Lizenz

MIT — siehe [LICENSE](LICENSE).

---

*73 de DM6LE — gebaut für Chaser, die beim seltenen Gipfel nicht am VFO-Knopf fummelm wollen.*
