# Local AI Runtime Foundation

## Purpose
This module provides the local inference engine (`llama.cpp`), model management, and the Inference Manager daemon for CerynixOS. It ensures that the device can process natural language and generate tool calls securely, completely offline.

## Main Components
- `default.nix`: Installs `llama-cpp` and python dependencies, and defines the `cerynix-inference-manager` systemd service.
- `model-loader.nix`: Fetches the default `qwen2.5-0.5b-instruct-q4_k_m.gguf` model and writes `/etc/cerynixos/ai/model-config.json`.
- `src/inference_manager.py`: The Python daemon that loads the model, enforces memory budgets, handles timeouts, and serves inference requests via a local HTTP API over a Unix Domain Socket (UDS) (`/run/cerynixos/ai-runtime.sock`).
- `src/task_memory.py`: Local task storage with privacy controls.
- `src/prompt_templates.py`: OS-specific system prompts.
- `src/benchmark.py`: Local benchmarking tool.

## Data Flow
- CerynixAI Desktop UI -> Inference Manager (HTTP over UDS) -> `llama.cpp` process -> CerynixAI Desktop UI.
- Output from Inference Manager is sent to the Action Broker (Phase 3).

## Risks or Limits
- The 0.5B model is heavily quantized. It is fast and uses < 1GB RAM, but complex reasoning may fail. We rely on the Action Broker to catch unsafe tool calls.
- `fetchurl` will cause a ~350MB download during the initial `nix build` of the OS.
