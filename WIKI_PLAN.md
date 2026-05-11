# Plan: AGI-format wiki bootstrap for andromeda

## Context

Andromeda's reverse-engineering work is bottlenecked on byte-level format knowledge that currently lives in two places: a ~640K HTML spec corpus in `AGI_Specifications/` (which `CLAUDE.md` explicitly tells Claude not to read broadly) and conversational history scattered across sessions. The result is that every new session re-derives format facts from scratch, agidev's known inaccuracies aren't pinned to specific claims, and hard-won corrections we've discovered together evaporate into chat history.

This plan instantiates the pattern described in `llm-wiki.MD` as an **AGI-format-only wiki** in-repo: a persistent, cross-linked markdown knowledge base maintained by Claude, covering byte layouts, the LOGIC VM, encryption details, blitting/rendering, and source-reliability annotations. The wiki distills the spec corpus once and stays current as we work, so future sessions consult `wiki/index.md` first and fall back to `AGI_Specifications/` only for source-of-truth verification. This also positions a future Rust rewrite to inherit a language-agnostic format reference rather than re-extracting it from Python.

**Ownership note:** Per the existing implementation-ownership convention (user writes code, Claude consults), the wiki is the explicit exception — Claude authors and maintains wiki content, consistent with the `llm-wiki.MD` pattern. The user directs ingestion, reviews drafts, and approves edits. Code in `gfx/`, `resource/`, `util/`, `main.py` is unaffected by this plan.

## Resume protocol (read first if you are picking this up cold)

This plan is designed to be executed across multiple sessions. If you are a fresh agent invoked with no prior conversation context, do these three things before taking any other action:

1. **Read the Progress section below.** It records which phases are complete, in-progress, or not yet started, plus per-chapter checkboxes for Phase B ingest.
2. **Read `wiki/log.md` if it exists.** Its tail (`## [YYYY-MM-DD] ingest | <chapter>` entries) is the authoritative record of what was actually applied to the wiki, in case the Progress section drifted out of sync with reality. If they disagree, trust `wiki/log.md`.
3. **Confirm with the user before resuming.** State which phase you're entering and which chapter you'd ingest next. Do not silently continue — the user may have changed scope between sessions.

When you finish a phase or a chapter, update the Progress section in this file (Edit tool) and append the corresponding entry to `wiki/log.md`. Both updates are part of "done"; do not mark a step complete without both.

## Progress

Update the checkboxes here as work proceeds. Format for in-progress items: `- [~] item — note`.

**Phase A — Scaffold**
- [x] `WIKI.md` written at repo root
- [x] `wiki/` directory + subdirectories (`entities/`, `concepts/`, `interpreter/`, `sources/`) created
- [x] `wiki/index.md` seeded with categorized empty sections
- [x] `wiki/log.md` seeded with bootstrap entry
- [x] `CLAUDE.md` redirect added under `### AGI Specification Reference`
- [x] Smoke check passed (fresh session reading CLAUDE.md mentions the wiki when asked an AGI-format question)

**Phase B — Bootstrap ingest** (sequential within each group; groups run in the listed order)

Group 1 — Files (foundation):
- [x] `3-1-Files.html`
- [x] `3-2-Files.html`
- [x] `3-3-Files.html`
- [x] `3-4-Files.html`

Group 2 — Interpreter (VM model):
- [x] `2-1-Interpreter.html`
- [x] `2-2-Interpreter.html`
- [x] `2-3-Interpreter.html`
- [x] `2-4-Interpreter.html`
- [x] `2-5-Interpreter.html`
- [x] `2-6-Interpreter.html`
- [x] `2-7-Interpreter.html`
- [x] `2-8-Interpreter.html`

Group 3 — Logic (bytecode):
- [x] `4-1-Logic.html`
- [x] `4-2-Logic.html`
- [x] `4-3-Logic.html`
- [x] `4-4-Logic.html`
- [x] `4-5-Logic.html`
- [x] `4-6-Logic.html`

Group 4 — Picture:
- [x] `5-1-PICTURE.html`
- [x] `5-2-PICTURE.html`
- [x] `5-3-PICTURE.html`

