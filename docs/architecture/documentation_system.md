# Documentation Strategy

## Overview

For technical documentation, prioritize Markdown in the `/docs/` directory. Use GitBook for user manuals and storytelling aspects. Avoid complex tools like Sphinx unless necessary.

## Documentation Approach

### Current Phase: Keep it Simple

- **Markdown in Repo:**
  - Place core docs in the root and `/docs/`:
    - `README.md`: Top-level overview, quickstart.
    - Convert `.rst` files to `.md` for consistency.
    - Include `RELEASE.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
    - Add topic pages in `/docs/` (e.g., `architecture.md`, `style.md`, `faq.md`).
  - Link documents via the `README.md`.

### Future Expansion: MkDocs and GitHub Pages

- **MkDocs Setup** (if a site is needed):
  - Create `mkdocs.yml` and use `/docs/` with Markdown.
  - Publish using GitHub Pages with a simple GitHub Action.
  - Convert any remaining `.rst` to `.md`.

### Advanced Needs: Sphinx

- **Sphinx Usage** (for Python API docs):
  - Maintain Markdown guides; Sphinx can read them via `myst-parser`.
  - Implement API autodoc and intersphinx if needed.
  - Publish using a Sphinx build Action on GitHub Pages.

## Minimal Configuration Examples

### MkDocs (Material)

```yaml
# mkdocs.yml
site_name: Saskan App Docs
theme:
  name: material
nav:
  - Home: index.md
  - Contributing: contributing.md
  - Release: release.md
  - Architecture: architecture.md
```

### Sphinx (Minimal)

```python
# docs/conf.py
project = "Saskan App"
extensions = ["myst_parser"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
html_theme = "sphinx_rtd_theme"
```

## Practical Advice

- **Standardize on Markdown:** Use GitHub as your primary doc host.
- **Centralize Documentation:** Keep everything in a single `/docs/` folder and link from the `README.md`.
- **Defer Site Generators:** Only consider them when navigation or API documentation becomes cumbersome.

## User Manual with GitBook

- **GitBook Integration:**
  - Ideal for crafting a user guide separate from technical documentation.
  - Integrates well with GitHub for seamless updates.
  - Suitable for storytelling and user-facing materials.

## Additional Tools

- **Storytelling and RPG Elements:**
  - Use Scrivener for narrative development.
  - Develop RPG content in World Anvil.
  - Create maps in Inkarnate, with support from Wonderdraft and GIMP.
  - Store graphics generated via DALL-E API in a `/draw/` folder.

By following this strategy, we can maintain a streamlined and effective documentation process tailored to both technical and user needs.
