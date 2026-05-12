Run a full wiki lint pass on `andromeda-wiki/`.

## Checks

Run all five. Read files in batches (entities → concepts → interpreter → sources → index + log).

1. **Contradictions.** Look for the same fact stated differently on two or more pages without a `> [!conflict]` callout. Pay special attention to `(agidev, unverified)` claims that are contradicted by code observations on another page.
2. **Orphan pages.** Every `.md` file under `andromeda-wiki/` (excluding `index.md` and `log.md`) must appear in `andromeda-wiki/index.md`. Report any that don't.
3. **Missing link targets.** Scan all pages for `[[...]]` wiki-links. Report any target that doesn't correspond to an existing file.
4. **Stale deferrals.** Grep all pages for `not yet ingested`, `to be added when`, `Group [0-9]`, `(not yet`, `deferred to`. These are maintenance debt from Phase B; resolve them or convert to explicit open-item callouts.
5. **Conflicts-page threshold.** Count `> [!conflict]` callouts across all pages. If more than 6, propose consolidating to `andromeda-wiki/conflicts.md`.

## Process

For each finding: state the affected file, describe the issue, and propose the fix. Apply fixes only after confirming with the user. Group trivial fixes (stale text, broken links) and apply them together; discuss substantive contradictions individually.

## Log entry

After completing the pass, append:
```
## [YYYY-MM-DD] lint | full-wiki

**Findings.**
1. ...

**Changes applied.**
- ...

**Open items carried forward.** [unresolved conflicts or gaps — not lint failures]
```
