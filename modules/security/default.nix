{ config, pkgs, lib, ... }:

let
  integrityScript = pkgs.writeScriptBin "cerynix-integrity" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/integrity_checker.py}
  '';
  identityScript = pkgs.writeScriptBin "cerynix-identity" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/identity_manager.py}
  '';
in
{
  environment.systemPackages = [
    integrityScript
    identityScript
  ];

  # ==========================================
  # HARDENING BASELINES
  # ==========================================

  # 1. Full Disk Encryption (LUKS) Baseline
  # This serves as the declarative standard for physical CerynixOS installs.
  # Note: Actually activating this requires matching hardware block devices,
  # so it is disabled for the generic ISO build.
  # boot.initrd.luks.devices."cryptroot" = {
  #   device = "/dev/nvme0n1p2"; # Stub
  #   preLVM = true;
  #   allowDiscards = true;
  # };

  # 2. AppArmor Enforcement
  # Globally enable AppArmor for mandatory access control.
  security.apparmor.enable = true;
  security.apparmor.killUnconfinedConfinables = false; # Soft fail for Milestone 1

  # 3. Network Hardening
  networking.firewall.enable = true;
  # Only allow SSH and strictly required ports. AI Runtime communicates over UDS locally.
  networking.firewall.allowedTCPPorts = [ 22 ];
  networking.firewall.allowPing = false;

  # 4. Strict Sudo Rules Review
  # We validate that `NOPASSWD` is strictly limited to isolated commands like `cerynix-update`
  # and `cerynix-plugin-runner`. We do NOT allow generic `NOPASSWD` access to bash or arbitrary binaries.
}
