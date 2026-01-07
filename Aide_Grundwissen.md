---
title: AIDE Grundwissen
description: AIDE (Advanced Intrusion Detection Environment) ist ein hostbasiertes IntrusionDetectionSystem.
published: true
tags: referencecards, aide
editor: markdown
dateCreated: 2026-01-07
---

AIDE (Advanced Intrusion Detection Environment) ist ein hostbasiertes IntrusionDetectionSystem.
Es überprüft die Integrität der Dateien über Checksummen und meldet Änderungen.

**Homepage:** http://www.cs.tut.fi/~rammer/aide.html  
**Lizenz:** GPL 

# AIDE konfigurieren

Als erstes die Pfade und Dateien die AIDE überprüfen soll in `/etc/aide.conf` anpassen. Erläuterungen der übrigen Parameter bekommt man mit `man aide.conf`

# Datenbank initialisieren

Beim ersten Start muss die Datenbank mit den Prüfsummen erstellt werden.

```bash
aide --init
```

Die Datenbank wurde in `/var/lib/aide/aide.db.new` gespeichert. `/var/lib/aide/aide.db.new` muss jetzt in `/var/lib/aide/aide.db` umbenannt werden, sofern das nicht in der Konfiguration geändert wurde.

```bash
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```

# Datenbank und AIDE sichern

Nun sollte man `/usr/bin/aide`, `/etc/aide.conf` und `/var/lib/aide.db` auf einem sicheren Medium zb. CD-RW speichern. Will man AIDE auch von CD starten kann man den Pfad zur aide.db auf `./aide.db` in der Konfigurationsdatei ändern.

# Integrität prüfen

```bash
aide --check
```

Überprüft AIDE die Dateien auf System mit der Datenbank und meldet Änderungen auf die Konsole.

Mit `-f` kann man den Pfad zur `aide.conf` angeben um z.B. die Konfiguration von CD zu lesen.

```bash
cd /cdrom
aide -f ./aide.conf --check
```

# Änderungen in die Datenbank übernehmen

```bash
aide --update
```

In `/var/lib/aide.db.new` wurde die aktualisierte Datenbank gespeichert. Die muss wieder umbenannt und gesichert werden.

```bash
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```
