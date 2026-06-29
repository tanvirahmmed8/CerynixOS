{ config, pkgs, ... }:

{
  environment.systemPackages = with pkgs; [
    # Media Editing
    obs-studio
    gimp
    inkscape
    kdenlive
    ffmpeg
    blender
    
    # Audio
    audacity
  ];

  # Enable sound (PipeWire is modern default for creators)
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    jack.enable = true;
  };
}
