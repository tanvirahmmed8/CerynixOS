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
}
