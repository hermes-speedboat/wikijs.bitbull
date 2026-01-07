---
title: Zabbix Reference Card
description: Reference and best practices for Zabbix monitoring
published: true
date: 2026-01-07T00:00:00.000Z
tags: referencecards, zabbix
editor: markdown
dateCreated: 2026-01-07T00:00:00.000Z
---

# Setup

If you takte Zabbix for production monitoring it is strongly adviced to use one of this operating systems:
* [CentOS/Red Hat Enterprise Linux](https://www.zabbix.com/documentation/current/manual/installation/install_from_packages/rhel_centos)
* [Ubuntu LTS](https://www.zabbix.com/documentation/current/manual/installation/install_from_packages/debian_ubuntu)
* [SuSE SLES](https://www.zabbix.com/documentation/current/manual/installation/install_from_packages/suse)

[Install Requirements](https://www.zabbix.com/documentation/current/manual/installation/requirements)  
[Upgrade Zabbix](https://www.zabbix.com/documentation/current/manual/installation/upgrade)  
[Security Best Practice](https://www.zabbix.com/documentation/current/manual/installation/requirements/best_practices)  
[Known Issues](https://www.zabbix.com/documentation/current/manual/installation/known_issues)

## Sizing

| **Name**    | **Platform**              | **CPU/Memory**         | **Database**                          | **Monitored hosts** |
|-------------|--------------------------|-----------------------|---------------------------------------|---------------------|
| *Small*     | CentOS                   | Virtual Appliance     | MySQL InnoDB                          | 100                 |
| *Medium*    | CentOS                   | 2 CPU cores/2GB       | MySQL InnoDB                          | 500                 |
| *Large*     | RedHat Enterprise Linux  | 4 CPU cores/8GB       | RAID10 MySQL InnoDB or PostgreSQL     | >1000               |
| *Very large*| RedHat Enterprise Linux  | 8 CPU cores/16GB      | Fast RAID10 MySQL InnoDB or PostgreSQL| >10000              |

# Architecture Components

### Server

[Zabbix server](https://www.zabbix.com/documentation/current/manual/concepts/server) is the central component to which agents report availability and integrity information and statistics. The server is the central repository in which all configuration, statistical and operational data are stored.

### Database storage

All configuration information as well as the data gathered by Zabbix is stored in a database.

### Web interface

For an easy access to Zabbix from anywhere and from any platform, the web-based interface is provided. The interface is part of Zabbix server, and usually (but not necessarily) runs on the same physical machine as the one running the server.

### Proxy

[Zabbix proxy](https://www.zabbix.com/documentation/current/manual/concepts/proxy) can collect performance and availability data on behalf of Zabbix server. A proxy is an optional part of Zabbix deployment; however, it may be very beneficial to distribute the load of a single Zabbix server.

### Agent

[Zabbix agents](https://www.zabbix.com/documentation/current/manual/concepts/agent) are deployed on monitoring targets to actively monitor local resources and applications and report the gathered data to Zabbix server.

### Data flow

* Host > Item > trigger > action
* Host > Template > action

Lets say that you want to receive an alert that your CPU load it too high on Server X you must first create a host entry for Server X followed by an item for monitoring its CPU, then a trigger which activates if the CPU is too high, followed by an action which sends you an email.
