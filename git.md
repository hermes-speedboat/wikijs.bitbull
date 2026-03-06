---
title: Git Notes
description: Helpful git comands
published: true
date: 2026-03-06T06:05:42.914Z
tags: helpers, git
editor: markdown
dateCreated: 2026-03-06T06:05:42.914Z
---

# Git Daily Commands Cheat Sheet

Praktische Git-Kommandos für den täglichen Einsatz.  
Diese Liste deckt ~95% typischer Entwickler-Workflows ab.

---

# Repository Setup

## Neues Repository erstellen
```bash
git init
```

## Repository klonen
```bash
git clone <repo-url>
```

---

# Status & Überblick

## Status anzeigen
```bash
git status
```

## Commit-Historie anzeigen
```bash
git log
```

## Kompakte Historie
```bash
git log --oneline --graph --decorate
```

## Änderungen anzeigen
```bash
git diff
```

## Änderungen im Staging-Bereich
```bash
git diff --staged
```

---

# Dateien hinzufügen / Commit

## Einzelne Datei hinzufügen
```bash
git add file.txt
```

## Alle Änderungen hinzufügen
```bash
git add .
```

## Commit erstellen
```bash
git commit -m "commit message"
```

## Commit inklusive aller Änderungen
```bash
git commit -am "commit message"
```

---

# Remote Repositories

## Remote anzeigen
```bash
git remote -v
```

## Änderungen herunterladen
```bash
git fetch
```

## Änderungen herunterladen und mergen
```bash
git pull
```

## Änderungen hochladen
```bash
git push
```

---

# Branching

## Branch anzeigen
```bash
git branch
```

## Branch erstellen
```bash
git branch feature-x
```

## Branch wechseln
```bash
git switch feature-x
```

## Branch erstellen und wechseln
```bash
git switch -c feature-x
```

## Branch löschen
```bash
git branch -d feature-x
```

---

# Merging

## Branch mergen
```bash
git merge feature-x
```

## Merge abbrechen
```bash
git merge --abort
```

---

# Undo / Fehler korrigieren

## Datei zurücksetzen (lokale Änderungen verwerfen)
```bash
git restore file.txt
```

## Alle Änderungen verwerfen
```bash
git restore .
```

## Datei aus Staging entfernen
```bash
git restore --staged file.txt
```

## Letzten Commit ändern
```bash
git commit --amend
```

## Letzten Commit rückgängig machen (ohne Änderungen zu verlieren)
```bash
git reset --soft HEAD~1
```

## Hard Reset auf letzten Commit
```bash
git reset --hard HEAD
```

---

# Stash (temporäre Änderungen speichern)

## Änderungen stashen
```bash
git stash
```

## Stashes anzeigen
```bash
git stash list
```

## Stash wiederherstellen
```bash
git stash pop
```

---

# Dateien löschen / verschieben

## Datei löschen
```bash
git rm file.txt
```

## Datei verschieben / umbenennen
```bash
git mv old.txt new.txt
```

---

# .gitignore Änderungen anwenden

Wenn Dateien bereits getrackt sind und du `.gitignore` angepasst hast:

```bash
git rm -r --cached .
git add .
git commit -m "Remove ignored files"
```

---

# Nützliche Power Commands

## Gelöschte Dateien finden
```bash
git log --diff-filter=D --summary
```

## Datei aus einem alten Commit wiederherstellen
```bash
git checkout <commit> -- path/to/file
```

## Letzten Branch wechseln
```bash
git switch -
```

---

# Sehr hilfreiche Aliases

```bash
git config --global alias.lg "log --oneline --graph --decorate"
git config --global alias.st status
git config --global alias.co checkout
```

Beispiele:

```bash
git lg
git st
```

---

# Typischer Daily Workflow

```bash
git pull
git status
git add .
git commit -m "feature update"
git push
```

---

# Tipp

Bei Problemen:

```bash
git status
```

ist fast immer der erste Schritt.