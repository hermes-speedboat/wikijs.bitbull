---
title: Bob's Inbox
description: AI Agents Scratch pad
published: true
date: 2026-03-12T06:20:23.122Z
tags: 
editor: markdown
dateCreated: 2026-03-10T13:43:26.119Z
---

# NanoBob's Notes
* Her are the temp notes, my nanobot is keeping

### 2026-03-06 17:42

```
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
```

### 2026-03-10 14:34

````
DMSG:
Vor der anpassung an der FW:
[Tue Mar 10 08:34:00 2026] lockd: server 10.0.7.8 not responding, still trying
Nach der Anpassung an der FW:
[Tue Mar 10 08:43:52 2026] lockd: server 10.0.7.8 OK

Debug Helper CMD:
root@mail01.~# rpcinfo -p 10.0.7.8
program vers proto   port service
    100000  4   tcp  111  portmapper
    100000  3   tcp  111  portmapper
    100000  2   tcp  111  portmapper
    100000  4   udp  111  portmapper
    100000  3   udp  111  portmapper
    100000  2   udp  111  portmapper
    100024  1   udp  628  status
    100024  1   tcp  628  status
    100005  1   udp  880  mountd
    100005  1   tcp  880  mountd
    100005  2   udp  880  mountd
    100005  2   tcp  880  mountd
    100005  3   udp  880  mountd
    100005  3   tcp  880  mountd
    100003  3   tcp 2049  nfs
    100003  4   tcp 2049  nfs
    100227  3   tcp 2049
    100003  3   udp 2049  nfs
    100003  4   udp 2049  nfs
    100227  3   udp 2049
    100021  1   udp 32000  nlockmgr
    100021  3   tcp 32000  nlockmgr
    100021  4   tcp 32000  nlockmgr
    100021  1   tcp 32000  nlockmgr
    100021  3   udp 32000  nlockmgr
    100021  4   udp 32000  nlockmgr

AKTUELLE MOUNT OPTIONEN, ABGESTIMMT AUF QUANTUM UND STATEFUL:
root@mail01.~# grep ^10 /etc/fstab
10.0.7.8:/Q/shares/Mail_Backup_dumps /opt/zimbra/backup nfs _netdev,nofail,vers=3,proto=tcp,mountproto=tcp,noatime,hard,timeo=600,retrans=2,rsize=1048576,wsize=1048576 0 0
````

### 2026-03-12 07:20

````
🔗 Link zum Berechnen von Cryptos in der Schweizer Steuer Erklärung🇨🇭:

https://www.ictax.admin.ch/extern/de.html#/ratelist/2025

---

✅ Checkliste (Jahresende)

• [ ] Alle Wallets audieren  
• [ ] Wert zum 31.12. ermitteln (CHF)  
• [ ] Kantonalen Steuersatz prüfen (via ICTAX Link)  
• [ ] Berechnung: Portfolio × Satz = Steuer  
• [ ] In Steuererklärung deklarieren
````