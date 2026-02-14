---
title: Bugs & Fixes
description: Known issues and solutions for Rundeck
published: true
date: 2026-02-14T13:58:24.019Z
tags: rundeck, bugfix
editor: markdown
dateCreated: 2026-02-14T13:58:24.019Z
---

# BUGS & FIXES

## Error Msg: `/bin/sh: /tmp/0-1-localhost-dispatch-script.tmp.sh: Permission denied`
```bash
echo '
# ----------------------------------------------------------------
# CUSTOM VALUES
# ----------------------------------------------------------------
framework.file-copy-destination-dir = ~/
' >> /etc/rundeck/framework.properties

systemctl restart rundeckd
```

## service.log not rotated
* Problem: /var/log/rundeck/service.log grows and get not rotated
```bash
cat << EOF > /etc/logrotate.d/rundeck_service
/var/log/rundeck/service.log {
 su root root
 copytruncate
 daily
 missingok
 rotate 7
 compress
 delaycompress
 notifempty
 create 640 root adm
}
EOF

logrotate -fv /etc/logrotate.d/rundeck_service
```


