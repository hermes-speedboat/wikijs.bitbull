---
title: Bob's Inbox
description: AI Agents Scratch pad
published: true
date: 2026-03-20T09:11:17.700Z
tags: 
editor: markdown
dateCreated: 2026-03-10T13:43:26.119Z
---

# NanoBob's Notes
* Her are the temp notes, my nanobot is keeping

### GO Regeln einfach erklärt

Go ist ein strategisches Brettspiel für zwei Personen.
Ziel ist es, mit eigenen Steinen möglichst viel Gebiet zu sichern.

• 2 Spieler: Schwarz und Weiß
• Gespielt wird auf einem 9×9 Gitter (81 Schnittpunkte)
• Die Steine werden auf die Schnittpunkte, nicht in Felder, gelegt
• Schwarz beginnt

1. Spielablauf
1. Schwarz setzt einen Stein auf einen freien Schnittpunkt.
2. Danach setzt Weiß.
3. Es wird abwechselnd genau ein Stein gesetzt.
4. Ein gesetzter Stein bleibt liegen (keine Bewegung).

2. Freiheit (Liberties)
Jeder Stein braucht mindestens eine freie Nachbarposition (oben, unten, links, rechts).
Diese nennt man Freiheiten.
• Hat ein Stein oder eine zusammenhängende Gruppe keine Freiheit mehr, wird sie vom Brett entfernt.

3. Schlagen (Gefangennahme)
Wenn du die letzte Freiheit einer gegnerischen Gruppe besetzt:
– Diese Steine werden vom Brett genommen.
– Du bewahrst sie als Gefangene auf (zählen bei der Wertung).

4. Selbstmordregel
Du darfst keinen Stein setzen, wenn er sofort keine Freiheit hätte,
ausser du schlägst dadurch gleichzeitig gegnerische Steine.

5. Ko-Regel
Man darf nicht sofort eine Stellung wiederherstellen,
die exakt wie im Zug davor aussieht.
Das verhindert endlose Wiederholungen.

6. Wann endet das Spiel?
Wenn beide Spieler hintereinander passen, endet die Partie.

7. Wertung (einfach erklärt)
Am Ende zählt man:
• Freie Schnittpunkte, die nur von deiner Farbe umgeben sind = Gebiet
• Gefangene gegnerische Steine
Wer mehr Punkte hat, gewinnt.


### Quantum NFS Firewall Rules / Debugging

````
DMSG:
Vor der anpassung an der FW:
[Tue Mar 10 08:34:00 2026] lockd: server 10.0.7.8 not responding, still trying
Nach der Anpassung an der FW:
[Tue Mar 10 08:43:52 2026] lockd: server 10.0.7.8 OK

Debug Helper CMD:
root@mail01.~# rpcinfo -p 10.0.7.8
program vers proto   port service
    100000  2   tcp  111  portmapper
    100000  4   udp  111  portmapper
    100024  1   udp  628   status
    100024  1   tcp  628   status
    100005  1   udp  880   mountd
    100005  1   tcp  880   mountd
    100003  3   tcp 2049   nfs
    100003  4   udp 2049   nfs
    100021  1   udp 32000  nlockmgr
    100021  3   tcp 32000  nlockmgr

AKTUELLE MOUNT OPTIONEN, ABGESTIMMT AUF QUANTUM UND STATEFUL:
root@mail01.~# grep ^10 /etc/fstab
10.0.7.8:/Q/shares/Mail_Backup_dumps /opt/zimbra/backup nfs _netdev,nofail,vers=3,proto=tcp,mountproto=tcp,noatime,hard,timeo=600,retrans=2,rsize=1048576,wsize=1048576 0 0
````

### Crypto Vermögens Steuer Schweiz

🔗 Link zum Berechnen von Cryptos in der Schweizer Steuer Erklärung🇨🇭:
https://www.ictax.admin.ch/extern/de.html#/ratelist/2025

* Checkliste (Jahresende)
• ✅ Alle Wallets audieren  
• ✅ Wert zum 31.12. ermitteln (CHF)  
• ✅ Berechnung: Portfolio × Satz = Versteuerbares Vermögen
• ✅ In Steuererklärung unter Vermögen deklarieren (am besten Berechnungs Grundlage beilegen)

### Windows Registry 
Verständnis der Struktur der Windows-Registry:

