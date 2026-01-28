---
description: Integrate GPT‑OSS 1208 model into CodexDeusMaximus agent
---

## Steps to use the new GPT‑OSS 1208 capabilities

1. **Install required dependencies** (if not already present):

   ```
   pip install torch>=2.8.0 transformers>=4.53.0
   ```
   // turbo
   // This step can be auto‑run.

1. **Ensure the model files can be downloaded** – the first call to `generate_gpt_oss` will download the model from HuggingFace. Make sure you have internet access and sufficient disk space (~200 GB for the 120 B model).

1. **Instantiate the agent** in your Python code:

   ```python
   from app.agents.codex_deus_maximus import create_codex
   codex = create_codex(data_dir="data")
   ```

1. **Generate a response** using the new method:

   ```python
   prompt = "Explain the repository structure and suggest improvements."
   response = codex.generate_gpt_oss(prompt)
   print(response)
   ```

1. **Optional – integrate into existing workflows**:
   - Call `codex.generate_gpt_oss` wherever you currently invoke `run_schematic_enforcement` or other agent actions to augment the output with LLM‑generated insights.
   - Example:

     ```python
     report = codex.run_schematic_enforcement()
     insight = codex.generate_gpt_oss(f"Summarize the enforcement report: {report}")
     print(insight)
     ```

1. **Run a quick sanity check** (auto‑run):

   ```bash
   python - <<PY
   from app.agents.codex_deus_maximus import create_codex
   c = create_codex()
   print(c.generate_gpt_oss("Hello, GPT‑OSS 1208!"))
   PY
   ```
   // turbo
   // This command will execute the snippet and print the model’s reply.

---

**Notes**

- The model is lazy‑loaded; the first call may take several minutes.
- If you encounter out‑of‑memory errors, consider using a quantized version or a smaller model (e.g., `gpt-oss-20b`).
- All generated text is returned as a plain string; you can further process it or feed it back into the CognitionKernel.

---
