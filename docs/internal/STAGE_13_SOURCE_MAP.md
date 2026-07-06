# Stage 13 CLI Source Map

| Source | SHA-256 | Disposition |
|---|---|---|
| `T:\00-Active\Project-AI-main\agent_playbook\src\agent_playbook\cli.py` | `a1ec8b7096f3b9b16dd9caf1a1a08dd13a24c095c4f54603bf2818fbaff041f4` | Typer/operator reference; direct subprocess and internal governance behavior rejected |
| `T:\00-Active\Project-AI-main\src\app\interfaces\cli\main.py` | `41be533ac99624e01e995b61ec1e98cbb82e2d78e8b8d7798ae455b044a37c7b` | Governance-routing intent retained through API-only boundary |
| `T:\00-Active\Project-AI-main\src\app\cli.py` | `2cefe41794c72315d6b5e46f7dbf864043bcc68883a855c79a077adc05db9450` | Command grouping reference; placeholder commands and release version rejected |
| `T:\00-Active\Project-AI-main\engines\sovereign_war_room\cli.py` | `d40c141d4ff82352800dbad1afa9a3a50194897acb05b6f66ce6dcb30681a72d` | Scenario UI reference; direct actuation rejected |

The rebuilt CLI is a new implementation. It is intentionally narrower than
the legacy surfaces and cannot import or instantiate AI-side authority.
