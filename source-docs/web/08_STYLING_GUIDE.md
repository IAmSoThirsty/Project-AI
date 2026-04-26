---
type: styling-guide
module: web.styles
tags: [css, styling, design-system, responsive, accessibility]
created: 2026-04-20
status: production
related_systems: [component-library, nextjs-frontend]
stakeholders: [frontend-team, ux-team, design-team]
platform: web
dependencies: [css-modules, css-variables]
---

# Styling & Design System Guide

**Purpose:** Comprehensive styling guidelines for consistent, accessible, and maintainable UI  
**Architecture:** CSS Variables + Global Classes + Component-Specific Styles  
**Theme:** Tron-inspired dark theme with cyan/magenta accents

---

## Table of Contents

1. [Design System Overview](#design-system-overview)
2. [CSS Variables](#css-variables)
3. [Global Styles](#global-styles)
4. [Component Styling](#component-styling)
5. [Responsive Design](#responsive-design)
6. [Animations](#animations)
7. [Accessibility](#accessibility)
8. [Best Practices](#best-practices)

---

## Design System Overview

### Visual Identity

**Theme:** Tron-inspired cyberpunk aesthetic  
**Primary Colors:** Cyan (#00d4ff), Magenta (#ff00ff)  
**Typography:** System fonts with monospace accents  
**Layout:** Card-based with glassmorphism effects

### Design Principles

1. **Consistency** - Unified visual language across all components
2. **Accessibility** - WCAG 2.1 AA compliance minimum
3. **Responsiveness** - Mobile-first responsive design
4. **Performance** - Minimal CSS, optimized animations
5. **Maintainability** - Reusable classes, CSS variables

---

## CSS Variables

**File:** `styles/globals.css`

### Color System

```css
:root {
  /* Primary Colors */
  --primary: #00d4ff;           /* Tron cyan */
  --primary-dark: #0099cc;      /* Darker cyan */
  --primary-light: #33ddff;     /* Lighter cyan */
  
  /* Secondary Colors */
  --secondary: #ff00ff;         /* Magenta */
  --secondary-dark: #cc00cc;    /* Darker magenta */
  --secondary-light: #ff33ff;   /* Lighter magenta */
  
  /* Accent Colors */
  --accent: #00ff88;            /* Success green */
  --accent-dark: #00cc6a;       /* Darker green */
  
  /* Status Colors */
  --success: #00ff88;           /* Green */
  --warning: #ffaa00;           /* Orange */
  --error: #ff4444;             /* Red */
  --info: #00d4ff;              /* Cyan */
  
  /* Backgrounds */
  --bg-dark: #0a0a0f;           /* Page background */
  --bg-card: #1a1a2e;           /* Card background */
  --bg-hover: #252540;          /* Hover background */
  --bg-active: #2d2d50;         /* Active background */
  
  /* Text Colors */
  --text-primary: #ffffff;      /* Primary text */
  --text-secondary: #a0a0a0;    /* Secondary text */
  --text-muted: #606060;        /* Muted text */
  
  /* Borders */
  --border-color: rgba(0, 212, 255, 0.3);  /* Primary border */
  --border-hover: rgba(0, 212, 255, 0.6);  /* Hover border */
  
  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.7);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.4);
}
```

### Typography

```css
:root {
  /* Font Families */
  --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  --font-mono: 'Courier New', Courier, monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;       /* 12px */
  --text-sm: 0.875rem;      /* 14px */
  --text-base: 1rem;        /* 16px */
  --text-lg: 1.125rem;      /* 18px */
  --text-xl: 1.25rem;       /* 20px */
  --text-2xl: 1.5rem;       /* 24px */
  --text-3xl: 1.875rem;     /* 30px */
  --text-4xl: 2.25rem;      /* 36px */
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Spacing

```css
:root {
  /* Spacing Scale */
  --spacing-0: 0;
  --spacing-1: 0.25rem;     /* 4px */
  --spacing-2: 0.5rem;      /* 8px */
  --spacing-3: 0.75rem;     /* 12px */
  --spacing-4: 1rem;        /* 16px */
  --spacing-5: 1.25rem;     /* 20px */
  --spacing-6: 1.5rem;      /* 24px */
  --spacing-8: 2rem;        /* 32px */
  --spacing-10: 2.5rem;     /* 40px */
  --spacing-12: 3rem;       /* 48px */
  --spacing-16: 4rem;       /* 64px */
}
```

### Border Radius

```css
:root {
  /* Border Radius */
  --radius-sm: 0.25rem;     /* 4px */
  --radius-md: 0.5rem;      /* 8px */
  --radius-lg: 0.75rem;     /* 12px */
  --radius-xl: 1rem;        /* 16px */
  --radius-full: 9999px;    /* Pill shape */
}
```

### Transitions

```css
:root {
  /* Transition Durations */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  
  /* Transition Easing */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Global Styles

### Base Styles

```css
/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-primary);
  background: var(--bg-dark);
  min-height: 100vh;
  overflow-x: hidden;
}
```

### Card Component

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-md);
  transition: all var(--duration-normal) var(--ease-in-out);
}

.card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  transform: translateY(-2px);
}
```

### Button Component

```css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-in-out);
  outline: none;
}

.button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.4);
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Button Variants */
.button-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.button-secondary {
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--primary);
}

.button-secondary:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--primary-light);
}

.button-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.button-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
```

### Input Component

```css
.input {
  width: 100%;
  padding: var(--spacing-3);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  outline: none;
  transition: all var(--duration-normal) var(--ease-in-out);
}

.input::placeholder {
  color: var(--text-muted);
}

.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-error {
  border-color: var(--error);
}
```

### Badge Component

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.badge-success {
  background: rgba(0, 255, 136, 0.2);
  color: var(--success);
  border: 1px solid var(--success);
}

.badge-info {
  background: rgba(0, 212, 255, 0.2);
  color: var(--info);
  border: 1px solid var(--info);
}

.badge-warning {
  background: rgba(255, 170, 0, 0.2);
  color: var(--warning);
  border: 1px solid var(--warning);
}

.badge-error {
  background: rgba(255, 68, 68, 0.2);
  color: var(--error);
  border: 1px solid var(--error);
}
```

### Error Message

```css
.error-message {
  display: block;
  margin-top: var(--spacing-2);
  font-size: var(--text-sm);
  color: var(--error);
}
```

---

## Component Styling

### Layout Classes

```css
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--spacing-4);
}

.container-sm {
  max-width: 640px;
}

.container-md {
  max-width: 768px;
}

.container-lg {
  max-width: 1024px;
}
```

### Grid System

```css
.grid {
  display: grid;
  gap: var(--spacing-6);
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

/* Responsive Grid */
@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
```

### Flexbox Utilities

```css
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.items-start {
  align-items: flex-start;
}

.items-end {
  align-items: flex-end;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-start {
  justify-content: flex-start;
}

.justify-end {
  justify-content: flex-end;
}

.gap-2 {
  gap: var(--spacing-2);
}

.gap-4 {
  gap: var(--spacing-4);
}

.gap-6 {
  gap: var(--spacing-6);
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Breakpoints */
/* xs: 0-639px (default) */
/* sm: 640px+ */
/* md: 768px+ */
/* lg: 1024px+ */
/* xl: 1280px+ */
```

### Responsive Classes

```css
/* Hide on mobile, show on tablet+ */
@media (max-width: 767px) {
  .hidden-mobile {
    display: none;
  }
}

/* Hide on desktop, show on mobile */
@media (min-width: 768px) {
  .hidden-desktop {
    display: none;
  }
}

/* Responsive text sizes */
.text-responsive-lg {
  font-size: var(--text-xl);
}

@media (min-width: 768px) {
  .text-responsive-lg {
    font-size: var(--text-2xl);
  }
}

@media (min-width: 1024px) {
  .text-responsive-lg {
    font-size: var(--text-3xl);
  }
}
```

### Mobile-First Example

```css
/* Mobile (default) */
.dashboard {
  padding: var(--spacing-4);
}

/* Tablet */
@media (min-width: 768px) {
  .dashboard {
    padding: var(--spacing-6);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .dashboard {
    padding: var(--spacing-8);
  }
}
```

---

## Animations

### Loading Spinner

```css
.loading {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

### Pulse Animation

```css
.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

### Fade In

```css
.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
```

### Slide Up

```css
.slide-up {
  animation: slideUp var(--duration-normal) var(--ease-out);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Glow Effect

```css
.glow {
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
  }
  to {
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
  }
}
```

---

## Accessibility

### Focus Styles

```css
/* Remove default outline, add custom focus */
*:focus {
  outline: none;
}

