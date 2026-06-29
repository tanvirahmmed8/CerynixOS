# Self-Healing Scenarios (v1)

CerynixOS v1 supports automated detection and targeted recovery for the following five scenarios:

## 1. Failed Update Rollback (Guided)
- **Trigger**: System boot fails or post-update verification tests fail.
- **Action**: Proposes a `nixos-rebuild switch --rollback` to the last known-good generation. Requires user/CerynixAI approval.

## 2. Broken User Config (Guided)
- **Trigger**: Malformed JSON/YAML in `~/.config/cerynixos`.
- **Action**: Proposes restoring from the last backup managed by `snapshot_manager.py`.

## 3. Common Service Restart (Automatic)
- **Trigger**: Health Agent detects `cerynix-action-broker` or `cerynix-inference-manager` is inactive.
- **Action**: Automatically issues `systemctl restart <service>` and logs the event.

## 4. Config Drift Detection (Guided)
- **Trigger**: A managed file in `/etc/cerynixos` was modified outside of Nix.
- **Action**: Suggests running `nixos-rebuild switch` to snap the system back to its declarative state.

## 5. Storage Pressure Cleanup (Guided)
- **Trigger**: Disk usage on `/nix/store` exceeds 90%.
- **Action**: Suggests running `nix-collect-garbage -d` to free up space. Requires user/CerynixAI approval to prevent accidental deletion of cached dev environments.
