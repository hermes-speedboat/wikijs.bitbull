---
title: fetch stuff
description: download, get, copy
published: true
date: 2026-01-30T09:38:20.071Z
tags: cmd, helpers
editor: markdown
dateCreated: 2026-01-30T09:38:20.071Z
---

* mirror website with cli
 ```bash
wget --random-wait -r -U Mozilla -e robots=off --span-hosts --domains miyuru.lk --convert-links https://www.miyuru.lk/geoiplegacy/
httrack "https://lab9.lab.domain.info/" -s0 -O "./" "+*.lab.domain.info/*" -v
```