---
title: network
description: network related
published: true
date: 2026-01-30T15:19:30.476Z
tags: cmd, helpers, networking
editor: markdown
dateCreated: 2026-01-30T15:19:30.476Z
---

* Proxy environment variables
* https://about.gitlab.com/blog/2021/01/27/we-need-to-talk-no-proxy/
* `$HOME/.bashrc`
```bash
export http_proxy=http://proxy.example.com:8080
export no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```
`/etc/environment`
```bash
http_proxy=http://proxy.example.com:8080
no_proxy=whole-domain-direct.com,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```
|                       | curl      | wget           | Ruby      | Python    | Go        |
| --------------------- | --------- | -------------- | --------- | --------- | --------- |
| no_proxy              | Yes       | Yes            | Yes       | Yes       | Yes       |
| NO_PROXY              | Yes       | No             | Yes       | Yes       | Yes       |
| Case precedence       | lowercase | lowercase only | lowercase | lowercase | Uppercase |
| Matches suffixes?     | Yes       | Yes            | Yes       | Yes       | Yes       |
| Strips leading .?     | Yes       | No             | Yes       | Yes       | No        |
| * matches all hosts?  | Yes       | No             | No        | Yes       | Yes       |
| Supports regexes?     | No        | No             | No        | No        | No        |
| Supports CIDR blocks? | No        | No             | Yes       | No        | Yes       |
| Detects loopback IPs? | No        | No             | No        | No        | Yes       |

* blink NIC LED for 5 minutes
```bash
NIC=$(ip route show default 0.0.0.0/0 | awk '{print $5; exit}')
END=$((SECONDS+300))
while [ $SECONDS -lt $END ]; do
    ip link set $NIC down
    sleep 2
    ip link set $NIC up
    sleep 2
done
```

