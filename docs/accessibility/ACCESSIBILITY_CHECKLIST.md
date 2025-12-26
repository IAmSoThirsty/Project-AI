# Accessibility Checklist for PyQt GUI

This checklist provides a minimum accessibility baseline for the Leather Book PyQt GUI.

## Keyboard navigation
- [ ] All interactive controls reachable with Tab/Shift+Tab
- [ ] Logical focus order across panels
- [ ] Keyboard shortcuts documented and discoverable (Help menu)

## Screen reader compatibility
- [ ] All widgets have accessible names (`setAccessibleName`)
- [ ] Important non-text UI elements have accessible descriptions
- [ ] Semantic grouping using `QGroupBox` or `aria`-like hints

## Color & Contrast
- [ ] Ensure text contrast >= WCAG 2.1 AA for normal text
- [ ] Do not rely on color alone to convey information
- [ ] Provide high-contrast theme option (accessible.css or QSS variant)

## Font & Scaling
- [ ] Support system font scaling (Respect `QFontMetrics` and DPI)
- [ ] Ensure UI elements don't clip at 125%/150% scaling

## Focus indicators
- [ ] Visible focus ring for keyboard-focused controls
- [ ] Focus indicator colors are high contrast

## Accessibility testing
- [ ] Manual keyboard-only traversal test
- [ ] Screen reader smoke test (NVDA on Windows, VoiceOver on macOS)
- [ ] Automated checks for color contrast (axe-like tools for desktop are limited)

## Documentation
- [ ] Add a short accessibility page to docs with instructions for enabling high-contrast and keyboard shortcuts
- [ ] Provide guidance to QA on accessibility test cases
