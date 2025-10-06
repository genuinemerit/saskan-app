# Saskantinon

Tools and scaffolding for the **Saskan Lands** project: world-building utilities, data models, and game-support code.

Note on naming: the package is `saskan`; “Saskantinon” refers to the broader project/world.

---

## Features (current / planned)

- Map and timeline utilities for world-building
- Data schemas and loaders for locations, factions, ecology
- CLI scaffolding for generators and validators
- Project meta: contributing, code style, CI hooks (in progress)

---

## Installation

> Requires Python 3.12.

Poetry (recommended):

```bash
poetry install
poetry run saskan --help
```

Virtualenv + pip (alternative):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

---

## Quick Start

CLI overview:

```bash
saskan --help
saskan version
saskan hello --name Alice
```

Run server and connect locally:

```bash
# Start server (defaults to 127.0.0.1:7777)
saskan start

# Connect client (same host/port by default)
saskan connect

# Custom host/port
saskan start -H 0.0.0.0 -p 8888
saskan connect -H 127.0.0.1 -p 8888
```

Dev shortcuts (Makefile):

```bash
make init                 # install deps
make run ARGS="version"   # run CLI via Poetry
make test                 # pytest -q
make format               # isort + black
make check                # format + lint + type + tests
```

---

## Environment

Defaults come from `saskan/infra/config/net.py` and can be overridden via env vars:

- `SASKAN_HOST`: server bind/target host (default `127.0.0.1`)
- `SASKAN_PORT`: server bind/target port (default `7777`)
- `SASKAN_LANG`: UI/CLI language (default `en-US`; supported: `en-US`, `es-ES`)

Examples:

```bash
export SASKAN_LANG=es-ES
export SASKAN_HOST=0.0.0.0 SASKAN_PORT=8888
```

Internationalization bundles live under `saskan/data/locales/*/messages.yaml`.

---

## Development

Tooling is configured in `pyproject.toml` and `Makefile`:

```bash
isort . --check
black . --check
mypy
pytest -q
```

See also: `docs/meta/linters_and_typechecks.md` for practical guidance.

---

## Architecture & Design

- High-level architecture: `docs/architecture/summary.md`
- ADRs (Architecture Decision Records): `docs/adr/`
- Message schemas: `saskan/infra/schema/*.json`

---

## Project Background (short)

Set in a post-collapse world facing ecological failure, Saskan Lands explores recovery after the loss of natural pollinators.

Tools here support simulation and narrative systems tied to that premise.
For extended lore and design notes, see the architecture docs above and the project wiki.

---

## Contributing

Contributions are welcome. Please read:

* `CONTRIBUTING.md`
* `CODE_OF_CONDUCT.md`

Add yourself to `AUTHORS.md` in your PR if you wish to be credited.

---

## Security

If you discover a vulnerability, **do not open a public issue**.
Follow `SECURITY.md` for private disclosure instructions.

---

## License

This project is licensed under the MIT License – see `LICENSE` for details.

---

## Acknowledgments

See `AUTHORS.md`.

---

## saskan-app

[![CI](https://img.shields.io/github/actions/workflow/status/genuinemerit/saskan-app/ci.yml?branch=develop)](https://github.com/genuinemerit/saskan-app/actions)
[![License](https://img.shields.io/github/license/genuinemerit/saskan-app)](https://github.com/genuinemerit/saskan-app/blob/develop/LICENSE)
[![Issues](https://img.shields.io/github/issues/genuinemerit/saskan-app)](https://github.com/genuinemerit/saskan-app/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/genuinemerit/saskan-app)](https://github.com/genuinemerit/saskan-app/pulls)

