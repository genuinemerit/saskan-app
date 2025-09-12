# Internationalization (i18n) Authoring Guide

This document summarizes conventions and practices for adding or editing
localized strings in the Saskan project. It codifies decisions from ADR-0014
(Handshake & Activation), ADR-0016 (UX shells), and the *First Splash* design.

---

## Key Format

* Keys are **lowercase, dotted path** identifiers.
* Regex rule: `^[a-z0-9]+(\.[a-z0-9]+)*$`
* No spaces, capitals, underscores, or dashes.

### Examples

* `system.welcome`
* `system.reject`
* `msg.handshake.welcome`
* `ui.splash.title`
* `ui.menu.quit`

---

## Namespaces

Use namespaces to group related strings:

| Namespace | Purpose                                     | Examples                       |
|-----------|---------------------------------------------|--------------------------------|
| `system.*`| Server lifecycle & handshake outcomes       | `system.welcome`, `system.reject` |
| `msg.*`   | Protocol/session messages                   | `msg.handshake.welcome`        |
| `ui.*`    | CLI / PySide UI strings                     | `ui.splash.title`, `ui.menu.quit` |
| `err.*`   | Application errors not tied to handshake    | `err.invalid_input`            |
| `log.*`   | Log templates (if user-visible)             | `log.server.ready`             |

---

## Locale Policy

* Supported locales: `en-US`, `es-ES`.
* Default: `en-US`.
* Selection: via environment variable `SASKAN_LANG`.
* `en-EN` is **not valid**.

---

## File Layout

Localized values live under:

```text
saskan/data/locales/en-US/*.json
saskan/data/locales/es-ES/*.json

````

Each file is a flat JSON object mapping keys to strings.

```json
{
  "ui.splash.title": "Welcome to Saskan",
  "ui.splash.hint.quit": "Press Q or select File → Quit"
}
````

---

## Authoring Rules

1. **Never hard-code** user-facing strings in CLI, PyGame, or PySide code.
   Always reference an i18n key.
2. Add the new key to both `en-US` and `es-ES`.
3. Prefer short, descriptive key paths (`ui.menu.quit` not `ui.menu.quit_button_label`).
4. Use existing namespaces; introduce new ones only if justified in ADRs.

---

## Review & CI

* New pull requests must pass i18n tests:

  * All keys conform to regex.
  * No `en-EN` references.
* Linting/pre-commit hooks enforce this.
* Reviewers should verify that:

  * Added strings exist in all supported locales.
  * Call sites reference keys, not raw strings.

---

## Examples in Practice

### CLI / PySide

```python
from saskan.i18n import t

print(t("ui.splash.title"))
```

### Handshake message

```json
{
  "id": "uuid",
  "ver": "1",
  "name": "msg.handshake.welcome",
  "audience": "user",
  "severity": "info",
  "payload": {}
}
```

---

## References

* ADR-0014: Startup, Handshake, and Session Activation
* ADR-0016: UX Shells and Interactions
* Feature: First Splash

This gives contributors a one-page rulebook: what the keys look like, where they live, and how to use them.
