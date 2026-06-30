{ config, pkgs, ... }:

let
  # We use a mocked model file here to prevent a massive 500MB download during ISO generation
  # In Milestone 2, the Control Plane will distribute the real .gguf file.
  qwenModel = pkgs.writeText "qwen2.5-0.5b-instruct-q4_k_m.gguf" "MOCK_GGUF_DATA_PLACEHOLDER";

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
