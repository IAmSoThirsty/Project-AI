# WaterFall Native Engine

This crate is the first Rust foothold for Thirsty's WaterFall.

Current scope:
- tokenize and parse a small HTML fragment into a DOM-like tree
- derive a simple block-flow layout blueprint
- expose native engine identity so UTF can profile the runtime cleanly

Current non-goals:
- full HTML5 parsing
- CSS cascade and selector matching
- JavaScript execution
- GPU compositing

The point of this crate is to establish a real native rendering-engine spine inside the repository so UTF can see and reason about it while the desktop shell continues to evolve around it.
