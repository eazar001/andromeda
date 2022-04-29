# WIKI.md — schema & conventions

## Purpose

`andromeda-wiki/` is an AGI-format-only knowledge base distilled from `AGI_Specifications/` and cross-checked against working decoders in `resource/` and external sources (ScummVM, AGI Studio). It is **Claude-authored, user-directed**: Claude proposes, writes, and maintains the content; the user directs ingestion priorities and reviews edits. The wiki exists so future sessions consult a small, cited, cross-linked reference instead of re-deriving format facts from a ~640K HTML corpus the project's `CLAUDE.md` explicitly tells Claude not to read broadly.

Scope is strictly **byte-level formats and the LOGIC VM**: layouts, encodings, opcodes, palettes, encryption, event-loop semantics. Engine architecture, Python implementation notes, and future-rewrite design stay in `README.md`, `DEVELOPMENT_PLAN.md`, and `CLAUDE.md` — not here.

## Directory layout

```
andromeda-wiki/
├── index.md         # categorized catalog of every page; entry point for all queries
├── log.md           # chronological log of ingest / query / lint operations
├── entities/        # one page per resource type (VIEW, PIC, LOG, SND, OBJECT, WORDS.TOK, VOL, *DIR)
├── concepts/        # shared primitives (rle, nibble-packing, offset-encoding, ega-palette, xor-key, ...)
├── interpreter/     # VM model, opcode tables, event loop, priority bands
└── sources/         # one short page per ingested chapter, citing back to AGI_Specifications/
```

Empty subdirectories carry a `.gitkeep` until they hold real pages.

## Page conventions

- **Markdown only.** No frontmatter, no Dataview, no custom syntax. If conventions need to evolve, write them here first.
- **Cross-references use Obsidian-style wiki-links**: `[[entities/view]]`, `[[concepts/rle]]`. Relative paths from `andromeda-wiki/` root.
- **Every factual claim cites a source** inline, in square brackets after the claim:
  - Spec citation: `[3-2-Files.html §VOL layout]`
  - Code citation: `[resource/view.py:get_view_data]` or `[ScummVM agi/decode.cpp:42]`
  - Multiple sources cited together when they corroborate: `[6-1-VIEW.html §cel header; resource/view.py:get_view_data]`
- **Contradictions between sources are flagged inline** with an Obsidian callout:
  ```
  > [!conflict] agidev vs. ScummVM
  > agidev.com claims X. ScummVM treats it as Y. Ground truth: Y, per [resource/view.py] which round-trips Y correctly on sq1.
  ```
  If `> [!conflict]` callouts proliferate (more than ~6 across the wiki), consolidate to `andromeda-wiki/conflicts.md` (per Phase C lint rule).
- **No orphans.** Every page is linked from `index.md` and reachable in ≤2 hops. Every new page adds an `index.md` entry in the same edit.

## Source-reliability rules

Carried over from `CLAUDE.md` and the `agi_spec_sources` memory:

1. **ScummVM source and AGI Studio are ground truth** for byte-level format details. When in doubt about a contested claim, trust the code that round-trips real game data over the spec prose.
2. **agidev.com (the Peter Kelly spec, vendored at `AGI_Specifications/`) has known factual errors** in byte-level details. It remains the broadest single reference and is the primary ingestion source, but its claims are not authoritative on their own.
3. **When agidev and ScummVM (or working code in `resource/`) disagree**, the wiki records both, marks ScummVM/AGI Studio as the resolution, and tags the agidev claim `(agidev, unverified)` or `(agidev, contradicted)`.
4. **Unverified claims are tagged**, not deleted. Future sessions may cross-check, so the tag stays until a code citation or ScummVM citation resolves it.

## Operations

Four canonical workflows. Each gets a short prompt template here; these seed the Phase D skills.

### Ingest

> "Ingest `<chapter>` into the wiki. Spawn an `Explore` subagent with the brief in `WIKI.md §Operations §Ingest brief`. Review the proposal with me, then apply edits and update `index.md` + `log.md`."

**Subagent brief (canonical):** Read `AGI_Specifications/Specifications/<chapter>`. Produce a structured proposal under ~2500 words: new entity pages (proposed path + body), deltas to existing concept pages (file path + specific insertions), cross-reference candidates, and any contradictions noticed vs. existing wiki pages. **Do not write files** — proposals only. List which concept pages already exist so duplicates aren't proposed.

### Query

> "Check the wiki for `<question>`. If `andromeda-wiki/index.md` doesn't surface it, fall back to `AGI_Specifications/` for that specific chapter and offer to file the answer."

The agent reads `andromeda-wiki/index.md` first, follows wiki-links to the relevant page(s), answers with citations from the wiki. Only falls through to `AGI_Specifications/` HTML if the wiki is silent or the user is verifying a contested claim.

### File (conversational)

> "File the finding we just discussed into the wiki."

Used when a session-derived insight (e.g., reverse-engineered from code, observed during decoder work) belongs in the wiki. Agent proposes the page + edits, user approves, agent applies and logs.

### Lint

> "Run the wiki lint pass."

A single main-session sweep: contradictions, orphans, missing concept pages, stale claims, conflicts-page consolidation check. Runs without subagents — the whole wiki should fit in context at this scale.

## Index discipline

- `index.md` is updated on every ingest and every conversational file. Index entry goes in the same commit/edit as the new page.
- Categories in `index.md` mirror the directory layout (Entities / Concepts / Interpreter / Sources), plus a top "Quick refs" section for the highest-traffic pages.
- One-line description per entry. If a description doesn't fit on one line, the page is too broad — split it.
- Orphan pages (no inbound link from `index.md`) are a lint failure.

## Log discipline

Every ingest, file, query (when notable), and lint pass appends an entry to `andromeda-wiki/log.md` with the canonical prefix:

```
## [YYYY-MM-DD] <op> | <target>
```

Where `<op>` is `ingest`, `file`, `query`, or `lint`, and `<target>` is the chapter, page, question, or `full-wiki`. Body lists what was added/changed and any conflicts flagged. The log is the authoritative resumability record — if the plan's Progress section drifts out of sync with the log, trust the log.
