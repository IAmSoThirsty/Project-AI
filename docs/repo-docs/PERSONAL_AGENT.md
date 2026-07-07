# Project-AI Personal Agent

Project-AI now includes a small personal-agent mode. Its first active role is
Caregiver Scribe: learn the vault, learn the repo, and write navigation maps
back into Obsidian.

## Files

- `src/app/personal_agent.py` - implementation
- `config/personal_agent.json` - backend and path settings
- `config/personal_agent_instructions.md` - behavior instructions
- `data/personal_agent/` - runtime memory and chat logs
- `scripts/personal_agent.py` - direct launcher
- `wiki/_Scribe/Project-AI/` - generated Obsidian scribe notes and manifests

`data/personal_agent/` and `wiki/_Scribe/Project-AI/` are ignored by git because
they can contain private learned memory and generated navigation data.

## Run

From the repo root:

```powershell
py -3.12 .\scripts\personal_agent.py
```

Or through the Project-AI CLI:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m app.cli personal chat
```

## Scribe First

The configured Obsidian vault is `wiki`.

Initialize the scribe home:

```powershell
py -3.12 .\scripts\personal_agent.py scribe init
```

Absorb the vault structure first:

```powershell
py -3.12 .\scripts\personal_agent.py scribe absorb-vault
```

Then learn the Project-AI file terrain:

```powershell
py -3.12 .\scripts\personal_agent.py scribe learn-repo
```

The scribe writes:

- `wiki/_Scribe/Project-AI/00 Scribe Home.md`
- `wiki/_Scribe/Project-AI/Vault Navigation Map.md`
- `wiki/_Scribe/Project-AI/vault_manifest.jsonl`
- `wiki/_Scribe/Project-AI/Project-AI File Index.md`
- `wiki/_Scribe/Project-AI/repo_file_manifest.jsonl`

## Learn

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m app.cli personal learn fact "The user prefers direct answers."
py -3.12 -m app.cli personal learn preference "Use Python examples first."
py -3.12 -m app.cli personal learn goal "Build a useful private local agent."
py -3.12 -m app.cli personal memory
```

Interactive chat also supports:

```text
/learn fact text
/learn preference text
/learn goal text
/learn skill text
/remember text
/prefer text
/goal text
/memory
/forget memory-id
/training-export
```

## Local Model Backend

The default config expects LM Studio's OpenAI-compatible local server:

```text
http://localhost:1234/v1
```

For Ollama, edit `config/personal_agent.json`:

```json
{
  "backend": "ollama",
  "base_url": "http://localhost:11434",
  "model": "gemma3:4b"
}
```

Then start chat again.
