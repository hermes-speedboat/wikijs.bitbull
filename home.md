---
title: Welcome
description: Welcome
published: true
date: 2026-01-31T08:56:53.823Z
tags: 
editor: markdown
dateCreated: 2026-01-30T07:35:57.104Z
---

# Welcome
Welcome to my Open Source Wiki, it's a place for knowledge, hacking and sharing useful information.
Content is focused on business and lean usage of Linux and Open Source applications.

# Links
* [Script Archive](https://github.com/joe-speedboat/scripts)
* [GitHub](https://github.com/joe-speedboat)
* [Ansible Galaxy](https://galaxy.ansible.com/ui/standalone/namespaces/3440/)

# Interesting stuff
* [Radxa Dragon Q6A - Single board computer based on Qualcom QCS6490](https://radxa.com/products/dragon/q6a/)
  * Fedora Install to NVMe (boot into SDCard with t4 image)
    ```bash
    smartctl --all /dev/nvme0n1
    nvme format --ses=1 /dev/nvme0n1
    curl -L https://mirror.iscas.ac.cn/fedora-riscv/releases/42/Spins/aarch64/images/QCS6490/Radxa-Dragon-Q6A/Fedora-GNOME-42-20251017000000.QCS6490.Radxa-Dragon-Q6A.raw.gz | gzip -d | sudo dd of=/dev/nvme0n1 bs=4M status=progress conv=fsync oflag=sync
    fstrim -av
    ```
    
* [Personal onpremise AI assistant](https://openclaw.ai/)
* [AI Workflow Automation Platform & Tools](https://n8n.io/)
* [Ollama is the easiest way to automate your work using open models onprem](https://ollama.com/)
* [Rundeck is the orchestration tool for all of your existing automation](https://www.rundeck.com/)
* [Ascender provides a web-based user interface, REST API, and task engine for Ansible](https://github.com/ctrliq/ascender)
