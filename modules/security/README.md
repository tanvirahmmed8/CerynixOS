# Security Hardening on Device

## Purpose
The `security` module enforces the system-wide baseline for CerynixOS. It provides both declarative OS protections (AppArmor, LUKS, Firewall) and active integrity checking logic.

## Main Components
- `src/integrity_checker.py`: (`cerynix-integrity`) verifies SHA256 hashes of the Local AI models and verifies plugin manifest signatures to prevent malware tampering.
- `src/identity_manager.py`: (`cerynix-identity`) mocks a hardware TPM enrollment flow, generating a secure `device_id` and x509 cert stub for the Control Plane (Milestone 2).
- `default.nix`: Declaratively turns on `apparmor` and `networking.firewall`, and defines the `boot.initrd.luks` standard for physical installs.
