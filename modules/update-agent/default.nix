{ config, pkgs, lib, ... }:

let
  updateAgentScript = pkgs.writeScriptBin "cerynix-update" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/update_agent.py}
  '';
  updateStatusScript = pkgs.writeScriptBin "cerynix-update-status" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/update_status.py}
  '';
in
{
  environment.systemPackages = [
    updateAgentScript
    updateStatusScript
  ];

  # Allow the Action Broker to trigger updates safely
  security.sudo.extraRules = [
    {
      users = [ "cerynix-broker" ];
      commands = [
        { command = "/run/current-system/sw/bin/cerynix-update *"; options = [ "NOPASSWD" ]; }
        { command = "/run/current-system/sw/bin/cerynix-update-status"; options = [ "NOPASSWD" ]; }
      ];
    }
  ];

  # Automated Daily Update Checks
  systemd.timers.cerynixos-update-check = {
    wantedBy = [ "timers.target" ];
    partOf = [ "cerynixos-update-check.service" ];
    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;
      RandomizedDelaySec = "1h"; # Jitter to prevent DDOSing our GitHub Pages
    };
  };

  systemd.services.cerynixos-update-check = {
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${updateAgentScript}/bin/cerynix-update --check";
    };
  };
}
