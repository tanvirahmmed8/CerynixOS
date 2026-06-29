{ config, pkgs, lib, ... }:

{
  imports = [
    ./model-loader.nix
  ];

  # We use llama-cpp as the default inference engine
  environment.systemPackages = with pkgs; [
    llama-cpp
    
    # Optional accelerated path for high-end GPUs (e.g. Nvidia)
    # vllm
    
    # Python environment with dependencies for our inference manager
    (python3.withPackages (ps: with ps; [
      fastapi
      uvicorn
      requests
      psutil
      sqlite
    ]))
  ];

  # Systemd service for the Inference Manager
  systemd.services.cerynix-inference-manager = {
    description = "CerynixOS Local AI Inference Manager";
    wantedBy = [ "multi-user.target" ];
    after = [ "network.target" ];
    
    serviceConfig = {
      ExecStart = "${pkgs.python3}/bin/python ${./src/inference_manager.py}";
      Restart = "always";
      RestartSec = "5s";
      # Run as an unprivileged dynamic user
      DynamicUser = true;
      StateDirectory = "cerynixos-ai"; # /var/lib/cerynixos-ai
    };
  };
}
