# Project Structure

## Directories

- `config/`: Configuration files (JSON, YAML, stored prompts).
- `data/`: Data storage, including datasets (`data/datasets`) and runtime artifacts.
- `docs/`: Documentation, guides, and reports.
  - `reports/`: Generated audit and status reports.
  - `internal/`: Internal design docs and summaries.
- `scripts/`: Operational scripts.
  - `demos/`: Demonstration scripts.
  - `launch/`: Batch/Shell launch scripts.
  - `maintenance/`: System verification and maintenance tools.
  - `tools/`: CLI tools and utilities.
- `src/`: Source code.
- `tests/`: Automated tests.
  - `manual/`: Manual test scripts.

## Key Scripts

- `scripts/quickstart.py`: Quick setup and check.
- `scripts/start_api.py`: Start the backend API.
- `scripts/tools/project_ai_cli.py`: Main CLI tool.
