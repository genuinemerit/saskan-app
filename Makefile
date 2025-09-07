# Makefile — Saskan
# Usage: `make <target>` or `make <target> ARGS="..."`
# GitFlow-aware: adds guards + release/hotfix helpers while preserving existing targets.

SHELL := bash
# Run help as the default function
.DEFAULT_GOAL := help
PACKAGE := saskan
POETRY := poetry

# --- Helpers ---------------------------------------------------------------

# Run inside the Poetry venv
PRUN = $(POETRY) run

# Fail if the working tree isn't clean (used by guarded targets)
git_clean := test -z "$$(git status --porcelain)"

# Current branch helper (evaluated at parse; in some targets we recompute at runtime)
BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(none)")

# Print section headers
define header
	@printf "\n\033[1;34m==> %s\033[0m\n" $(1)
endef

# --- Guards ----------------------------------------------------------------

.PHONY: require-clean require-main require-develop require-release-branch require-hotfix-branch
require-clean:
	@$(git_clean) || { echo "✗ Working tree not clean. Commit/stash first."; exit 1; }

require-main:
	@if [ "$(BRANCH)" != "main" ]; then echo "✗ Must run on 'main' (current: $(BRANCH))"; exit 1; fi

require-develop:
	@if [ "$(BRANCH)" != "develop" ]; then echo "✗ Must run on 'develop' (current: $(BRANCH))"; exit 1; fi

require-release-branch:
	@if ! echo "$(BRANCH)" | grep -Eq '^release/[0-9]+\.[0-9]+\.[0-9]+$$'; then \
	  echo "✗ Must run on 'release/x.y.z' branch (current: $(BRANCH))"; exit 1; fi

require-hotfix-branch:
	@if ! echo "$(BRANCH)" | grep -Eq '^hotfix/[0-9]+\.[0-9]+\.[0-9]+$$'; then \
	  echo "✗ Must run on 'hotfix/x.y.z' branch (current: $(BRANCH))"; exit 1; fi

# --- Core ------------------------------------------------------------------

.PHONY: init
init:  ## Install / sync dependencies (uses pyproject.toml + poetry.lock)
	$(call header,Install / sync deps)
	$(POETRY) install

.PHONY: lock
lock:  ## Recreate lockfile and sync env (use when deps change)
	$(call header,Regenerate lockfile & install)
	$(POETRY) lock
	$(POETRY) install

.PHONY: lint
lint:  ## Lint: isort --check + black --check (fast)
	$(call header,isort --check-only)
	$(PRUN) isort . --check-only
	$(call header,Black --check)
	$(PRUN) black . --check

.PHONY: format
format:  ## Format: isort + black (modifies files)
	$(call header,isort)
	$(PRUN) isort .
	$(call header,Black)
	$(PRUN) black .

.PHONY: type
type:  ## Type-check with mypy
	$(call header,mypy)
	$(PRUN) mypy

.PHONY: test
test:  ## Run tests (quiet)
	$(call header,pytest)
	$(PRUN) pytest -q -p no:warnings

.PHONY: cov
cov:  ## Coverage: run tests with coverage + report (text + optional HTML)
	$(call header,coverage run)
	$(PRUN) coverage run -m pytest
	$(call header,coverage report)
	$(PRUN) coverage report -m
	@echo "HTML report: htmlcov/index.html (generate with 'make cov-html')"

.PHONY: cov-html
cov-html:  ## Generate HTML coverage report
	$(PRUN) coverage html
	@echo "Open ./htmlcov/index.html"

.PHONY: run
run:  ## Run the CLI (pass extra args via ARGS="...")
	$(call header,CLI)
	$(PRUN) $(PACKAGE) $(ARGS)

.PHONY: clean
clean:  ## Clean caches, build artifacts, coverage, pyc, etc.
	$(call header,Clean caches & artifacts)
	@rm -rf .pytest_cache .mypy_cache htmlcov dist build \
		coverage.xml .coverage
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -delete

# --- Git hooks / QA bundles -----------------------------------------------

.PHONY: hooks
hooks:  ## Install pre-commit hooks
	$(call header,Install pre-commit hooks)
	$(POETRY) add --group dev pre-commit --quiet || true
	$(PRUN) pre-commit install

.PHONY: fix
fix:  ## Run all pre-commit hooks on the whole repo
	$(call header,pre-commit run --all-files)
	$(PRUN) pre-commit run --all-files

.PHONY: check
check: format lint type test ## Full QA gate: lint, type, tests

# --- Build / package -------------------------------------------------------

.PHONY: build
build:  ## Build wheel + sdist
	$(call header,Build dist)
	$(POETRY) build

# Convenience for CI entrypoints
.PHONY: ci-pr ci-tag
ci-pr: check            ## CI: run PR checks
ci-tag: check build     ## CI: on tag builds, run checks + build artifacts

# --- Version helpers -------------------------------------------------------

# Current version from Poetry (fast; no python needed)
VERSION := $(shell $(POETRY) version -s 2>/dev/null || echo "0.0.0")

.PHONY: version
version:  ## Show current project version (from Poetry)
	@echo $(VERSION)

# Bump version via Poetry: `make bump BUMP=patch|minor|major`
BUMP ?= patch
.PHONY: bump
bump: require-clean  ## Bump version; commits pyproject.toml
	$(call header,Version bump $(BUMP))
	$(POETRY) version $(BUMP)
	git add pyproject.toml
	git commit -m "chore(release): bump version ($(BUMP))"
	@echo "New version: $$($(POETRY) version -s)"

