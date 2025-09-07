# Saskantinon

Tools and scaffolding for the **Saskan Lands** project: world-building utilities, data models, and game-support code.

**Scope**: This repo contains meta/tooling and supporting code for the Saskan Lands ecosystem. Core game logic may live in sibling packages as the project evolves.

---

## Features (current / planned)

- Map and timeline utilities for world-building
- Data schemas and loaders for locations, factions, ecology
- CLI scaffolding for generators and validators
- Project meta: contributing, code style, CI hooks (in progress)

---

## Installation

> Requires Python 3.11+.

Clone and install in editable mode:

```bash
git clone https://github.com/genuinemerit/saskan-app.git
cd saskan-app
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
````

> If you prefer Poetry or Hatch, see the project wiki for alternates (coming soon).

---

## Quick Start

List available CLI commands (if present):

```bash
saskan --help
```

Run tests (if configured):

```bash
pytest -q
```

Lint/format (if configured):

```bash
flake8 .
isort . --check
black . --check
```

---

## Project Background (short)

Set in a post-collapse world facing ecological failure, Saskan Lands explores recovery after the loss of natural pollinators.

Tools here support simulation and narrative systems tied to that premise.
For extended lore and design notes, see the project wiki (to be linked).

---

## Contributing

Contributions are welcome. Please read:

* [CONTRIBUTING.md](CONTRIBUTING.md)
* [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md)

Add yourself to [AUTHORS.md](AUTHORS.md) in your PR if you wish to be credited.

---

## Security

If you discover a vulnerability, **do not open a public issue**.
Follow [SECURITY.md](SECURITY.md) for private disclosure instructions.

---

## License

This project is licensed under the MIT License – see [LICENSE.md](LICENSE.md) for details.”

---

## Acknowledgments

See [AUTHORS.md](AUTHORS.md).
