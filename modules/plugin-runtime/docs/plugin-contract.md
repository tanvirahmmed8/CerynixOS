# CerynixOS Plugin Contract (v1)

Plugins allow developers to extend the capabilities of CerynixAI securely. A plugin is distributed as a directory containing a `manifest.json` and an executable entrypoint.

## 1. Structure
```text
my-plugin/
├── manifest.json
└── main.py (or any executable binary/script)
```

## 2. manifest.json Schema
```json
{
  "name": "weather-plugin",
  "version": "1.0.0",
  "description": "Fetches local weather.",
  "entrypoint": "./main.py",
  "permissions": [
    "network:read",
    "file:read_tmp"
  ]
}
```

## 3. Execution Interface
The Action Broker (via the `plugin_runner`) will execute your entrypoint.
- **Input:** Passed as command-line arguments, or JSON string to `stdin` (if defined by your tool schema).
- **Output:** Your script MUST output valid JSON to `stdout`. Any non-JSON debug logs should be written to `stderr`.

## 4. Isolation
Your plugin runs under the `cerynix-plugin-user`. You do NOT have root access. You cannot read system secrets. If your plugin violates the permissions requested in the manifest, the runner will terminate it and log a security audit event.
