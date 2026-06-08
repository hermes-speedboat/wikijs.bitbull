---
title: Qwen3.6-35B-A3B vLLM Setup on DGX Spark
description: Optimized vLLM inference with MoE, AWQ 4-bit and MTP on the DGX Spark (GB10, Grace Blackwell ARM64)
published: true
date: 2026-06-08T10:17:53.874Z
tags: ai, vllm, dgx_spark
editor: markdown
dateCreated: 2026-06-08T09:10:50.089Z
---

# Qwen3.6-35B-A3B vLLM Setup on DGX Spark

Optimized vLLM inference with MoE, AWQ 4-bit and MTP on the DGX Spark (GB10, Grace Blackwell ARM64).

## Goal

Run **Qwen3.6-35B-A3B** (Mixture of Experts) on the DGX Spark at maximum throughput for agents, n8n and OpenWebUI. Thinking/reasoning tokens are suppressed server-wide for clean API responses.

## Performance

- **Qwen3.6-35B-A3B** (AWQ 4-bit + MTP): **50-70 tok/s generation**, 528 tok/s prompt processing
- KV cache usage at 32k context: ~0.7%

## Quickstart

```bash
cd /srv/vllm
git clone https://github.com/hermes-speedboat/vllm.qwen3.6-35b_mtp_spark.git .
bash setup_vllm.sh        # venv + vllm + huggingface-hub
bash download_model.sh     # 24 GB model from HF
bash vllm-server.sh        # start server on port 8000
```

## Architecture

### MoE (Mixture of Experts)

Qwen3.6-35B-A3B has **35B parameters total** but only **3B active parameters per token**.
256 experts total, 8 active per token + 1 shared expert. 40 layers (mixed: DeltaNet Linear-Attention + Full-Attention).

Advantage over a dense 27B model: ~10x less memory bandwidth required → significantly higher throughput on bandwidth-constrained hardware like the DGX Spark.

### AWQ 4-bit

Accuracy-aware quantization to 4-bit (group_size=32). Model weighs **24 GB total** on disk, ~1.5 GB active per forward pass.

vLLM flags: `--quantization awq --dtype float16`

Reason for `float16` over `bfloat16`: AWQ quantization requires float16 compute dtype. Using `bfloat16` (the default with `--dtype auto`) produces an error.

### MTP (Multi Token Prediction)

Qwen3.6 was trained with multi-token prediction heads. vLLM uses this for speculative decoding:

- Model generates 2 draft tokens per forward pass
- Verification achieves ~85-98% acceptance rate
- **Effective 1.5-2x more tokens per time unit**

MTP is baked into the model architecture (`config.json: "mtp_num_hidden_layers": 1`). The relevant vLLM flag is `--speculative-config '{"method":"mtp","num_speculative_tokens":2}'`.

Note: The feature was renamed from `qwen3_next_mtp` to `mtp` in vLLM 0.22.1. The old name is deprecated.

### Why not GGUF or FP8?

- **GGUF** models achieve only 8-13 tok/s on the DGX Spark due to the GGUF parser overhead and lack of ARM64-optimized kernels. The `qwen35` GGUF architecture is also unsupported by the transformers GGUF parser.
- **FP8** (1 byte/param) would require ~27 GB for the full dense model — plus MoE sparsity isn't utilized.
- **AWQ + MoE** exploits the DGX Spark's memory bandwidth bottleneck: only 3B active params/token × 0.5 bytes = 1.5 GB moved per forward pass vs 27 GB for a comparable dense FP8 model.

## Reasoning / Thinking

Qwen3.6 generates internal reasoning (thinking tokens) by default. Unlike the earlier approach with `--default-chat-template-kwargs '{"enable_thinking": false}'`, reasoning is now **enabled** — the model generates full thinking in responses.

This is because `--default-chat-template-kwargs` conflicts with `tool_choice: "auto"` in vLLM 0.22.1, preventing native `tool_calls` from being parsed correctly.