# --- GitFlow: release/hotfix management -----------------------------------

# Start a release branch from develop.
# Usage: `make start-release RELEASE=1.2.0`
RELEASE ?=
.PHONY: start-release
start-release: require-clean require-develop  ## Create release/x.y.z from develop
	@[ -n "$(RELEASE)" ] || { echo "Set RELEASE=x.y.z (e.g., make start-release RELEASE=1.2.0)"; exit 2; }
	$(call header,Create branch release/$(RELEASE) from develop)
	git checkout -b release/$(RELEASE) develop
	@echo "→ Stabilize here (fixes/docs only). Consider: 'make bump' if version needs updating."

# Finish a release: merge to main, tag, push; back-merge to develop; delete branch.
.PHONY: finish-release
finish-release: require-clean require-release-branch  ## Merge release/* → main, tag vX.Y.Z, back-merge
	$(call header,Finalize release from $(BRANCH))
	@cur=$$(git rev-parse --abbrev-ref HEAD); \
	rel=$$(echo $$cur | sed -n 's/^release\/\([0-9.]\+\).*$$/\1/p'); \
	[ -n "$$rel" ] || { echo "Cannot parse version from $$cur"; exit 2; } ; \
	git checkout main; \
	git merge --no-ff $$cur -m "Merge $$cur → main"; \
	git tag -a v$$rel -m "Release v$$rel"; \
	git push origin main v$$rel; \
	git checkout develop; \
	git merge --no-ff $$cur -m "Merge $$cur → develop"; \
	git branch -d $$cur; \
	git push origin develop :$$cur

# Start a hotfix branch from main.
# Usage: `make start-hotfix HOTFIX=1.2.1`
HOTFIX ?=
.PHONY: start-hotfix
start-hotfix: require-clean require-main  ## Create hotfix/x.y.z from main
	@[ -n "$(HOTFIX)" ] || { echo "Set HOTFIX=x.y.z (e.g., make start-hotfix HOTFIX=1.2.1)"; exit 2; }
	$(call header,Create branch hotfix/$(HOTFIX) from main)
	git checkout -b hotfix/$(HOTFIX) main

# Finish a hotfix: merge to main, tag, push; back-merge to develop; delete branch.
.PHONY: finish-hotfix
finish-hotfix: require-clean require-hotfix-branch  ## Merge hotfix/* → main, tag vX.Y.Z, back-merge
	$(call header,Finalize hotfix from $(BRANCH))
	@cur=$$(git rev-parse --abbrev-ref HEAD); \
	rel=$$(echo $$cur | sed -n 's/^hotfix\/\([0-9.]\+\).*$$/\1/p'); \
	[ -n "$$rel" ] || { echo "Cannot parse version from $$cur"; exit 2; } ; \
	git checkout main; \
	git merge --no-ff $$cur -m "Merge $$cur → main"; \
	git tag -a v$$rel -m "Hotfix v$$rel"; \
	git push origin main v$$rel; \
	git checkout develop; \
	git merge --no-ff $$cur -m "Merge $$cur → develop"; \
	git branch -d $$cur; \
	git push origin develop :$$cur

# Optional: publish a GitHub Release from latest tag (Release Drafter usually handles publish on tag)
.PHONY: gh-release
gh-release:  ## Publish GitHub Release for latest tag (requires gh)
	$(call header,Publish GitHub Release (latest tag))
	@which gh >/dev/null || { echo "Install GitHub CLI (gh) first."; exit 2; }
	@last=$$(git describe --tags --abbrev=0); \
	gh release create $$last --generate-notes || { echo "Release may already exist."; exit 0; }

# --- Legacy/manual flow (kept for convenience) -----------------------------
# NOTE: For GitFlow, prefer start/finish release & hotfix targets above.

.PHONY: release
release:  ## Legacy: bump+build+tag (bump=patch|minor|major). Prefer GitFlow targets instead.
	$(call header,Release $(bump))
	@[ "$(bump)" ] || (echo "Set bump=patch|minor|major"; exit 2)
	@$(git_clean) || (echo "Working tree dirty; commit/stash first."; exit 2)
	$(POETRY) version $(bump)
	$(POETRY) build
	@git add pyproject.toml
	@git commit -m "chore(release): $(shell $(POETRY) version -s)"
	@git tag "v$(shell $(POETRY) version -s)"
	@echo "Created tag v$(shell $(POETRY) version -s). Push with:"
	@echo "  git push && git push --tags"
	@echo "Then publish release notes (Release Drafter draft should be ready)."

# --- Misc ------------------------------------------------------------------

.PHONY: help
help:  ## Portable help with grep+awk; uses \x1b for ANSI color (works on mawk/gawk)
	@printf "\nTargets:\n"
	@grep -h -E '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | \
	awk 'BEGIN { FS=":.*##" } \
	     { printf "  \x1b[36m%-22s\x1b[0m %s\n", $$1, $$2 }'

.PHONY: help-nocolor
help-nocolor:  ## If your terminal/awk hates ANSI, use this instead
	@printf "\nTargets:\n"
	@grep -h -E '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | \
	sed -E 's/^([a-zA-Z0-9_.-]+):.*##[ ]?(.*)$$/  \1\t\2/'
