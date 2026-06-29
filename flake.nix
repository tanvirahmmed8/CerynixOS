{
  description = "CerynixOS - Enterprise AI Operating System";

  inputs = {
    # Using the stable 24.05 channel for reproducible enterprise base
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }: {

    nixosConfigurations = {
      
      # 1. VM Configuration for local testing
      cerynixos-vm = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./modules/base
          ./modules/ai-runtime
          ./modules/action-broker
          ./modules/health
          ./modules/optimizer
          ./modules/self-healing
          ./modules/desktop
          ./modules/update-agent
          ./modules/plugin-runtime
          ./modules/security
          ./profiles/workstation-dev
          {
            # VM specific overrides
            virtualisation.vmVariant = {
              virtualisation.memorySize = 4096;
              virtualisation.cores = 4;
              virtualisation.qemu.options = [ "-m 4096" ];
            };
          }
        ];
      };

      # 2. ISO Installer Configuration
      cerynixos-iso = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
          ./modules/base
          ./modules/ai-runtime
          ./modules/action-broker
          ./modules/health
          ./modules/optimizer
          ./modules/self-healing
          ./modules/desktop
          ./modules/update-agent
          ./modules/plugin-runtime
          ./modules/security
          ./profiles/workstation-dev
        ];
      };

      # 3. Bare Metal Target (Reference for physical installs)
      cerynixos-baremetal = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./modules/base
          ./modules/ai-runtime
          ./modules/action-broker
          ./modules/health
          ./modules/optimizer
          ./modules/self-healing
          ./modules/desktop
          ./modules/update-agent
          ./modules/plugin-runtime
          ./modules/security
          ./profiles/workstation-dev
          # Hardware config would normally be included here via an import
          # e.g., ./hardware-configuration.nix
        ];
      };

    };

  };
}
