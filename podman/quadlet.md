---
title: Quadlet getting started
description: Compare with Docker compose and examples
published: true
date: 2026-04-18T05:41:33.470Z
tags: podman, container, docker
editor: markdown
dateCreated: 2026-04-18T05:41:00.509Z
---

# Podman Quadlet – Getting Started

## Overview

**Podman Quadlet** is a declarative systemd integration for Podman.

Instead of running containers via CLI (`podman run`) or generating systemd units afterwards, Quadlet lets you define containers as **systemd-managed services using simple configuration files**.

👉 Official documentation:
[https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)

---

## What is Quadlet?

Quadlet is:

* A **generator for systemd units**
* A **declarative interface** for Podman resources
* A **native Linux service model for containers**

It allows you to define:

* `.container` → containers
* `.network` → networks
* `.volume` → volumes
* `.pod` → pods
* `.build` → image builds

These files are parsed by a systemd generator and converted into real `.service` units.

---

## Why was it created?

Quadlet solves several limitations:

### Problems without Quadlet

* `podman run` is imperative → not declarative
* `podman generate systemd` is static and outdated
* No clean integration into systemd dependency graph

### Goals of Quadlet

* Native **systemd lifecycle management**
* Declarative infrastructure
* First-class Linux service integration
* Rootless-friendly container operations

👉 Recommendation from Podman:
Use Quadlet instead of `generate systemd`.

---

## How Quadlet works

1. You place files in:

   ```bash
   ~/.config/containers/systemd/
   # or
   /etc/containers/systemd/
   ```

2. systemd runs a generator:

   ```
   podman-system-generator
   ```

3. It converts:

   ```
   *.container → *.service
   ```

4. You manage everything via systemd:

   ```bash
   systemctl --user start web.service
   ```

---

## Quadlet vs Docker Compose

👉 Compose reference:
[https://docs.docker.com/compose/gettingstarted/](https://docs.docker.com/compose/gettingstarted/)

| Feature             | Docker Compose      | Quadlet                   |
| ------------------- | ------------------- | ------------------------- |
| Config format       | YAML                | INI (systemd style)       |
| Scope               | Application-centric | Service-centric           |
| Lifecycle           | `docker compose up` | `systemctl`               |
| Dependency handling | `depends_on`        | `After=` + `Requires=`    |
| Health awareness    | built-in            | manual (`Notify=healthy`) |
| Build support       | inline (`build:`)   | separate `.build`         |
| Networking          | automatic           | explicit `.network`       |
| Orchestration level | app-level           | host-level                |

👉 Summary:

* **Compose = developer workflow**
* **Quadlet = production service integration**

---

## Example: Docker Compose (reference)

👉 Source:
[https://docs.docker.com/compose/gettingstarted/](https://docs.docker.com/compose/gettingstarted/)

```yaml
services:
  web:
    build: .
    ports:
      - "${APP_PORT}:5000"
    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
```

---

# Quadlet Equivalent Setup

## Architecture

* shared network: `app.network`
* services:

  * `redis.container`
  * `web.container`
* volume:

  * `redis-data.volume`

---

## 1. Network

`app.network`

```ini
[Unit]
Description=App network

[Network]
NetworkName=app
Driver=bridge
```

---

## 2. Volume

`redis-data.volume`

```ini
[Unit]
Description=Redis data volume

[Volume]
VolumeName=redis-data
```

---

## 3. Redis container

`redis.container`

```ini
[Unit]
Description=Redis service

[Container]
ContainerName=redis
Image=docker.io/library/redis:alpine
Network=app.network
NetworkAlias=redis
Volume=redis-data.volume:/data

# Healthcheck
HealthCmd=["redis-cli","ping"]
HealthInterval=5s
HealthTimeout=3s
HealthRetries=5
HealthStartPeriod=10s
HealthOnFailure=kill

# Critical for dependency handling
Notify=healthy

[Service]
Restart=always
TimeoutStartSec=900
```

---

## 4. Web container

Assumes image is prebuilt:

```bash
podman build -t localhost/web:latest .
```

`web.container`

```ini
[Unit]
Description=Web service
Requires=redis.container
After=redis.container

[Container]
ContainerName=web
Image=localhost/web:latest
Pull=never
Network=app.network
PublishPort=8000:5000

Environment=REDIS_HOST=redis
Environment=REDIS_PORT=6379

[Service]
Restart=always
TimeoutStartSec=900

[Install]
WantedBy=default.target
```

---

## Optional: Build via Quadlet

`web.build`

```ini
[Unit]
Description=Build web image

[Build]
ImageTag=localhost/web:latest
File=./Dockerfile
SetWorkingDirectory=unit
```

Then in `web.container`:

```ini
Image=web.build
```

---

# Startup

```bash
systemctl --user daemon-reload
systemctl --user start web.service
```

Dependencies automatically start:

* network
* volume
* redis

---

# Key Differences vs Compose

### depends_on → systemd dependencies

Compose:

```yaml
depends_on:
  redis:
    condition: service_healthy
```

Quadlet:

```ini
Requires=redis.container
After=redis.container
```

* Redis:

```ini
Notify=healthy
```

---

### Networking

Compose:

* automatic network

Quadlet:

* explicit:

```ini
Network=app.network
```

---

### Service discovery

Compose:

```
redis:6379
```

Quadlet:

* must ensure:

```ini
ContainerName=redis
# or
NetworkAlias=redis
```

---

# Cheat Sheet

## File locations

```bash
# rootless
~/.config/containers/systemd/

# rootful
/etc/containers/systemd/
```

---

## Core commands

```bash
# reload generator
systemctl --user daemon-reload

# start service
systemctl --user start web.service

# enable at login
systemctl --user enable web.service

# logs
journalctl --user -u web.service -f

# status
systemctl --user status web.service

# list containers
podman ps -a
```

---

## Debugging

```bash
# generator dry-run
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun

# verify unit
systemd-analyze --user verify web.service

# run healthcheck manually
podman healthcheck run redis
```

---

## Important Quadlet keys

### Container

```ini
Image=
ContainerName=
Network=
NetworkAlias=
Volume=
PublishPort=
Environment=
HealthCmd=
Notify=healthy
Pull=
AutoUpdate=
```

---

### Unit (systemd)

```ini
Requires=
After=
```

---

### Service

```ini
Restart=
TimeoutStartSec=
```

---

### Install

```ini
WantedBy=default.target
```

---

## Best Practices

* Always set `ContainerName=` for predictable DNS
* Use `.network` explicitly
* Use `Notify=healthy` for dependency correctness
* Prefer prebuilt images for simplicity
* Use Quadlet for **long-running services**, not dev loops

---

## Summary

Quadlet is:

> **systemd-native container orchestration for single-node environments**

Best suited for:

* servers
* homelabs
* edge nodes
* production services without Kubernetes

