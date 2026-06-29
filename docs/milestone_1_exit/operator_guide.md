# CerynixOS: Milestone 1 Operator Guide

Welcome to CerynixOS. This guide explains how to interact with the local Device Plane modules built during Milestone 1.

## 1. Starting the CerynixAI Desktop UI
Because we are in a simulated development environment, the UI is built using Web Technologies (HTML/JS/CSS) as a prototype for the final Desktop Overlay.
To view the UI:
1. Run the UI Server:
   ```bash
   cerynix-ui-server
   ```
2. Open your browser to `http://localhost:3000`. You will see the premium glassmorphism interface, Optimization Dashboard, and Chat UI.

## 2. Using the Telemetry & Optimization Tools
- **Health Diagnostics:** Run `cerynix-diag --export` to generate a redacted snapshot of the system's CPU/RAM/Service health.
- **Optimization Profiles:** Run `cerynix-optimizer apply gaming` (or `coding`, `battery_saver`) to adjust kernel parameters.
- **One-Click Revert:** If a profile causes issues, simply run `cerynix-optimizer revert` to instantly restore the previous system state.

## 3. Testing Self-Healing
You can test the self-healing daemon by manually killing a critical service and watching the healer bring it back:
```bash
systemctl stop cerynix-action-broker
cerynix-healer
systemctl is-active cerynix-action-broker # Will report 'active'
```

## 4. Testing the Update Agent Rollback
We have included a mock test harness to prove the OS will automatically rollback a bad update:
```bash
python /var/lib/cerynixos-src/modules/update-agent/src/update_test.py
```
*(This will feed a poisoned metadata file into the agent and assert that a rollback is triggered).*

## 5. Using Plugins
Developers can manage plugins securely:
```bash
cerynix-plugin-manager list
cerynix-plugin-runner weather-plugin Seattle
```
All executions are isolated and logged to `/var/log/cerynixos-plugins/audit.log`.
