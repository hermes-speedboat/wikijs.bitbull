---
title: shell
description: shell hints
published: true
date: 2026-01-31T10:37:31.783Z
tags: cmd, helpers
editor: markdown
dateCreated: 2026-01-30T08:51:16.945Z
---


## count processes per user
```bash
ps hax -o user | sort | uniq -c
```

## Get the 10 biggest files/folders for the current direcotry
```bash
du -sm * .[^\.]* | sort -n | tail
```
