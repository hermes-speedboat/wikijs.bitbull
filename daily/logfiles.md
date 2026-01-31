---
title: logfiles
description: All about logfiles, journald, auditd
published: true
date: 2026-01-31T10:36:30.276Z
tags: cmd, helpers, logs, rh10
editor: markdown
dateCreated: 2026-01-30T09:05:05.024Z
---

## auditd logrotate generations
Tested on Rocky Linux 10
```bash
sed -i 's/max_log_file_action =.*/max_log_file_action = rotate/' /etc/audit/auditd.conf
sed -i 's/max_log_file =.*/max_log_file = 30/' /etc/audit/auditd.conf
pkill -9 -f /sbin/auditd
ps -ef | grep -i auditd
systemctl start auditd.service
systemctl status auditd.service
ls -la /var/log/audit/
```

## Make `less` behave like `tail -f`
```bash
less +F somelogfile
```
