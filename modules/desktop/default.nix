{ config, pkgs, lib, ... }:

let
  uiServerScript = pkgs.writeScriptBin "cerynix-ui-server" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/ui_server.py}
  '';
  voiceStubScript = pkgs.writeScriptBin "cerynix-voice-stub" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/voice_stub.py}
  '';
in
{
  # 1. Select GNOME as the desktop base
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;
  
  # 2. Basic aesthetics and font defaults
  fonts.packages = with pkgs; [
    inter
    jetbrains-mono
  ];

  # 3. Expose the UI and Voice components globally
  environment.systemPackages = with pkgs; [
    uiServerScript
    voiceStubScript
    gnome.gnome-tweaks
  ];
  
  # Note for Milestone 1: We start the UI server via a systemd user service 
  # or rely on the user to run `cerynix-ui-server` manually for testing the Web UI mockup.
}
