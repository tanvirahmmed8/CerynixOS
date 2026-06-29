{ config, pkgs, lib, ... }:

let
  healerScript = pkgs.writeScriptBin "cerynix-healer" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/healer.py}
  '';
  snapshotScript = pkgs.writeScriptBin "cerynix-snapshot" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/snapshot_manager.py}
  '';
in
{
  environment.systemPackages = [
    healerScript
    snapshotScript
  ];

  # Allow the Action Broker (cerynix-broker) to execute the healer and snapshot tools via sudo without password
  security.sudo.extraRules = [
    {
      users = [ "cerynix-broker" ];
      commands = [
        { command = "/run/current-system/sw/bin/cerynix-healer"; options = [ "NOPASSWD" ]; }
        { command = "/run/current-system/sw/bin/cerynix-snapshot *"; options = [ "NOPASSWD" ]; }
      ];
    }
  ];
}
