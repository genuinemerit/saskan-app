# tox

## What tox is

A test automation tool for Python projects.

It creates isolated virtual environments and runs your test suite, linters, or other commands across multiple configurations.

Originally built to make sure a library works on many Python versions, but also handy for consistent “one command runs everything” QA.

## Typical use cases

Multi-Python testing

e.g. run pytest under Python 3.10, 3.11, 3.12 with one tox command.

Consistent QA pipeline

You define environments (lint, type, docs) and tox handles the virtualenv setup.

A CI system can just call tox instead of duplicating steps.

Local developer workflow

Instead of running make lint && make type && make test, a dev can just run tox.

## Why/why not for you right now

### Why not yet

You already use Poetry for dependency management and Makefile for QA orchestration.

You’re not shipping a library that needs testing across many Python versions.

CI is already wired up with GitHub Actions + pre-commit.

### Why later

If you decide you want a single tool that abstracts all the QA targets (instead of make), tox can do it.

If you want to guarantee tests pass on multiple Python versions locally before CI tells you, tox is a good fit.

## Takeaway

tox is basically a unified “run everything in fresh venvs” tool.

You don’t need it now — your Makefile + Poetry + GitHub Actions setup already covers your needs.

### Consider it later if:

You release this as a library and want to test against many Python versions.

You want CI and local QA to use exactly the same tox.ini config for repeatability.
