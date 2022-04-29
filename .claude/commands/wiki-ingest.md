Ingest `$ARGUMENTS` into the andromeda-wiki.

## Step 1 — Snapshot wiki state

Read `andromeda-wiki/index.md` to list all existing pages by category (entities, concepts, interpreter, sources). Also grep the log tail for any currently-tracked dangling forward-refs:

```
grep -E "remain dangling|forward-ref" andromeda-wiki/log.md | tail -10
```

You'll pass this snapshot to the subagent so it knows what already exists and what concepts to extend rather than recreate.

## Step 2 — Spawn subagent

Spawn an `Explore` subagent with this exact brief (substitute the chapter path and the page list from step 1):

> Read `AGI_Specifications/Specifications/$ARGUMENTS`. Produce a structured proposal under ~2500 words:
>
> 1. **New pages** — for each new entity/concept/interpreter page: proposed path and full markdown body.
> 2. **Deltas to existing pages** — file path + the specific text to insert (quote the surrounding context so the insertion point is unambiguous).
> 3. **Index delta** — one-line entry per new page, with the correct category section.
> 4. **Cross-reference candidates** — pages that should gain links to each other.
> 5. **Conflicts** — any byte-level or semantic contradiction vs. existing wiki pages.
>
> **Do NOT write any files — proposals only.**
>
> Existing pages: [list from step 1]

## Step 3 — Review checklist (before writing anything)

Work through these in order. Each is a category of recurring reviewer correction from Phase B:

1. **Byte values.** For any numeric claim involving nibble order, endianness, or bit positions: verify against the raw HTML. Common error: hi/lo nibble pairs inverted; big-endian fields described as little-endian; attenuation register bit order reversed.
2. **`(agidev, unverified)` tags.** Apply to spec claims that can't be verified against code or a secondary source. Do NOT apply to observations about `resource/`, `gfx/`, or `util/` files — those are code facts, not unverifiable claims.
3. **Citations.** Strip `§SectionName` from citations if that section header doesn't exist in the HTML. Many chapters are prose with no formal headers; use plain `[chapter.html]` for those.
4. **Scope.** Claims must come from this chapter's text. Drop any prediction about what "chapter X will cover" unless the source literally says so.
5. **Cross-links.** All `[[wiki-links]]` must point to pages that exist now or are being created in this ingest. New dangling forward-refs are allowed only with explicit rationale logged.
6. **Index entries.** One line per new page. No multi-line bullets.
7. **Source page format.** Four sections: title heading, Scope, Informs, Notes. Match the format of existing source pages.
8. **Page-creation threshold.** Don't create a child page before its parent. Don't create a stub with fewer than 3 facts — fold it into a parent section instead.
9. **Source-page-only decision.** If the chapter covers loader internals, interpreter-binary encryption, version history, or sample-code bibliography (not format content), create only a source page. Document the scope call in Notes.

## Step 4 — Apply

After corrections: write new pages, apply deltas to existing pages, update `andromeda-wiki/index.md`, append a log entry to `andromeda-wiki/log.md`.

Log entry format:
```
## [YYYY-MM-DD] ingest | $ARGUMENTS

**Created.** [[path/page]], ...
**Extended.** [[path/page]], ...
**Review corrections.** [numbered list of substantive corrections only; omit trivial formatting fixes]
**Findings worth pinning.** [surprising or high-value facts; leave blank if none]
**Conflicts.** [any > [!conflict] callouts added, or "None"]
**Open items.** [unresolved questions or deferred claims to revisit]
**Validation status.** [one of: triangulated / code-to-spec / spec-only / no decoder]
```

Finally, update `WIKI_PLAN.md` to check the chapter's checkbox in the Progress section.
