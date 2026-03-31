#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from app.agents.codex_deus_maximus import create_codex

c = create_codex()
print(c.generate_gpt_oss("Hello, GPT‑OSS 1208!"))