Group 5 — View (validation case):
- [x] `6-1-VIEW.html`
- [x] `6-2-VIEW.html`
- [x] `6-3-VIEW.html`

Group 6 — Sound:
- [x] `7-1-SOUND.html`
- [x] `7.2-SOUND.html`

Group 7 — Other (parallel-safe):
- [x] `8-1-OtherData.html`
- [x] `8-2-WORDS_TOK.html`
- [x] `8-3-SampleCode.html`

Group 8 — Intro/Info (parallel-safe, lowest priority):
- [x] `1-1-Introduction.html`
- [x] `1-2-WhatsNew.html`
- [x] `9-1-Info.html`
- [x] `9-2AGDS.html`
- [x] `9-3-MakingOfThunderstorm.html`

**Phase C — Lint pass**
- [x] Contradictions scan — no new contradictions; all six existing ones properly flagged with `[!conflict]`
- [x] Orphan-page scan — none; all 60 pages in index, reachable in ≤2 hops
- [x] Missing-concept-page scan — `[[interpreter/debug-modes]]` was dangling; created stub page + index entry
- [x] Stale-claim scan — six files had "not yet ingested" / "to be added when" markers; all resolved
- [x] Conflicts page consolidated — six `[!conflict]` callouts across five pages; density is acceptable, no dedicated conflicts.md needed

**Phase D — Extract skills from usage**
- [ ] Review `wiki/log.md` for prompt patterns that repeated during Phases B and C
- [ ] Draft `/wiki-file` skill body (highest-value, conversational filing)
- [ ] Draft `/wiki-ingest <path>` skill body
- [ ] Draft `/wiki-query <question>` skill body
- [ ] Draft `/wiki-lint` skill body
- [ ] User installs the skills they want via `update-config` or hand-editing

## End state

```
andromeda/
├── CLAUDE.md                    # +3 lines redirecting AGI-format Qs to wiki/index.md first
├── WIKI.md                      # NEW — schema + conventions doc
├── wiki/                        # NEW — Claude-owned wiki
│   ├── index.md                 # content catalog, grouped by category
│   ├── log.md                   # chronological ingest/query/lint log
│   ├── entities/                # one page per resource type (VIEW, PIC, LOG, SND, OBJECT, WORDS.TOK, VOL, *DIR)
│   ├── concepts/                # shared primitives (rle, nibble-packing, offset-encoding, ega-palette, xor-key, etc.)
│   ├── interpreter/             # VM model, opcode tables, event loop, priority bands
│   └── sources/                 # one short page per ingested chapter with citation back to AGI_Specifications/
└── AGI_Specifications/          # unchanged — remains source of truth
```

No new tooling, no hooks, no subagents-as-personas, no skills (yet). The skill layer is deferred to Phase D after we see what prompts actually repeat.

## Out of scope (non-goals)

- Engine architecture docs, Python impl notes, Rust rewrite design — these stay where they are (`README.md`, `DEVELOPMENT_PLAN.md`, `CLAUDE.md`). The wiki is **format-only**.
- Search tooling (qmd/MCP). The index file is sufficient at this scale; revisit only if it stops working.
- Frontmatter/Dataview conventions. Add later if useful, not on day one.
- Automated ingestion via hooks. Editorial judgment is the point.

## Phase A — Scaffold

Create the bones so the wiki has somewhere to live before any ingest happens.

1. **Write `WIKI.md`** at repo root. Sections:
   - **Purpose** — one paragraph: AGI-format-only knowledge base, Claude-authored, user-directed.
   - **Directory layout** — the tree above with one-line purpose per directory.
   - **Page conventions** — markdown only; obsidian-style `[[wiki-links]]` for cross-refs; every factual claim cites a source (e.g., `[3-2-Files.html §VOL layout]` or `[ScummVM agi/decode.cpp:42]`); contradictions between sources flagged inline with `> [!conflict]` callouts.
   - **Source-reliability rules** — carry over the existing agidev-vs-ScummVM guidance from `CLAUDE.md`. When agidev.com and ScummVM disagree, the wiki records both and marks ScummVM/AGI-Studio as ground truth; agidev claims tagged `(agidev, unverified)`.
   - **Operations** — describe ingest, query, lint, and conversational filing as the four workflows. Each gets a short canonical prompt template (these become the seeds for Phase D skills).
   - **Index discipline** — `index.md` is updated on every ingest; orphan pages forbidden; every page reachable from the index in ≤2 hops.
