#                                           [2026-03-03 13:45]
#                                          Productivity: Active
# Sovereign AI Merge & Quantization Pipeline
# ------------------------------------------
#                                             Date: 2026-03-02 04:47
#                                             Status: Active
#                                             Productivity: Active

"""
Merges LoRA adapters with the base model and quantizes to GGUF (Q4_K_M)
for local deployment on Ryzen hardware.
"""

import os
from unsloth import FastLanguageModel


def merge_and_save_gguf(agent_name, lora_path, quantization="q4_k_m"):
    print(f"Merging and quantizing {agent_name}...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=lora_path,
        max_seq_length=2048,
        load_in_4bit=True,
    )

    output_dir = f"models/gguf/{agent_name}"
    os.makedirs(output_dir, exist_ok=True)

    model.save_pretrained_gguf(
        output_dir,
        tokenizer,
        quantization_method=quantization,
    )

    print(f"Successfully exported {agent_name} to {output_dir}")


if __name__ == "__main__":
    lora_model_path = "models/galahad_lora"
    if os.path.exists(lora_model_path):
        merge_and_save_gguf("galahad", lora_model_path)
    else:
        print(f"LoRA model not found at {lora_model_path}. Run training first.")