*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Button focus */
.button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.4);
}

/* Input focus */
.input:focus-visible {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
}
```

### Screen Reader Only

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Skip to Content

```css
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--primary);
  color: white;
  padding: var(--spacing-3) var(--spacing-6);
  z-index: 100;
  transition: top var(--duration-fast);
}

.skip-to-content:focus {
  top: 0;
}
```

### High Contrast Mode

```css
@media (prefers-contrast: high) {
  :root {
    --primary: #00ffff;
    --text-primary: #ffffff;
    --bg-dark: #000000;
    --border-color: #ffffff;
  }
}
```

---

## Best Practices

### 1. Use CSS Variables

**❌ Bad (hardcoded values):**
```css
.button {
  color: #00d4ff;
  padding: 12px 24px;
}
```

**✅ Good (CSS variables):**
```css
.button {
  color: var(--primary);
  padding: var(--spacing-3) var(--spacing-6);
}
```

### 2. Mobile-First Responsive

**❌ Bad (desktop-first):**
```css
.element {
  width: 1000px;
}

@media (max-width: 768px) {
  .element {
    width: 100%;
  }
}
```

**✅ Good (mobile-first):**
```css
.element {
  width: 100%;
}

@media (min-width: 768px) {
  .element {
    width: 1000px;
  }
}
```

### 3. Semantic Class Names

**❌ Bad (presentational):**
```css
.blue-text {
  color: blue;
}

.big-padding {
  padding: 40px;
}
```

**✅ Good (semantic):**
```css
.status-success {
  color: var(--success);
}

.card-content {
  padding: var(--spacing-6);
}
```

### 4. Avoid !important

**❌ Bad:**
```css
.button {
  color: red !important;
}
```

**✅ Good (increase specificity):**
```css
.button.button-error {
  color: var(--error);
}
```

### 5. Use rem/em for Scalability

**❌ Bad (px for fonts):**
```css
.text {
  font-size: 16px;
}
```

**✅ Good (rem for fonts):**
```css
.text {
  font-size: var(--text-base);  /* 1rem = 16px */
}
```

---

## Dark Mode Support (Future)

```css
/* Light mode */
[data-theme="light"] {
  --bg-dark: #ffffff;
  --bg-card: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #606060;
}

/* Dark mode (default) */
[data-theme="dark"] {
  --bg-dark: #0a0a0f;
  --bg-card: #1a1a2e;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
}

/* Respect system preference */
@media (prefers-color-scheme: light) {
  :root {
    --bg-dark: #ffffff;
    --bg-card: #f5f5f5;
    --text-primary: #000000;
    --text-secondary: #606060;
  }
}
```

---

## Related Documentation

- [Component Library](./06_COMPONENT_LIBRARY.md)
- [React Frontend](./02_REACT_FRONTEND.md)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Frontend Team / UX Team  
**Review Cycle:** Quarterly