2. **Create `wiki/` scaffolding** — empty `entities/`, `concepts/`, `interpreter/`, `sources/` directories (with `.gitkeep` if needed), plus seeded `index.md` (empty categorized sections) and `log.md` (one bootstrap entry).
3. **Edit `CLAUDE.md`** — modify the existing `AGI Specification Reference` section (currently under `### AGI Specification Reference` in the Architecture section) to add: "Consult `wiki/index.md` first for AGI format questions — it's a distilled, cited knowledge base maintained by this agent. Fall back to `AGI_Specifications/` only when the wiki is silent or when verifying a contested byte-level claim against source-of-truth." Keep the existing "do not read broadly" guidance for the raw spec.

## Phase B — Bootstrap ingest (full corpus sweep)

Ingest all 34 chapters from `AGI_Specifications/Specifications/` using sequential subagents — one chapter per `Explore` agent. Main session never reads the raw HTML; it consumes only the structured distillates returned by subagents and applies wiki edits.

**Subagent contract.** Each `Explore` agent receives:
- The single chapter path it owns.
- A short brief on existing wiki state (which concept/entity pages already exist, which to extend vs. duplicate-avoid).
- An instruction to return a structured proposal under ~2500 words: new entity pages (with proposed paths + bodies), deltas to existing concept pages (with file paths + specific insertions), cross-reference candidates, and any conflicts noticed vs. existing pages.
- Explicit "do not write files" — proposals only.

Main session reviews each proposal with the user, applies the edits, updates `index.md` and `log.md`, then queues the next chapter.

**Ordering — foundational first, then formats, then meta.** This minimizes duplicate concept pages because concept pages get created in the foundational chapters and only *extended* (not re-proposed) in later chapters.

| Order | Group | Chapters | Strategy |
|---|---|---|---|
| 1 | Files | `3-1` → `3-4` | Sequential. Establishes VOL/DIR, offset-encoding, resource access concepts. Foundation for everything else. |
| 2 | Interpreter | `2-1` → `2-8` | Sequential. Establishes the VM model, event loop, priority bands. Heavy internal cross-reference. |
| 3 | Logic | `4-1` → `4-6` | Sequential. Cites both Files (resource layout) and Interpreter (VM) concepts. The biggest remaining decoder gap. |
| 4 | Picture | `5-1` → `5-3` | Sequential. Shares draw-primitive vocabulary with View. |
| 5 | View | `6-1` → `6-3` | Sequential. Validation case — we already have a working VIEW decoder, so the wiki claims here can be cross-checked against `resource/view.py`. |
| 6 | Sound | `7-1`, `7.2` | Sequential (only 2 chapters). |
| 7 | Other | `8-1`, `8-2`, `8-3` | Parallel-safe — three independent topics (misc data, WORDS.TOK, sample code). |
| 8 | Intro/Info | `1-1`, `1-2`, `9-1`, `9-2`, `9-3` | Parallel-safe — meta/historical. Lowest priority, lightest pages. |

Cross-group parallelism is intentionally limited to groups 7 and 8. The format groups (3–6) run sequentially within themselves *and* sequentially relative to each other, because concept pages compound. Group 2 (Interpreter) could in principle run parallel to Group 1 (Files), but I'd rather pay the time cost to keep the concept-page sequence clean.

**Pacing.** One group per execution slot is the natural unit. After each group, do a mini-lint: scan for duplicate concept pages, missing cross-refs, conflicts to flag.

**Resumability.** Every chapter ingest appends to `wiki/log.md` with the canonical prefix `## [YYYY-MM-DD] ingest | <chapter>` so a fresh agent can `grep "^## \[" wiki/log.md | tail` to see exactly where the previous session stopped. The plan file itself is also updated with a checkbox per chapter as we proceed.

