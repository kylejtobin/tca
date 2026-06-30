---
name: tca_required_reference_documentation
description: The co-located documentation strategy for TCA programs. How to place package-level README files and module companion docs so an LLM gets adjacent semantic context while the files stay human-readable on GitHub. Consult before writing or generating documentation for any package or module.
---

# TCA Program Documentation

## Overview
We use co-located, static `.mdx` files to provide LLMs with adjacent semantic context during development while ensuring human readability on GitHub and lean production deployments.

### Co-Located MDX Strategy
- **Package-level entry point:** Place a `README.mdx` in every package directory to explain the domain context and architecture. GitHub will automatically render this file when a human or agent navigates the folder.
- **Module-level expansion:** If a specific module requires deeper narrative, create a precisely named companion file right next to it (e.g., `execution.py` pairs with `execution.mdx`).
- **Strictly static content:** Use only standard Markdown syntax inside the `.mdx` files (no JSX) so they render correctly in GitHub's native viewer.

### Guidelines for LLM Documentation Generation
- **Start at the Entry Points:** Look at `__init__.py` and the main exports first to understand what the package exposes to the rest of the system before getting lost in the internal helper files.
- **Explain the "Why", Not the "What":** Do not translate the code into English line-by-line. Focus the narrative on the domain purpose, the architectural intent, and the problems the code is meant to solve.
- **Trace the Core Workflow:** Identify the primary data structures, base classes, or orchestration functions, and explain the main path of how data or execution flows through them.
- **Group by Concept:** Structure the explanation around logical features and domain concepts rather than just writing a mechanical, file-by-file summary.
- **Keep it Skimmable:** Use clear, hierarchical Markdown headings and bullet points so the context can be rapidly ingested by both human readers and future LLM sessions.
