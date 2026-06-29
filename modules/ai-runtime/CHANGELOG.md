# Changelog - AI Runtime Module

## 2026-06-29
- **Feature:** Initial AI Runtime setup
- **Changes:**
  - Added `llama-cpp` and Python dependencies to system packages.
  - Implemented `model-loader.nix` to fetch Qwen 2.5 0.5B GGUF automatically.
  - Created Python-based `inference_manager` systemd service.
  - Secured `inference_manager` by switching from TCP port 8080 to Unix Domain Sockets (`/run/cerynixos/ai-runtime.sock`).
  - Created `task_memory`, `prompt_templates`, and `benchmark` utilities.
