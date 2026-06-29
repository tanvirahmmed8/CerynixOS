{ config, pkgs, ... }:

{
  # Core System Settings
  system.stateVersion = "24.05";
  
  # Bootloader (systemd-boot for generational rollbacks)
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  # Retain a sensible number of rollback generations
  boot.loader.systemd-boot.configurationLimit = 10;

  # Networking
  networking.hostName = "cerynixos";
  networking.networkmanager.enable = true;

  # Base Packages (Strictly minimal tools required for system health and action broker)
  environment.systemPackages = with pkgs; [
    git
    curl
    vim
    wget
    htop
    jq
  ];

  # Safe Defaults: Restrict SSH root login
  services.openssh = {
    enable = true;
    settings.PermitRootLogin = "no";
    settings.PasswordAuthentication = false;
  };

  # Immutable / Declarative enforcement
  # (Placeholder for read-only root or ephemeral / config if we go full erase-your-darlings)
  # fileSystems."/" = { ... }
}
