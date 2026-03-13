---
title: Install Nanobot
description: Install Nanobot on Rocky10 with some features
published: true
date: 2026-03-13T06:20:01.705Z
tags: nanobot, ai
editor: markdown
dateCreated: 2026-03-13T06:20:01.705Z
---

# Nanobot Installation
* https://github.com/HKUDS/nanobot

## Infrastructure
I have a DGX Spark running in my LAB, so I only configure with ollama.
If you use own providers, just look into project documentation.
Note that ollama api is not working properly, so I use vllm api for now.
There are some drawbacks, but it goes to far to explain that here.

#### Install Ollama on DGX Spark
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

* `systemctl edit ollama`
```
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAM_KEEP_ALIVE=1h"
```
* open firewall port
```bash
ufw enable 11434/tcp
```
* configure bot model
```bash
cd
mkdir models
cd models
```
* `vi Modelfile-bot-qwen3.5-9b`
```
FROM qwen3.5:9b
# higher can hold more context in conversations, but uses more memory on ollama
PARAMETER num_ctx 131072
# Stable Instruct Mode
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 40
PARAMETER min_p 0.05
# loop control
PARAMETER presence_penalty 0.2
PARAMETER repeat_penalty 1.1
# tokenlimit
# align with nanobot setting if lower or higher
PARAMETER num_predict 8192                                       
# deterministic runs
PARAMETER seed 42
```
* create new bot model
```bash
ollama create qwen3.5-9b-bot -f Modelfile-bot-qwen3.5-9b
ollama ls | grep bot
```

## Nanobot setup
* Setup  and initialize nanobot
```bash
dnf install tar git tree
useradd nanobot

# enable systemd userspace config for nanobot user
loginctl enable-linger nanobot

# I do not cover SELinux here
vi /etc/selinux/config
setenforce 0

# install uv and nanobot
su - nanobot
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install nanobot-ai
 
# create file structure and sample config
nanobot onboard
```

Setup basis config, read and replace values as needed
If you do not understand what to insert in values, read project doc first
`vi .nanobot/config.json`
```
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "qwen3.5-9b-bot:latest",
      "provider": "auto",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 40,
      "memoryWindow": 100,
      "reasoningEffort": null
    }
...
  "tools": {
    "web": {
      "search": {
        "apiKey": "BS..replace..Dz",
        "maxResults": 5
      }
    },
...
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://1.1.replace.1.1:11434/v1",
      "extraHeaders": null
    },
...
  "channels": {
    "sendProgress": true,
    "sendToolHints": false,
    "telegram": {
      "enabled": true,
      "token": "86104....replace...hCfgs",
      "allowFrom": ["2...replace...8"],
      "proxy": null,
      "replyToMessage": false
    },
```

WIP, hang on
