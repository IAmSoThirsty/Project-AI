---
description: "Use when editing React UI code in TSX/JSX files. Enforces component structure, accessibility, and testability patterns."
name: "Frontend React Standards"
applyTo: "**/*.{tsx,jsx}"
---

# Frontend React Standards

- Prefer function components and explicit prop interfaces.
- Keep components small and focused; split files when a component exceeds one primary responsibility.
- Use semantic HTML and include accessible labels for all interactive controls.
- Avoid inline anonymous callbacks in deeply repeated render paths when this harms readability or performance.
- Write or update tests for behavior changes in component logic.
- Reuse established project patterns before introducing new state or styling conventions.
