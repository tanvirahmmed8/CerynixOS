{ config, pkgs, ... }:

let
  # The user will provide their own custom/finetuned model manually.
  # Just place your .gguf file at modules/ai-runtime/models/custom-model.gguf
  # Nix will automatically copy it into the ISO during the build.
  qwenModel = ./models/custom-model.gguf;

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