## Phase C — Lint pass

Once Phase B is complete, run a single full-wiki lint:
- Contradictions across pages (especially agidev-vs-ScummVM where wiki claims either source without flagging).
- Orphan pages (no inbound links from `index.md` or other pages).
- Concepts mentioned but lacking their own page.
- Stale claims newer chapters superseded.
- Data gaps that warrant cross-checking against ScummVM source.

Lint runs as a single main-session pass (no subagents) since by then the whole wiki should fit comfortably in context.

## Phase D — Extract skills from usage

After Phase B + C, review what prompts actually repeated during ingest. Author thin skills for the patterns that emerged. Likely candidates:
- `/wiki-ingest <path>` — formalize the Phase B subagent + review workflow for ongoing ingests.
- `/wiki-file` — the conversational-filing case (file the finding we just discussed). This is the highest-value skill day-to-day.
- `/wiki-query <question>` — query against the wiki with citations, offer to file the answer.
- `/wiki-lint` — re-run the Phase C checks.

Don't pre-author. Wait to see the actual ergonomics first. User does the skill setup work (per implementation-ownership convention) using `update-config` or hand-editing; Claude drafts the skill bodies.

## Critical files

- **NEW** `WIKI.md` — schema & conventions; lives at repo root next to `CLAUDE.md`.
- **NEW** `wiki/index.md`, `wiki/log.md`, and the four subdirectories.
- **EDIT** `CLAUDE.md` — small redirect added under `### AGI Specification Reference` (Architecture section, around the paragraph that warns against reading the spec broadly).
- **READ-ONLY, foundational** `AGI_Specifications/Specifications/*.html` — the 34 source chapters.
- **READ-ONLY, validation** `resource/view.py`, `resource/objects.py`, `resource/directory.py` — for cross-checking wiki claims against working decoders during the View/Files/Other group ingests.

No code in `gfx/`, `resource/`, `util/`, `main.py`, or `pyproject.toml` is modified by this plan.

## Verification

The wiki bootstrap is "done" when all four conditions hold:

1. **Coverage** — every chapter in `AGI_Specifications/Specifications/` has a corresponding entry under `wiki/sources/` and at least one entity or concept page that cites it.
2. **Discoverability** — `wiki/index.md` lists every wiki page; no orphans. Every page is reachable from the index in ≤2 hops.
3. **Cross-check on familiar ground** — wiki claims for VIEW, VIEWDIR/LOGDIR/PICDIR/SNDDIR, and OBJECT match the behavior of the existing decoders in `resource/view.py`, `resource/directory.py`, `resource/objects.py`. Concretely: pick 3 byte-level claims from the wiki for each of these formats and confirm they agree with the code. If they disagree, the wiki is wrong (or the spec is wrong about a format the code handles correctly) — investigate and reconcile.
4. **Round-trip** — open a fresh Claude session and ask a format question (e.g., "what's the byte layout of a VIEW cel header?"). Verify the agent reads `wiki/index.md` first, finds the right page, and answers from the wiki — without reading `AGI_Specifications/` HTML.

Smoke-check after Phase A (before any ingest): scaffold is in place, `CLAUDE.md` redirect renders sensibly, `WIKI.md` is internally consistent. A fresh session reading just CLAUDE.md should mention the wiki when asked an AGI-format question, even if it's empty.

## Risks and what would change the plan

- **If a chapter's distillate balloons past ~3K words consistently**, the chapter is probably two topics — split the subagent call into two narrower briefs.
- **If concept-page duplicates appear despite the sequential ordering**, tighten the subagent brief with explicit "do not propose a new concept page for X, Y, Z — extend the existing ones."
- **If the agidev/ScummVM conflict rate is higher than expected**, add a dedicated `wiki/conflicts.md` page that lists every flagged contradiction with resolution status, rather than scattering `> [!conflict]` callouts.
- **If the bootstrap stalls** (user runs out of bandwidth to review every chapter), fall back to skeleton-first: subagents produce stub pages only, deepen on demand as each format becomes implementation-relevant.
