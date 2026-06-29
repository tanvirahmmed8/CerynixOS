{ config, pkgs, ... }:

{
  environment.systemPackages = with pkgs; [
    # Container & Virtualization
    docker
    docker-compose
    
    # Dev utilities
    direnv
    tmux
    ripgrep
    fzf
    
    # Compilation & Languages (Basics)
    gcc
    gnumake
    python3
    nodejs
  ];

  # Enable Docker daemon
  virtualisation.docker.enable = true;

  # Developer environment variables or aliases could go here
  environment.variables = {
    EDITOR = "vim";
  };
}
