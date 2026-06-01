# GeoSphere Austria Warnings – Home Assistant Integration

[![HACS Custom][hacs-badge]][hacs-url]
[![GitHub Release][release-badge]][release-url]
[![Validate with Hassfest][hassfest-badge]][hassfest-url]

Időjárás figyelmeztetések a **GeoSphere Austria WarnAPI** alapján, koordináta-alapú lekérdezéssel.  
Automatikusan a te városodra/falvadra vonatkozó figyelmeztetéseket jeleníti meg – nincs szükség régió/tartomány névből kiindulni.

---

## Entitások

A telepítés után a következő entitások jönnek létre (minden konfigurált helyszínhez):

### Binary Sensorok
| Entitás | Leírás |
|---|---|
| `binary_sensor.aktiv_idojarasi_figyelmeztetés` | `on` ha bármilyen aktív figyelmeztetés van |
| `binary_sensor.figyelmeztetés_vihar_szel` | `on` ha szélvihar figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_eso` | `on` ha eső figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_ho` | `on` ha hó figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_jegesedes` | `on` ha jegesedés figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_zivatar` | `on` ha zivatar figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_hoseg` | `on` ha hőség figyelmeztetés aktív |
| `binary_sensor.figyelmeztetés_hideg` | `on` ha hideg figyelmeztetés aktív |

### Sensorok
| Entitás | Leírás |
|---|---|
| `sensor.aktiv_figyelmeztetések_szama` | Aktív figyelmeztetések száma (0, 1, 2, …) |
| `sensor.legmagasabb_figyelmeztetési_szint` | Legmagasabb szint: `0`=nincs, `1`=sárga, `2`=narancs, `3`=piros |
| `sensor.figyelmeztetések_összefoglalója` | Szöveges összefoglaló, pl. `🟡 Zivatar (2025-06-01 14:00 – 20:00)` |

---

## Telepítés

### HACS (ajánlott)

1. Nyisd meg a HACS-et Home Assistantban
2. **Integrations** → három pont menü → **Custom repositories**
3. Add hozzá: `https://github.com/szepnorbee/ha-geosphere-warnings` → kategória: **Integration**
4. Keress rá: **GeoSphere Austria Warnings** → **Download**
5. Indítsd újra a Home Assistantot

### Manuális

Másold a `custom_components/geosphere_warnings` mappát a HA `custom_components/` könyvtárába, majd indítsd újra.

---

## Beállítás

1. **Beállítások** → **Eszközök és szolgáltatások** → **Integráció hozzáadása**
2. Keress rá: **GeoSphere Austria Warnings**
3. Add meg:
   - **Szélességi fok** (alapértelmezett: HA home koordináta)
   - **Hosszúsági fok** (alapértelmezett: HA home koordináta)
   - **Helyszín neve** (pl. `Stössing`)
   - **Lekérdezési intervallum** (perc, alapértelmezett: 30)

Több helyszín is hozzáadható (pl. otthon + munkahely).

---

## Automatizáció – Telegram értesítés

```yaml
automation:
  - alias: "GeoSphere – Figyelmeztetés értesítés"
    triggers:
      - trigger: state
        entity_id: binary_sensor.aktiv_idojarasi_figyelmeztetés
        from: "off"
        to: "on"
    actions:
      - action: notify.telegram
        data:
          message: >
            ⚠️ *Időjárás figyelmeztetés!*
            
            {{ states('sensor.figyelmeztetések_összefoglalója') }}
            
            Szint: {{ state_attr('sensor.legmagasabb_figyelmeztetési_szint', 'level_label') }}
```

### Szint alapú értesítés (csak narancs/piros)

```yaml
automation:
  - alias: "GeoSphere – Súlyos figyelmeztetés"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.legmagasabb_figyelmeztetési_szint
        above: 1   # 2=narancs, 3=piros
    actions:
      - action: notify.telegram
        data:
          message: >
            🔴 *SÚLYOS időjárás figyelmeztetés!*
            {{ states('sensor.figyelmeztetések_összefoglalója') }}
```

---

## Adatforrás

- **Forrás:** [GeoSphere Austria WarnAPI](https://openapi.hub.geosphere.at/warnapi/v1/)
- **Endpoint:** `https://warnungen.zamg.at/wsapp/api/getWarningsForCoords`
- **Autentikáció:** nem szükséges
- **Frissítési frekvencia:** konfigurálható, alapértelmezett 30 perc

### Figyelmeztetési szintek
| Szint | Szín | Leírás |
|---|---|---|
| 1 | 🟡 Sárga | Moderate |
| 2 | 🟠 Narancs | Severe |
| 3 | 🔴 Piros | Extreme |

### Figyelmeztetési típusok
| ID | Típus |
|---|---|
| 1 | Szél/Vihar |
| 2 | Eső |
| 3 | Hó |
| 4 | Jegesedés |
| 5 | Zivatar |
| 6 | Hőség |
| 7 | Hideg |

---

## Licenc

MIT License

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
[release-badge]: https://img.shields.io/github/v/release/szepnorbee/ha-geosphere-warnings
[release-url]: https://github.com/szepnorbee/ha-geosphere-warnings/releases
[hassfest-badge]: https://github.com/szepnorbee/ha-geosphere-warnings/actions/workflows/validate.yml/badge.svg
[hassfest-url]: https://github.com/szepnorbee/ha-geosphere-warnings/actions/workflows/validate.yml