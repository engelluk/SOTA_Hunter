# SOTA Hunter

**Un clic pour syntoniser. Un clic pour logger. Ne quittez jamais SOTAwatch.**

SOTA Hunter est une extension Chrome qui ajoute des boutons **Tune** et **Log** directement dans le tableau des spots de [SOTAwatch3](https://sotawatch.sota.org.uk/) — pour travailler une activation de sommet sans toucher au clavier ni changer de fenêtre.

---

## Avant / Après

| Sans SOTA Hunter | Avec SOTA Hunter |
|---|---|
| ![SOTAwatch sans extension](screenshots/without%20extension.png) | ![SOTAwatch avec extension](screenshots/with%20enxtension.png) |

---

## Ce qui se passe quand vous cliquez

### Tune (bouton bleu)
Règle la fréquence VFO et le mode de votre **radio Yaesu** en un clic via CAT série direct — aucun logiciel intermédiaire, aucun pont CAT-vers-TCP.

Le bon côté de bande est choisi automatiquement :
- SSB → LSB en dessous de 7,3 MHz, USB au-dessus
- FT8 / FT4 / JS8 / DATA → DATA-U
- CW, FM, AM sont transmis sans modification

### Log (bouton violet)
Ouvre un rapide dialogue RST, puis envoie un **enregistrement QSO ADIF complet** au HRD Logbook via UDP — exactement le même protocole que WSJT-X, donc aucune configuration supplémentaire n'est nécessaire au-delà de l'activation du transfert QSO dans HRD.

![Dialogue RST avant le log](screenshots/log.png)

L'enregistrement loggé comprend l'indicatif, la fréquence, la bande, le mode, la **SOTA_REF**, le nom et l'altitude du sommet (récupérés en direct depuis l'API SOTA), ainsi que l'indicatif et le locator de votre station.

---

## Fonctionnalités en un coup d'œil

| Fonctionnalité | Détail |
|---|---|
| Syntonisation CAT directe | 8 modèles Yaesu supportés — débit configuré automatiquement par modèle |
| Libération automatique du port COM | Port série libéré automatiquement à la fermeture de l'onglet SOTAwatch |
| Intégration HRD Logbook | UDP ADIF sur le port 2333 — identique à WSJT-X/JTDX |
| Déduplication des activateurs | N'affiche que le spot le plus récent par activateur — réduit l'encombrement |
| Enrichissement des sommets | Récupère le nom et l'altitude depuis l'API SOTA, mis en cache |
| Dialogue RST | Pré-rempli 59/599/+00 selon le mode, modifiable avant l'envoi |
| Retour visuel | Orange → en attente, vert → succès, rouge → erreur avec info-bulle |
| Popup de paramètres | Sélecteur de modèle radio, port COM, indicatif, locator, port de log, test de connexion |

---

## Radios supportées

Supporte actuellement tous les radios Yaesu utilisant le protocole ASCII CAT standard. Sélectionnez votre modèle dans le popup — le débit correct est renseigné automatiquement.

| Radio | Débit par défaut | Connexion |
|---|---|---|
| FT-DX10 | 38400 | USB (Silicon Labs CP2105) |
| FTX-1 | 38400 | USB (Silicon Labs CP2105) |
| FT-710 | 38400 | USB (Silicon Labs CP2105) |
| FTDX101MP/D | 38400 | USB + RS-232C |
| FT-991A | 4800 | USB (Silicon Labs CP210x) |
| FT-891 | 9600 | USB (Silicon Labs CP210x) |
| FTDX3000 | 4800 | RS-232C (adaptateur USB requis) |
| FTDX1200 | 4800 | RS-232C + USB |

Utilisez **Custom / Other** pour tout radio Yaesu non listé — configurez le débit manuellement.

---

## Prérequis

- **Windows** + **Google Chrome**
- **Python 3.6+** avec `pyserial` dans votre `PATH`
- **Radio Yaesu** (voir Radios supportées) connecté via USB ou RS-232C série
- **HRD Logbook** (optionnel) avec le transfert QSO UDP activé sur le port 2333

---

## Installation rapide

### 1 — Enregistrer le host natif
Double-cliquer sur `native-host\install.bat`. Cela écrit une clé de registre pour que Chrome puisse trouver le bridge Python.

### 2 — Charger l'extension
1. Ouvrir `chrome://extensions/`
2. Activer le **Mode développeur**
3. Cliquer sur **Charger l'extension non empaquetée** → sélectionner le dossier `extension/`
4. Noter l'identifiant de l'extension affiché sur la carte

### 3 — Configurer le manifeste du host natif
Copier le modèle :
```
native-host\com.sotahunter.bridge.json.template  →  native-host\com.sotahunter.bridge.json
```
Ouvrir le fichier `.json` et définir :
```json
"path": "C:\\Users\\VotreNom\\SOTA_Hunter\\native-host\\bridge.bat",
"allowed_origins": ["chrome-extension://VOTRE_ID_EXTENSION/"]
```

### 4 — Configurer les paramètres
Cliquer sur l'icône SOTA Hunter dans la barre d'outils pour ouvrir le popup de paramètres :

![Paramètres de l'extension](screenshots/extension%20settings.png)

- **Radio Model** — sélectionner votre radio ; le débit est renseigné automatiquement
- **COM Port** — port série de votre radio (vérifier dans le Gestionnaire de périphériques)
- **My Callsign / Grid Square** — inclus dans chaque QSO loggé
- **HRD Log Port** — port UDP pour HRD Logbook (défaut : 2333)

Cliquer sur **Test Connection** pour vérifier que le radio répond.

### 5 — Activer le transfert QSO HRD (pour Log)
HRD Logbook → **Outils → Configurer → Transfert QSO** → activer *"Recevoir les notifications QSO via UDP d'autres applications (WSJT-X)"*.

---

## Dépannage

| Symptôme | Solution |
|---|---|
| Le bouton Tune devient rouge | Vérifier le port COM dans les paramètres ; utiliser **Tester la connexion** ; vérifier `native-host\bridge.log` |
| Le bouton Log devient rouge | Vérifier que HRD Logbook fonctionne avec le transfert UDP activé |
| Aucun bouton n'apparaît | Recharger SOTAwatch ; vérifier les erreurs dans `chrome://extensions/` |
| « Impossible de se connecter au host natif » | Relancer `install.bat` ; vérifier le chemin et l'ID d'extension dans le manifeste `.json` ; redémarrer Chrome |

---

## Architecture

```
SOTAwatch DOM → content.js → background.js → bridge.py → cat_client.py  → Radio Yaesu (CAT)
                                                        → adif_logger.py → HRD Logbook (UDP)
```

Chrome lance automatiquement le bridge Python à la demande — aucun processus à démarrer manuellement, aucun port localhost ouvert.

---

## Licence

MIT — voir [LICENSE](LICENSE).

---

*73 de DM6LE — conçu pour les chasseurs qui ne veulent pas tripoter le bouton VFO quand un sommet rare est en ligne.*
