---
title: helpers
description: Daily comands that make your life easier
published: true
date: 2026-02-17T17:11:22.686Z
tags: helpers, kubernetes
editor: markdown
dateCreated: 2026-02-17T17:11:22.686Z
---

## login to database
### postgresql
```bash
PGPASSWORD="$POSTGRES_PASSWORD" \
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```
### bitnami mariadb
```bash
/opt/bitnami/mariadb/bin/mariadb \
  -h 127.0.0.1 \
  -u "$MARIADB_USER" \
  -p"$MARIADB_PASSWORD" \
  "$MARIADB_DATABASE"
```
