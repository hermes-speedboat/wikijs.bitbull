---
title: ksm
description: 
published: true
date: 2026-02-01T09:16:53.394Z
tags: howto, setup, ksm, kvm
editor: markdown
dateCreated: 2026-02-01T09:16:53.394Z
---

## tuning
It is easy to enable kvm. However, the defaults are fairly conservative.

### howto enable
* `vi /etc/rc.local`

```bash
# ksm page merging, default 0
echo 1 > /sys/kernel/mm/ksm/run
# pages to scan on each run, default: 100
echo 1000 > /sys/kernel/mm/ksm/pages_to_scan
# time to sleep after each scan, default: 200
echo 20 > /sys/kernel/mm/ksm/sleep_millisecs
```
```bash
chmod +x /etc/rc.d/rc.local
```

### load tuning
```bash
free -t | grep ^Mem: | awk '{print $7/1024 " MB"}'
top # sort for cpu with "P" and look for ksmd
```