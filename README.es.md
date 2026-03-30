# SOTA Hunter

**Un clic para sintonizar. Un clic para registrar. Nunca salgas de SOTAwatch.**

SOTA Hunter es una extensión de Chrome que añade botones **Tune** y **Log** directamente en la tabla de spots de [SOTAwatch3](https://sotawatch.sota.org.uk/) — para trabajar una activación de cima sin tocar el teclado ni cambiar de ventana.

---

## Antes / Después

| Sin SOTA Hunter | Con SOTA Hunter |
|---|---|
| ![SOTAwatch sin extensión](screenshots/without%20extension.png) | ![SOTAwatch con extensión](screenshots/with%20enxtension.png) |

---

## Qué ocurre al hacer clic

### Tune (botón azul)
Ajusta la frecuencia VFO y el modo de tu **radio Yaesu** con un clic mediante CAT serie directo — sin software intermedio, sin puentes CAT-a-TCP.

La banda lateral correcta se elige automáticamente:
- SSB → LSB por debajo de 7,3 MHz, USB por encima
- FT8 / FT4 / JS8 / DATA → DATA-U
- CW, FM, AM se transmiten sin cambios

### Log (botón morado)
Abre un breve diálogo de RST y luego envía un **registro QSO ADIF completo** al HRD Logbook vía UDP — exactamente el mismo protocolo que WSJT-X, por lo que no se necesita configuración adicional más allá de activar el reenvío de QSO en HRD.

![Diálogo RST antes de registrar](screenshots/log.png)

El registro incluye indicativo, frecuencia, banda, modo, **SOTA_REF**, nombre y altitud de la cima (obtenidos en tiempo real desde la API SOTA), y el indicativo y locator de tu estación.

---

## Funciones de un vistazo

| Función | Detalle |
|---|---|
| Sintonización CAT directa | 8 modelos Yaesu soportados — baudios configurados automáticamente por modelo |
| Liberación automática del puerto COM | Puerto serie liberado automáticamente al cerrar la pestaña de SOTAwatch |
| Integración con HRD Logbook | UDP ADIF en el puerto 2333 — igual que WSJT-X/JTDX |
| Deduplicación de activadores | Muestra solo el spot más reciente por activador — reduce el desorden |
| Enriquecimiento de cimas | Obtiene nombre y altitud de la API SOTA, almacenado en caché |
| Diálogo RST | Prerelleno 59/599/+00 según el modo, editable antes de enviar |
| Retroalimentación visual | Naranja → pendiente, verde → éxito, rojo → error con tooltip |
| Popup de ajustes | Selector de modelo de radio, puerto COM, indicativo, locator, puerto de log, probar conexión |

---

## Radios soportadas

Actualmente soporta todos los radios Yaesu que usan el protocolo ASCII CAT estándar. Selecciona tu modelo en el popup — los baudios correctos se rellenan automáticamente.

| Radio | Baudios por defecto | Conexión |
|---|---|---|
| FT-DX10 | 38400 | USB (Silicon Labs CP2105) |
| FTX-1 | 38400 | USB (Silicon Labs CP2105) |
| FT-710 | 38400 | USB (Silicon Labs CP2105) |
| FTDX101MP/D | 38400 | USB + RS-232C |
| FT-991A | 4800 | USB (Silicon Labs CP210x) |
| FT-891 | 9600 | USB (Silicon Labs CP210x) |
| FTDX3000 | 4800 | RS-232C (adaptador USB necesario) |
| FTDX1200 | 4800 | RS-232C + USB |

Usa **Custom / Other** para cualquier radio Yaesu no listado — configura los baudios manualmente.

---

## Requisitos

- **Windows** + **Google Chrome**
- **Python 3.6+** con `pyserial` en tu `PATH`
- **Radio Yaesu** (ver Radios soportadas) conectado via USB o RS-232C serie
- **HRD Logbook** (opcional) con reenvío UDP de QSO activado en el puerto 2333

---

## Instalación rápida

### 1 — Registrar el host nativo
Haz doble clic en `native-host\install.bat`. Esto escribe una clave de registro para que Chrome pueda encontrar el puente Python.

### 2 — Cargar la extensión
1. Abre `chrome://extensions/`
2. Activa el **Modo desarrollador**
3. Haz clic en **Cargar descomprimida** → selecciona la carpeta `extension/`
4. Anota el ID de extensión que aparece en la tarjeta

### 3 — Configurar el manifiesto del host nativo
Copia la plantilla:
```
native-host\com.sotahunter.bridge.json.template  →  native-host\com.sotahunter.bridge.json
```
Abre el archivo `.json` y establece:
```json
"path": "C:\\Users\\TuNombre\\SOTA_Hunter\\native-host\\bridge.bat",
"allowed_origins": ["chrome-extension://TU_ID_DE_EXTENSION/"]
```

### 4 — Configurar los ajustes
Haz clic en el icono de SOTA Hunter en la barra de herramientas para abrir el popup de ajustes:

![Ajustes de la extensión](screenshots/extension%20settings.png)

- **Radio Model** — selecciona tu radio; los baudios se rellenan automáticamente
- **COM Port** — puerto serie de tu radio (consultar el Administrador de dispositivos)
- **My Callsign / Grid Square** — incluidos en cada QSO registrado
- **HRD Log Port** — puerto UDP para HRD Logbook (por defecto: 2333)

Haz clic en **Test Connection** para verificar que el radio responde.

### 5 — Activar el reenvío QSO de HRD (para Log)
HRD Logbook → **Herramientas → Configurar → Reenvío QSO** → activar *"Recibir notificaciones QSO vía UDP de otras aplicaciones (WSJT-X)"*.

---

## Solución de problemas

| Síntoma | Solución |
|---|---|
| El botón Tune se pone rojo | Comprobar el puerto COM en ajustes; usar **Probar conexión**; revisar `native-host\bridge.log` |
| El botón Log se pone rojo | Comprobar que HRD Logbook esté en ejecución con el reenvío UDP activado |
| No aparecen botones | Recargar SOTAwatch; comprobar errores en `chrome://extensions/` |
| "No se puede conectar al host nativo" | Volver a ejecutar `install.bat`; verificar la ruta e ID de extensión en el manifiesto `.json`; reiniciar Chrome |

---

## Arquitectura

```
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → Radio Yaesu (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome lanza automáticamente el puente Python bajo demanda — sin procesos que iniciar manualmente, sin puertos localhost abiertos.

---

## Licencia

MIT — ver [LICENSE](LICENSE).

---

*73 de DM6LE — construido para cazadores que no quieren manosear el botón VFO cuando una cima rara está en el aire.*
