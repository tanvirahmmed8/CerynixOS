# Changelog - Security Module

## 2026-06-29
- **Feature:** Initial Security Hardening Baseline
- **Changes:**
  - Implemented `cerynix-integrity` to hash models and verify plugin signatures.
  - Implemented `cerynix-identity` to generate TPM mock identities.
  - Enabled AppArmor and locked down the networking firewall in `default.nix`.
  - Defined the LUKS Full Disk Encryption baseline.
