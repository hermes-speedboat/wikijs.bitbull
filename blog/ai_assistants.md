---
title: AI Assistant Framework Comparsion
description: Research about OpenClaw alternatives
published: true
date: 2026-03-07T18:43:55.953Z
tags: llm, blog, ai, ai assistant
editor: markdown
dateCreated: 2026-03-07T09:58:18.982Z
---

# AI Assistant Frameworks – Kurzvergleich

| Produkt | Sprache | Deployment | Fokus | Interfaces | Admin | Footprint | Tools / Features | MCP | Security | CVEs | LLM Support | GitHub |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ZeroClaw** | Rust | Static binary, Docker | Lokaler autonomer Agent | CLI + viele Chat Apps | CLI + TOML | Sehr klein (<5MB RAM) | Shell, Browser, Git, HTTP, Scheduler, Vector+BM25 Memory | Ja | Stark (Sandbox, Allowlists, local-only) | Keine | OpenAI, Claude, Ollama | ⭐ ~24k |
| **NanoClaw** | TypeScript | Docker / Node | Container-basierter Personal Assistant | Viele Chat Apps | JSON + CLI | Klein (Container) | Web, File, Gmail, Scheduler | Ja | Mittel (Container Isolation) | pot. Env-Key Leak | Claude, OpenAI kompatibel | ⭐ ~20k |
| **PicoClaw** | Go | Single binary | Extrem leicht für SBC / Edge | Viele Chat Apps + CLI | YAML/JSON | <10MB RAM | Cron, File, Search, SQLite Memory | Geplant / integriert | Basis Sandbox | Keine | OpenAI, Claude, Ollama, DeepSeek | ⭐ ~23k |
| **nanobot** | Python | pip / Docker | Einfacher Single-User Assistant | Viele Chat Apps + Email | JSON + CLI | Klein (~10–20MB RAM) | Web, Mail, Shell, Scheduler, MCP Tools | Ja | Mittel (frühere Schwächen) | CVE-2026-2577 (fix) | OpenAI, Claude, Ollama, vLLM | ⭐ ~30k |
| **IronClaw** | Rust | Binary + Docker | Security-first Assistant | CLI, Web UI, Telegram, Slack | Web UI + CLI | Mittel (Postgres + WASM) | WASM Sandbox Tools, Scheduler, Vector Memory | Ja | Sehr hoch (Sandbox + Secret Vault) | Keine | GPT, Claude (Cloud) | ⭐ ~6k |
| **TinyClaw** | TypeScript | Node / Docker | Multi-Agent Team Orchestrator | Discord, WhatsApp, Telegram, CLI | JSON + CLI | Klein | Agent Routing, Task Queue, Parallel Agents | Nein | Niedrig | Keine | Claude, GPT | ⭐ ~3k |

**Kurzfazit**

- **Effizienz / Edge:** PicoClaw, ZeroClaw  
- **Einfach & flexibel:** nanobot  
- **Security-fokussiert:** IronClaw  
- **Container-Isolation:** NanoClaw  
- **Multi-Agent Workflow:** TinyClaw  