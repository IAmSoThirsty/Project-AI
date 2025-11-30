# Documentation

Project-AI documentation is organized into two main sections to keep the repository root clean and improve navigation.

## Directory Structure

### `docs/overview/`

Primary documentation, architecture guides, and user-facing quick-start materials:

- **AI_PERSONA_FOUR_LAWS.md** — Asimov's Laws framework and ethical decision-making
- **AI_PERSONA_IMPLEMENTATION.md** — Persona system architecture and state management
- **LEATHER_BOOK_ARCHITECTURE.md** — PyQt6 UI architecture and design patterns
- **LEATHER_BOOK_README.md** — Leather Book interface overview
- **LEATHER_BOOK_UI_COMPLETE.md** — UI completion status and component reference
- **DESKTOP_APP_QUICKSTART.md** — Quick-start guide for desktop application
- **DESKTOP_APP_README.md** — Desktop app features and setup
- **IMAGE_GENERATION_QUICKSTART.md** — Image generation features and usage
- **IMAGE_GENERATION_RESTORATION.md** — Image generation system restoration notes
- **PROGRAM_SUMMARY.md** — Complete architecture and program summary
- **INTEGRATION_GUIDE.md** — Integration points and component coupling
- **INTEGRATION_SUMMARY.md** — Integration summary and API reference
- **IMPLEMENTATION_COMPLETE.md** — Implementation completion status
- **INFRASTRUCTURE.md** — Infrastructure and deployment architecture

### `docs/notes/`

Auxiliary notes, session reports, test results, and reference materials:

- Session and completion summaries
- Test reports and coverage reports
- Fixes and improvements audit logs
- Feature summaries and branch notes
- Quick reference guides and troubleshooting

## Key Files at Repository Root

- **README.md** — Primary entry point (kept at root per GitHub convention)
- **PROGRAM_SUMMARY.md** — Also available in docs/overview/ for reference
- **pyproject.toml**, **requirements.txt** — Dependency and project configuration
- **Dockerfile**, **docker-compose.yml** — Container configuration
- **src/**, **tests/**, **web/** — Source code and test suites

## Navigation Tips

- Start with [README.md](../README.md) for project overview
- Review [docs/overview/PROGRAM_SUMMARY.md](overview/PROGRAM_SUMMARY.md) for complete architecture
- Check [docs/overview/DESKTOP_APP_QUICKSTART.md](overview/DESKTOP_APP_QUICKSTART.md) to run the app locally
- See [docs/overview/LEATHER_BOOK_ARCHITECTURE.md](overview/LEATHER_BOOK_ARCHITECTURE.md) for UI implementation details

## Document Cross-References

Internal links use relative paths. When a document is moved from root to `docs/overview/` or `docs/notes/`, relative links like `[link](../OTHER_FILE.md)` point back to the root if needed.

---

Last updated: November 2025
