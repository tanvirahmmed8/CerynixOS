{ config, pkgs, lib, ... }:

{
  environment.systemPackages = with pkgs; [
    (python3.withPackages (ps: with ps; [
      fastapi
      uvicorn
      pytest
      requests
    ]))
  ];

  # The mock fixtures directory needs to be mapped to the expected location
  # Since the workspace is e:\Test code\os (Windows), in a real NixOS environment this would be copied.
  # For the VM build, we link the mocks directory to /etc/cerynixos/mocks.
  environment.etc."cerynixos/mocks".source = ../../mocks;

  systemd.services.cerynix-action-broker = {
    description = "CerynixOS Action Broker";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];
    
    serviceConfig = {
      ExecStart = "${pkgs.python3}/bin/python ${./src/broker.py}";
      Restart = "always";
      RestartSec = "5s";
      
      # Security Posture: Run as dedicated user
      User = "cerynix-broker";
      Group = "cerynix-broker";
      RuntimeDirectory = "cerynixos"; # Creates /run/cerynixos for the UDS
      LogsDirectory = "cerynixos-audit"; # Creates /var/log/cerynixos-audit
    };
  };

  # Create the user
  users.users.cerynix-broker = {
    isSystemUser = true;
    group = "cerynix-broker";
  };
  users.groups.cerynix-broker = {};

  # Polkit / Sudoers rules for the broker to run specific commands as root
  security.sudo.extraRules = [
    {
      users = [ "cerynix-broker" ];
      commands = [
        { command = "/run/current-system/sw/bin/systemctl restart *"; options = [ "NOPASSWD" ]; }
        { command = "/run/current-system/sw/bin/nixos-rebuild *"; options = [ "NOPASSWD" ]; }
      ];
    }
  ];
}