**Registry-Hierarchie:**
- Schlüssel (ähnlich wie Ordner)
- Unterschlüssel
- Werte (Daten, die in Schlüsseln gespeichert sind)

Jeder Wert enthält:
- Name
- Daten
- Datentyp

**Haupt-Registrerings-Hives (Stammschlüssel):**
- HKEY_LOCAL_MACHINE (HKLM) – Systemweite Einstellungen (Hardware, Treiber, installierte Software, Sicherheit)
- HKEY_CURRENT_USER (HKCU) – Einstellungen für den aktuell angemeldeten Benutzer
- HKEY_CLASSES_ROOT (HKCR) – Verwaltet Dateizuordnungen und Programmregistrierungen
- HKEY_USERS (HKU) – Konfigurationsdaten für alle Benutzerprofile auf dem System
- HKEY_CURRENT_CONFIG (HKCC) – Informationen über das Hardwareprofil

**Gängige Datentypen:**
- REG_SZ (Zeichenfolge)
- REG_DWORD (32-Bit-Wert)
- REG_QWORD (64-Bit-Wert)
- REG_BINARY (Binärdaten)
- REG_MULTI_SZ (Mehrere Zeichenfolgen)

**Warum es wichtig ist:**
- Systemfehlerbehebung
- Sicherheitskonfiguration
- Leistungsoptimierung
- Softwarebereitstellung
- Fortgeschrittene Windows-Verwaltung

### empty Qdrant Collection 

````
POST /collections/wiki/points/delete
{
  "with_vectors": true,
  "with_payload": true,
  "filter": {}
}
````

### Qdrant search

````
python3 - <<'PY' | curl -X POST "http://rag.domain.tld/collections/wiki/points/search" \
  -H "Content-Type: application/json" \
  -d @- | jq
import json
print(json.dumps({
  "vector": [0.1]*2560,
  "limit": 5,
  "with_payload": True
}))
PY
````

```
{
  "limit": 50,
  "filter": {
    "must": [
      {
        "key": "metadata.title",
        "match": {
          "text": "AWX"
        }
      }
    ]
  }
}
```

### DGX Spark Specs
NVIDIA DGX Spark - Hardware Specifications

Core Components:
- SoC: NVIDIA GB10 Grace Blackwell Superchip
- CPU: 20-Core ARM (10x Cortex-X925 + 10x Cortex-A725)
- GPU: NVIDIA Blackwell Architecture
- CUDA Cores: 6,144
- Tensor Cores: 5. Generation
- RT Cores: 4. Generation
- Memory: 128 GB LPDDR5x (unified)
- Memory Bandwidth: 273 GB/s (256-bit @ 4266 MHz)
- Storage: 1 TB oder 4 TB NVMe M.2 (Self-Encrypting)

Performance:
- AI Compute: Bis zu 1,000 TOPS (Inferenz)
- FP4 Performance: Bis zu 1 PFLOP (mit Sparsity)
- Copy Engines: 2 (simultane Datenübertragungen)
- Max Model Size: Bis zu 200 Milliarden Parameter (Single) / 405B (Dual)

Connectivity & I/O:
- Ethernet: 1x RJ-45 (10 GbE)
- High-Speed Network: 2x QSFP (ConnectX-7 Smart NIC)
- Wireless: Wi-Fi 7, Bluetooth 5.4
- USB: 4x USB Type-C (einer mit Power Delivery)
- Video: 1x HDMI 2.1a (multichannel audio)
- Video Processing: 1x NVENC, 1x NVDEC

Physical:
- Form Factor: Small Form Factor (SFF)
- Dimensions: 150 mm (L) x 150 mm (W) x 50.5 mm (H)
- Weight: 1.2 kg (2.6 lbs)
- Power Supply: 240W extern (inklusive)
- TDP (GB10): 140W
- Available for other: 100W (ConnectX-7, Wi-Fi, SSD, etc.)

Environmental:
- Operating Temp: 5°C bis 30°C (41°F bis 86°F)
- Humidity: 10% bis 90% (non-condensing)
- Altitude: Bis zu 3,000 Meter (9,843 feet)

Pricing:
- Founders Edition: ~$4,699 (ca. 4,500 CHF)
- Pre-installed: NVIDIA AI Software Stack

Quelle: NVIDIA DGX Spark User Guide (https://docs.nvidia.com/dgx/dgx-spark/hardware.html)
