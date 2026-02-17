# Changelog

All notable changes to the Project AI Desktop application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-27

### Added

- Initial release of Project AI Desktop application
- Electron framework with React + TypeScript
- Material-UI design system
- Custom frameless window with title bar
- Sidebar navigation
- Dashboard screen with Triumvirate visualization
- Intent submission screen with real-time governance
- Audit log viewer with decision history
- TARL rules explorer with policy display
- Complete API integration with Governance Kernel
- Cross-platform build support (Windows, macOS, Linux)
- Production-ready configuration
- Custom hooks for API data fetching
- Reusable UI components (LoadingSpinner, ErrorMessage, VerdictBadge)
- Utility formatters for timestamps and data display
- Constants and configuration management
- TypeScript strict mode
- ESLint configuration

### Features

- **Triumvirate Dashboard**: Real-time kernel status and pillar monitoring
- **Intent Submission**: Interactive form with governance evaluation
- **Audit Trail**: Immutable log of all governance decisions
- **TARL Viewer**: Complete policy and rule explorer
- **Auto-Refresh**: Dashboard updates every 10 seconds
- **Dark Theme**: Professional governance aesthetic
- **Color-Coded Verdicts**: Visual distinction for Allow/Deny/Degrade
- **Pillar Visualization**: Galahad (Purple), Cerberus (Red), Codex Deus (Green)

### Security

- Context isolation enabled
- Node integration disabled
- Secure IPC communication
- TARL enforcement on all API calls

### Technical

- Electron 28
- React 18
- TypeScript 5
- Material-UI 5
- Vite 5
- Axios for HTTP requests
- electron-builder for distribution

[1.0.0]: https://github.com/project-ai/desktop/releases/tag/v1.0.0
