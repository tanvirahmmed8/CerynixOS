# Action Broker

## Purpose
The Action Broker is the strict security boundary between the AI Runtime and the host operating system. It receives JSON tool calls via a Unix Domain Socket, validates them against the active enterprise policy, sanitizes arguments, executes them safely, and writes audit logs.

## Main Components
- `default.nix`: Sets up the `cerynix-broker` user, systemd service, and highly restricted sudoers rules.
- `src/broker.py`: FastAPI application serving over UDS (`/run/cerynixos/broker.sock`).
- `src/policy_engine.py`: Loads the enterprise policy mock fixture to determine if a tool is allowed and if it requires user approval.
- `src/executor.py`: Uses `subprocess` to safely invoke local binaries (no shell injection).
- `src/audit_logger.py`: Emits structured JSON events to `/var/log/cerynixos-audit/broker-events.log`.

## Data Flow
AI Runtime -> `POST /execute` -> Policy Check -> Argument Sanitization -> Sudo Subprocess -> JSON Response.

## Risks or Limits
- The `sudo.extraRules` configuration grants the broker passwordless access to restart ANY systemd service. This is a deliberate design choice for self-healing, but relies entirely on the `policy_engine.py` and `executor.py` for sandbox enforcement. Any vulnerability in argument parsing could lead to privilege escalation.
