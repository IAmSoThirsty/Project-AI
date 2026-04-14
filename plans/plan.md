# Project-AI Constitutional LLM Implementation Plan

## Goal
Implement a GPT-2 style transformer architecture (~85M-124M parameters) with a custom tokenizer and training pipeline for the Constitutional LLM project.

## Research Summary
- **GPT-2 Small (124M)**: `n_layer=12`, `n_head=12`, `n_embd=768`, `vocab_size=50257`.
- **GPT-2 ~85M**: To reach ~85M parameters, we can use `n_layer=12`, `n_head=12`, `n_embd=512`.
- **Architecture**: Decoder-only transformer with causal self-attention, layer normalization before blocks (pre-norm), and weight tying between embedding and output layers.

## Approach
1.  **Tokenizer**: Implement a Byte-Pair Encoding (BPE) tokenizer or a wrapper around `tiktoken` for GPT-2 compatibility.
2.  **Model**: Build a clean, modular PyTorch implementation of the GPT-2 transformer.
3.  **Training**: Create a training script with support for basic data loading, optimization (AdamW), and checkpointing.

## Subtasks
1. Create `t:\Project-AI-main\model\tokenizer.py` — implement/wrap GPT-2 BPE tokenizer. (expected: file created) (verify: `python -c "import sys; sys.path.append('t:/Project-AI-main'); from model.tokenizer import Tokenizer; t = Tokenizer(); print(t.encode('Hello world'))"`)
2. Create `t:\Project-AI-main\model\transformer.py` — implement GPT-2 architecture (Config, Attention, MLP, Block, Transformer). (expected: file created) (verify: `python -c "import torch; from model.transformer import GPT, GPTConfig; m = GPT(GPTConfig(n_layer=2, n_head=2, n_embd=128)); print(sum(p.numel() for p in m.parameters()))"`)
3. Create `t:\Project-AI-main\train.py` — implement training loop, data loading (e.g., TinyShakespeare or OpenWebText), and logging. (expected: file created) (verify: `python t:\Project-AI-main\train.py --test_run`)

## Deliverables
| File Path | Description |
|-----------|-------------|
| `t:\Project-AI-main\model\tokenizer.py` | Tokenization logic |
| `t:\Project-AI-main\model\transformer.py` | GPT-2 Transformer architecture |
| `t:\Project-AI-main\train.py` | Training script |

## Evaluation Criteria
- Model initializes correctly with ~85M-124M parameters.
- Tokenizer correctly encodes/decodes text.
- Training script runs a single forward/backward pass without error.
