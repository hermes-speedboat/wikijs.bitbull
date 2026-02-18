---
title: logging with gelf
description: Log Rundeck application logs into gelf destination
published: true
date: 2026-02-15T06:26:20.916Z
tags: rundeck, logging
editor: markdown
dateCreated: 2026-02-14T13:55:52.316Z
---

# gelf remote logging
* https://github.com/tseeker/rundeck-gelf-plugin
```bash
$ cd /var/lib/rundeck/libext
$ wget https://raw.githubusercontent.com/tseeker/rundeck-gelf-plugin/master/GelfPlugin.groovy
$ cd /etc/rundeck

# set values as default, since (by bug) framework.properties get not honored
$ grep default /var/lib/rundeck/libext/GelfPlugin.groovy
        host defaultValue:"syslog.domain.local", required:true, description: "Hostname to connect to"
        port defaultValue:2222, required:true, description: "Port to connect to", type: 'Integer'

$ grep Gelf rundeck-config.properties
rundeck.execution.logs.streamingWriterPlugins=GelfPlugin
```