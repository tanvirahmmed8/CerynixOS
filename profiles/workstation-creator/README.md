# Creator Workstation Profile

## Purpose
Provides a tailored NixOS package set and configuration for content creators, designers, and video editors using CerynixOS.

## Main Components
- `default.nix`: Installs creative software (OBS, Blender, GIMP, Kdenlive) and configures the audio subsystem (PipeWire).

## Data Flow
Imported by `flake.nix` for target device configurations meant for creative workloads.

## Risks or Limits
- PipeWire is enabled and replaces PulseAudio/JACK. Ensure no legacy audio conflicts exist. Real-time scheduling (`rtkit`) is enabled for low-latency audio.