Hermes (and most agent frameworks) handles thinking tokens from models like DeepSeek without issues — the reasoning is separated into its own field. If you run agents that cannot tolerate reasoning, configure them to use a different endpoint (OpenRouter, etc.).

## Configuration

All parameters are controlled via environment variables in `vllm-server.sh`:

- `PORT` (8000): Server port
- `MAX_MODEL_LEN` (262144): Maximum context length (up to 262144)
- `GPU_MEM_UTIL` (0.65): GPU memory utilization fraction
- `LANGUAGE_ONLY` (true): Disable vision encoder
- `NUM_SPEC_TOKENS` (2): MTP speculative tokens per step
- `MODEL_REPO` (cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit): Hugging Face model repository

## Tool Calling

Tool/function calling is partially supported for agent frameworks (Hermes, n8n, etc.):

- `--enable-auto-tool-choice`: Allow automatic tool selection from request
- `--tool-call-parser hermes`: Parse Hermes-style XML tool call output

**Limitation in vLLM 0.22.1:** `tool_choice: "auto"` does not produce native OpenAI `tool_calls` for this model. The model generates valid `<tool_call>` XML in the response content, but vLLM does not parse it into the structured `tool_calls` field. Forced tool calls (`tool_choice: "required"` or named function) work correctly.

Affects: Hermes agent with tool-heavy workloads. Workaround: route tool-heavy requests through a different endpoint (OpenRouter, etc.) and use this server for high-throughput text generation.

These are hardcoded in `vllm-server.sh` and not overridable via env vars.

## First-Request Latency

The first request after server start may have a latency spike (CUDA graph compilation). vLLM warns:
```
causes a latency spike; consider extending warmup to cover this shape/config.
```

Mitigated with `--enforce-eager`, which skips CUDA graph optimization entirely. On the DGX Spark the throughput difference is negligible.

## Systemd Autostart

```bash
mkdir -p ~/.config/systemd/user/
cp vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now vllm
```

For headless operation: `loginctl enable-linger $USER`

## Repository

All setup files are on GitHub:

**Repo:** [hermes-speedboat/vllm.qwen3.6-35b_mtp_spark](https://github.com/hermes-speedboat/vllm.qwen3.6-35b_mtp_spark)

| File | Purpose |
|---|---|
| `setup_vllm.sh` | Install uv, venv, vllm, huggingface-hub |
| `download_model.sh` | Download model via `snapshot_download()` |
| `vllm-server.sh` | Start vLLM with optimized flags |
| `vllm.service` | Systemd user service file |
| `test_vllm.sh` | API functional test |

## Hardware

- **DGX Spark (GB10):** Grace Blackwell ARM64, 128 GB unified memory
- **CUDA:** Blackwell GPU with ~1.5 TB/s memory bandwidth
- **Model + KV cache:** 24 GB (AWQ) + 32k context → ~0.7% cache utilization
- **ARM64:** vLLM works via `--torch-backend=auto`

## Troubleshooting

### GGUF Error "architecture qwen35 is not supported"

vLLM + transformers GGUF parser does not support newer architectures like `qwen35`. Solution: use PyTorch/safetensors format via `snapshot_download()`.

### AWQ Requires float16

```
ValueError: torch.bfloat16 is not supported for quantization method awq
```

Solution: always set `--dtype float16` explicitly. Do not rely on `--dtype auto` with AWQ models.

### OpenWebUI / Ollama API 404s

Clients (OpenWebUI) probing Ollama-compatible endpoints produce harmless 404s:
```
GET /api/v1/models 404
GET /api/tags 404
GET /v1/props 404
```

These are not server errors. Configure OpenWebUI to use an **OpenAI-compatible** endpoint (vLLM), not Ollama API path. The vLLM server only serves OpenAI-compatible endpoints at `/v1/models`, `/v1/chat/completions`, etc.

### JIT Kernel Compilation Warning

```
Triton kernel JIT compilation during inference
```

One-time warning on first request. Kernel is cached by Triton, warning disappears on subsequent requests.