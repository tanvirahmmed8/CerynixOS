# Local Image Build and Flash Process

This document describes how to compile the CerynixOS base image into a bootable format using Nix flakes.

## Prerequisites
- A Linux system with Nix installed and flakes enabled.
- For VM testing: QEMU installed on your host.

## 1. Building the VM Image for Testing
To quickly test the OS without physical hardware, build the QEMU VM target:
```bash
nix build .#nixosConfigurations.cerynixos-vm.config.system.build.vm
```
This produces a `result` symlink in your directory.

To run the VM:
```bash
./result/bin/run-cerynixos-vm
```

## 2. Building the Bootable ISO
To create a live USB installer or test in a hypervisor that requires an ISO:
```bash
nix build .#nixosConfigurations.cerynixos-iso.config.system.build.isoImage
```
The resulting ISO file will be located in `./result/iso/`.

## 3. Flashing to a USB Drive
*Warning: This will destroy all data on the target drive.*

Identify your USB drive (e.g., `/dev/sdX` or `/dev/diskN`). Do **not** flash to your main hard drive.

**On Linux:**
```bash
sudo dd if=./result/iso/nixos-*.iso of=/dev/sdX bs=4M status=progress
sync
```

**On macOS:**
```bash
sudo dd if=./result/iso/nixos-*.iso of=/dev/diskN bs=4m status=progress
```

## 4. Rollback and Recovery Workflow
CerynixOS (being NixOS-based) retains previous generations in the boot menu.
If an update breaks the system:
1. Reboot the machine.
2. At the systemd-boot menu, select the previous working generation.
3. Once booted into the working state, make it the default by running:
   ```bash
   sudo nixos-rebuild switch --rollback
   ```
