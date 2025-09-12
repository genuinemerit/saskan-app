# Opening and Closing Issues

---

## 1. Where and how to open an Issue

* In your repo (`saskan-app`) → click **Issues** → **New issue**.
* If you have templates (e.g. `feature_request.md`), GitHub will guide you into the right form; otherwise you’ll get a blank editor.

---

## 2. How many Issues?

* One Issue per discrete piece of work or request.

  * Example: *“Add first splash screen”* (feature)
  * Example: *“Fix CLI help formatting”* (bug)
* This keeps work small, trackable, and easy to cross-reference in PRs.

---

## 3. Issue anatomy

A good Issue has:

* **Title**: short, imperative → *“Feature request: add splash screen CLI command”*
* **Description**:

  * **Summary**: what’s being asked.
  * **Rationale**: why it matters.
  * **Acceptance criteria**: how we’ll know it’s done.
* **Labels**:

  * `enhancement` (or `feat`) → feature work.
  * `bug` → fixes.
  * `docs` → documentation requests.

You can create more custom labels if you want (we already set up `feat`, `fix`, `docs`, `chore`, etc.).

---

## 4. Assigning / claiming work

* As **@genuinemerit**, you create the Issue and can assign it to **@stanniel** (in the sidebar → **Assignees**).
* Or **@stanniel** can comment “I’ll take this” and self-assign.
* Either way, the Issue tracks who’s responsible.

---

## 5. Turning an Issue into a PR

When **@stanniel** creates a branch to work on it:

```bash
git checkout develop
git checkout -b feat/first_splash
```

Commit messages and PR description should reference the Issue:

```text
feat(cli): add splash screen command

Closes #12
```

* `#12` = the Issue number.
* When the PR is merged, GitHub automatically **closes the Issue** and links them together.

---

## 6. Communication cycle

* You (as **@genuinemerit**) → open Issues = backlog of work.
* **@stanniel** → picks an Issue, opens a branch/PR, references it.
* PR triggers CI, requests your review via CODEOWNERS.
* You approve → merge.
* GitHub auto-closes the Issue, marking it resolved.

---

## 7. Example workflow for your next feature

1. **@genuinemerit** opens Issue #12:

   * Title: *“Feature request: add splash screen command”*
   * Description:

     * Summary: Add CLI entry point to print a splash banner.
     * Rationale: first user experience.
     * Acceptance criteria: running `saskan splash` prints banner.
   * Label: `feat`
   * Assign: @stanniel

2. **@stanniel** creates branch `feat/first_splash`.

3. Implements code + tests.

4. Opens PR:

   * Title: `feat(cli): add splash screen command`
   * Body: references Issue #12 → `Closes #12`
   * Label: `feat`

5. **@genuinemerit** reviews/approves → merge.

6. Issue #12 auto-closes, showing “Closed by PR #14”.

---

## GitHub Issue Labels

The labels in `genuinemerit/saskan-app` reflect the expectations in these GitFlow‑oriented workflows.

Here’s how to check labels in the GitHub UI:

1. Go to the repository on GitHub (e.g., `https://github.com/<owner>/<repo>`)
2. At the top, click **Issues**.
3. In Issues, click the **Labels** tab

   * Or visit directly: `https://github.com/<owner>/<repo>/labels`
4. That page lists every label currently defined for the repo:

   * Name
   * Color
   * Description
   * Buttons to edit or delete.

From there you can:

* Verify whether your Release Drafter labels (`feat`, `fix`, `breaking-change`, etc.) exist.
* Edit any existing ones (rename, recolor, add descriptions).
* Add new ones with the **New label** button.

Tip: check labels from the command line:

```bash
gh label list --repo <owner>/<repo>
```

This prints a table of names, colors, and descriptions.
