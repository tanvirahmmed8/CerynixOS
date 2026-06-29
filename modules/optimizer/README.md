# Optimization Engine v1

## Purpose
The Optimization Engine applies system-level tunings (CPU governors, swappiness) based on predefined workload profiles. It is designed to be invoked by the Action Broker on behalf of CerynixAI, allowing the assistant to dynamically tune the system in response to health degradation or user requests.

## Main Components
- `src/profiles.json`: Defines the tuning parameters for workloads like `gaming`, `coding`, and `battery_saver`.
- `src/engine.py`: The CLI entry point (`cerynix-optimizer`) that applies the tunings and logs decisions.
- `src/revert_manager.py`: Captures the pre-tuning state, enabling a reliable `cerynix-optimizer revert` command.
- `default.nix`: Packages the tool and grants the Action Broker `sudo` privileges to run it securely.

## Data Flow
- CerynixAI detects a need to optimize -> Action Broker (`POST /execute` `{"tool": "cerynix-optimizer", "arguments": ["set", "gaming"]}`) -> `cerynix-optimizer set gaming` -> Sysfs modifications.

## Explainability
Every decision or revert action is logged to `/var/log/cerynixos-optimizer/decisions.log` so users and CerynixAI can understand *why* the system feels different.
