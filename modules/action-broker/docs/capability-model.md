# CerynixOS Capability Model

The Action Broker enforces strict privilege separation. The AI runtime has zero direct access to the system. All actions must be brokered.

## Tool Categories and Privileges

### 1. File Operations
- **Tools:** `file_read`, `file_write`, `grep`
- **Privilege:** Low. Runs as the invoking user or the unprivileged broker service user.
- **Restrictions:** Cannot write to `/etc/` or `/nix/store/` directly. Cannot read `/root/` or `/var/lib/cerynixos-ai/`.

### 2. Process Operations
- **Tools:** `ps`, `kill`
- **Privilege:** Medium.
- **Restrictions:** Can only view and kill processes owned by the user session.

### 3. Package and Config Operations
- **Tools:** `nixos-rebuild`, `nix-env`
- **Privilege:** High (Requires Polkit/sudo).
- **Restrictions:** Must always trigger a configuration verification step before applying. `nixos-rebuild switch` must be executed with rollback hooks armed.

### 4. Service Control
- **Tools:** `systemctl_status`, `systemctl_restart`
- **Privilege:** High (Requires Polkit/sudo for system services, Low for user services).
- **Restrictions:** Cannot disable security services (e.g., firewall, auditd).

### 5. Desktop Automation
- **Tools:** `dbus_send`, `wayland_hook`
- **Privilege:** Medium.
- **Restrictions:** Sandboxed to the active user's session bus.

## Approval Modes
Determined by the enterprise policy fetched via the mock `fixtures/sample-policy.json`.
- **suggest_only:** The broker rejects execution and returns a safe payload for the UI to present to the user.
- **ask_before_act:** The broker initiates a UX prompt and blocks until confirmed.
- **auto_act:** The broker executes immediately, provided the tool is in the allow list.
