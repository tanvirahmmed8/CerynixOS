{ config, pkgs, lib, ... }:

let
  diagScript = pkgs.writeScriptBin "cerynix-diag" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/cerynix_diag.py}
  '';
in
{
  environment.systemPackages = with pkgs; [
    diagScript
    (python3.withPackages (ps: with ps; [
      psutil
    ]))
  ];

  systemd.services.cerynix-health-agent = {
    description = "CerynixOS Local Health Agent";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];
    
    serviceConfig = {
      ExecStart = "${pkgs.python3}/bin/python ${./src/health_agent.py}";
      Restart = "always";
      RestartSec = "10s";
      
      # Health agent needs systemctl access to check service states
      # and needs to write to /var/lib/cerynixos-health.
      # Running as root for Milestone 1 to allow easy systemctl is-active and journalctl access.
      User = "root";
      StateDirectory = "cerynixos-health";
    };
  };
}
