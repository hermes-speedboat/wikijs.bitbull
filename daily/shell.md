---
title: shell
description: shell hints
published: true
date: 2026-01-30T09:39:36.115Z
tags: cmd, helpers, shell
editor: markdown
dateCreated: 2026-01-30T08:51:16.945Z
---

* trash a open logfile
```bash
cat /dev/null > logfile
echo -n > logfile
> logfile #bash
```

* count processes per user
```bash
ps hax -o user | sort | uniq -c
```

* Get the 10 biggest files/folders for the current direcotry
```bash
du -sm * .[^\.]* | sort -n | tail
```
