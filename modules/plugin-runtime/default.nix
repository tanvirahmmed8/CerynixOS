{ config, pkgs, lib, ... }:

let
  pluginManagerScript = pkgs.writeScriptBin "cerynix-plugin-manager" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/plugin_manager.py}
  '';
  pluginRunnerScript = pkgs.writeScriptBin "cerynix-plugin-runner" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/plugin_runner.py}
  '';
in
{
  # Create a dedicated, unprivileged user for running plugins securely
  users.users.cerynix-plugin-user = {
    isSystemUser = true;
    group = "nogroup";
    description = "Isolated CerynixOS Plugin Runtime User";
  };

  environment.systemPackages = [
    pluginManagerScript
    pluginRunnerScript
  ];

  # Allow the Action Broker to manage plugins (runs as root/default)
  security.sudo.extraRules = [
    {
      users = [ "cerynix-broker" ];
      commands = [
        { command = "/run/current-system/sw/bin/cerynix-plugin-manager *"; options = [ "NOPASSWD" ]; }
      ];
    }
    {
      users = [ "cerynix-broker" ];
      runAs = "cerynix-plugin-user";
      commands = [
        { command = "/run/current-system/sw/bin/cerynix-plugin-runner *"; options = [ "SETENV" "NOPASSWD" ]; }
      ];
    }
  ];
}
