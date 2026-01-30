---
title: convert
description: About converting 
published: true
date: 2026-01-30T08:38:01.798Z
tags: cmd, helpers, convert
editor: markdown
dateCreated: 2026-01-30T08:38:01.798Z
---

# convert
* rename files with spezial characters in it
```bash
convmv --notest -f latin1 -t utf8 *.pdf
```

* remove umlauts from file/folders
```bash
find . -type d | while read dir; do rename 's/ö/oe/g;s/Ö/Oe/g;s/ü/ue/g;s/Ü/Ue/g;s/ä/ae/g;s/Ä/Ae/g' "$dir"; done
find . -type f | while read file; do rename 's/ö/oe/g;s/Ö/Oe/g;s/ü/ue/g;s/Ü/Ue/g;s/ä/ae/g;s/Ä/Ae/g' "$file"; done
```
