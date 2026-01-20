# UI Modernization Guide

## Overview

This document describes the modern UI enhancements added to Project-AI's interface, including glassmorphism, gradient designs, and improved accessibility.

## New Features

### 1. Modern Stylesheet (`styles_modern.qss`)

A completely redesigned stylesheet featuring:

#### Glassmorphism Design
- Semi-transparent panels with backdrop blur effects
- Layered depth with subtle borders
- Modern aesthetic aligned with current design trends

#### Enhanced Color Palette
- Dark mode optimized with gradient backgrounds
- Purple-blue gradient accents (#667eea → #764ba2)
- Danger gradients (red-blue: #fc466b → #3f5efb)
- Success gradients (teal-green: #11998e → #38ef7d)

#### Improved Components
- **Buttons**: Gradient backgrounds with hover states
- **Input Fields**: Glass panels with focus states
- **Tabs**: Modern rounded design with smooth transitions
- **Scroll Bars**: Minimalist, semi-transparent design
- **Cards**: Glassmorphic containers for content grouping

### 2. Accessibility Enhancements

- High contrast text (#e8eaf6 on dark backgrounds)
- Visible focus indicators (2px outline in brand color)
- Adequate touch targets (min 36px height for buttons)
- Consistent hover feedback across all interactive elements

### 3. Typography Improvements

- Modern font stack: Inter, Segoe UI, system fonts
- Clear hierarchy with title (18pt), subtitle (14pt), body (11pt)
- Weighted fonts (400 regular, 600 semi-bold, 700 bold)

## Usage

### Applying the Modern Theme

```python
from PyQt6.QtWidgets import QApplication
from pathlib import Path

app = QApplication([])

# Load modern stylesheet
style_path = Path(__file__).parent / "styles_modern.qss"
with open(style_path, "r") as f:
    app.setStyleSheet(f.read())
```

### Using CSS Classes

Apply custom classes to widgets using Qt properties:

```python
from PyQt6.QtWidgets import QWidget

# Glass panel
widget = QWidget()
widget.setProperty("class", "glass-panel")

# Card style
card = QWidget()
card.setProperty("class", "card")

# Elevated card
elevated_card = QWidget()
elevated_card.setProperty("class", "card-elevated")
```

### Button Styles

```python
from PyQt6.QtWidgets import QPushButton

# Default (gradient purple)
default_btn = QPushButton("Default")

# Danger button
danger_btn = QPushButton("Delete")
danger_btn.setProperty("class", "danger")

# Success button
success_btn = QPushButton("Save")
success_btn.setProperty("class", "success")
```

### Label Hierarchy

```python
from PyQt6.QtWidgets import QLabel

# Title
title = QLabel("Main Title")
title.setProperty("class", "title")

# Subtitle
subtitle = QLabel("Section Subtitle")
subtitle.setProperty("class", "subtitle")

# Body text (default)
body = QLabel("Regular text content")
```

## Design Principles

### 1. Visual Hierarchy
Clear distinction between primary, secondary, and tertiary UI elements through size, color, and weight.

### 2. Consistency
Uniform spacing (8px grid system), border-radius (8px standard, 16px for cards), and color application.

### 3. Feedback
All interactive elements provide visual feedback:
- Hover states (brightness +10%)
- Active/pressed states (brightness -10%, subtle shift)
- Focus indicators (outline)

### 4. Performance
- Lightweight gradients (2-3 stops max)
- CSS-based styling (no image assets for basic UI)
- Hardware-accelerated where possible

## Migration from Legacy Styles

### Replacing `styles.qss` with `styles_modern.qss`

1. **Backup current style**: Keep `styles.qss` for reference
2. **Update imports**: Change stylesheet path to `styles_modern.qss`
3. **Test components**: Verify all UI elements render correctly
4. **Adjust custom widgets**: Update any hardcoded colors/styles

### Compatibility Notes

- Both stylesheets can coexist
- Modern style is additive (doesn't break existing functionality)
- Can be toggled via user preferences

## Color Reference

### Primary Colors
- **Brand Purple**: #667eea
- **Brand Violet**: #764ba2
- **Background Dark**: #0a0e27
- **Background Mid**: #16213e

### Text Colors
- **Primary Text**: #e8eaf6
- **Secondary Text**: #b0bec5
- **Muted Text**: #90a4ae

### Semantic Colors
- **Success**: #11998e → #38ef7d
- **Danger**: #fc466b → #3f5efb
- **Warning**: #f7971e → #ffd200
- **Info**: #667eea → #764ba2

## Browser/Platform Support

### Desktop (PyQt6)
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (X11/Wayland)

### Web (CSS Export)
The stylesheet can be adapted for web use by:
1. Converting Qt-specific properties to standard CSS
2. Using CSS variables for color management
3. Adding vendor prefixes for gradients

## Future Enhancements

- [ ] Dark/Light mode toggle
- [ ] Accent color customization
- [ ] Animation framework integration
- [ ] Theme presets (Cyberpunk, Classic, Minimal)
- [ ] Color blind friendly modes
- [ ] High contrast mode
