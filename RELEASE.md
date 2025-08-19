# Release Process

This document describes how to create a new release of the **Saskan*- project.

---

## 1. Prepare

- Ensure your working tree is clean:

```bash
  git status
````

- Run the quality gates:

  ```bash
  make check
  ```

## 2. Draft Release Notes

- Review the [draft release](https://github.com/genuinemerit/saskan-app/releases) created by Release Drafter.
- Confirm the version bump (patch, minor, major) is correct based on merged PR labels.
- Update `CHANGELOG.md` if needed.

## 3. Bump Version & Tag

- Use Poetry to bump the version:

  ```bash
  make release bump=patch   # or bump=minor / bump=major
  ```

  This will:

  - Update `pyproject.toml`
  - Build the distribution
  - Create a git tag (`vX.Y.Z`)

## 4. Push

- Push commits and tags:

  ```bash
  git push && git push --tags
  ```

## 5. Publish Release

- Go to [GitHub Releases](https://github.com/genuinemerit/saskan-app/releases).
- Publish the drafted release with the correct version tag.
- Release notes will be pre-filled by Release Drafter (edit as needed).

## 6. Publish to PyPI (optional, when ready)

- Ensure you are logged in (`poetry config pypi-token.pypi <token>`).
- Build and publish:

  ```bash
  poetry build
  poetry publish
  ```

---

## Notes

- **Pre-releases**: use `poetry version prerelease` (e.g. `0.1.0a1`) and tag accordingly.
- **Rollback**: if something goes wrong, delete the GitHub release and tag, fix, and re-tag.
- **Automation**: CI may later handle publish steps; this doc remains the human source of truth.
