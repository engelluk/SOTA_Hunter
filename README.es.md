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
Ajusta la frecuencia VFO y el modo de tu **Yaesu FT-DX10** con un clic mediante CAT serie directo — sin software intermedio, sin puentes CAT-a-TCP.

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
| Sintonización CAT directa | Puerto serie (COM7 por defecto, 38400 baudios) — sin software intermedio |
| Integración con HRD Logbook | UDP ADIF en el puerto 2333 — igual que WSJT-X/JTDX |
| Deduplicación de activadores | Muestra solo el spot más reciente por activador — reduce el desorden |
| Enriquecimiento de cimas | Obtiene nombre y altitud de la API SOTA, almacenado en caché |
| Diálogo RST | Prerelleno 59/599/+00 según el modo, editable antes de enviar |
| Retroalimentación visual | Naranja → pendiente, verde → éxito, rojo → error con tooltip |
| Popup de ajustes | Configurar puerto COM, indicativo, locator, puerto de log, probar conexión |

---

## Requisitos

- **Windows** + **Google Chrome**
- **Python 3.6+** con `pyserial` en tu `PATH`
- **Yaesu FT-DX10** en un puerto serie/USB (probado en COM7 via Silicon Labs CP2105)
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

### 4 — Establecer tu indicativo y locator
Haz clic en el icono de SOTA Hunter en la barra de herramientas → rellena el indicativo, locator y puerto COM → **Guardar**.

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
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → FT-DX10 (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome lanza automáticamente el puente Python bajo demanda — sin procesos que iniciar manualmente, sin puertos localhost abiertos.

---

## Licencia

MIT — ver [LICENSE](LICENSE).

---

*73 de DM6LE — construido para cazadores que no quieren manosear el botón VFO cuando una cima rara está en el aire.*
