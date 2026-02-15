---
title: dnf
description: Useful comands with dnf/yum
published: true
date: 2026-02-15T07:24:17.428Z
tags: linux, dnf, rpm
editor: markdown
dateCreated: 2026-02-15T07:24:17.428Z
---

## find rpm depending on files
* what provides the manpage I need
```bash
dnf provides */tcp.7*
dnf provides *bin/mailx
```