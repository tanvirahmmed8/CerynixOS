# Local Development Workflow

## 1. Prerequisites
- A Linux host (preferably NixOS, Ubuntu with Nix installed, or WSL2 with Nix).
- Flakes enabled in your local Nix configuration.

## 2. Building the Project
We use `nix flake` to define all outputs (VMs, ISOs, packages).

**To build the VM image for testing:**
```bash
nix build .#nixosConfigurations.cerynixos-vm.config.system.build.vm
```

**To build an installable ISO:**
```bash
nix build .#nixosConfigurations.cerynixos-iso.config.system.build.isoImage
```

## 3. Running Locally
To quickly boot the built VM and test changes without installing:
```bash
./result/bin/run-cerynixos-vm
```
*Note: The VM includes QEMU port forwarding to access local services via SSH or localhost if needed.*

## 4. Iterating on Services
When working on a specific CerynixOS service (e.g., `cerynix-action-broker`):
1. **Mock Remote Calls:** Ensure your service reads from `mocks/fixtures/` instead of reaching out to a network endpoint.
2. **Run Tests:** `nix flake check` runs all module and package-level tests.
3. **Log Collection:** Inside the VM, use standard `journalctl` to view structured logs emitted by your service:
   `journalctl -u cerynix-action-broker.service -f`

## 5. Rollback Testing
To test the core rollback mechanic during development:
1. Apply a broken configuration in the VM.
2. Trigger the healer or manually run `nixos-rebuild switch --rollback`.
3. Verify the previous generation is restored and working.
