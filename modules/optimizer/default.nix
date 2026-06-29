{ config, pkgs, lib, ... }:

let
  optimizerScript = pkgs.writeScriptBin "cerynix-optimizer" ''
    #!${pkgs.python3}/bin/python
    ${builtins.readFile ./src/engine.py}
  '';
in
{
  environment.systemPackages = [
    optimizerScript
  ];

  # The engine requires access to the profiles and hardware overrides.
  # We copy them to a known location in /etc so the script can read them.
  # Note: The engine.py script expects profiles.json in its __file__ directory, 
  # so in a real Nix setup we'd patch the path or map it. For Milestone 1, 
  # we simply place them in /etc and adjust our engine path logic if needed,
  # or rely on the script being executed from source for local dev.
  
  # Allow the Action Broker (cerynix-broker) to execute the optimizer via sudo without password
  security.sudo.extraRules = [
    {
      users = [ "cerynix-broker" ];
      commands = [
        { command = "/run/current-system/sw/bin/cerynix-optimizer *"; options = [ "NOPASSWD" ]; }
      ];
    }
  ];
}
