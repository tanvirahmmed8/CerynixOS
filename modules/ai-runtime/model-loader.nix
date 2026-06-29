{ config, pkgs, ... }:

let
  # The Qwen 2.5 0.5B model is excellent for on-device tool calling with tiny footprint.
  # We use fetchurl to ensure it is downloaded at build-time and hashed.
  qwenModel = pkgs.fetchurl {
    url = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf";
    hash = "sha256-b040ab597cc6770e70461d5635839a89d7182ec35a96db4eeb4f7dd8178a3c89";
  };

  # Generate a JSON config for the Inference Manager to parse
  modelConfig = pkgs.writeText "model-config.json" (builtins.toJSON {
    default_model_path = "${qwenModel}";
    model_id = "qwen2.5-0.5b-instruct-q4_k_m";
    context_size = 4096;
    max_memory_mb = 1024;
    temperature = 0.1;
  });

in {
  # Symlink the model and config to a well-known path for the runtime to use
  environment.etc."cerynixos/ai/model-config.json".source = modelConfig;
}
