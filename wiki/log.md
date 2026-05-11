# Wiki Log

Chronological record of wiki operations. Canonical entry prefix: `## [YYYY-MM-DD] <op> | <target>` where `<op>` is `ingest | file | query | lint` and `<target>` is the chapter, page, question, or `full-wiki`. This log is the authoritative resumability record — if the plan's Progress section disagrees with this log, trust the log.

## [2026-05-10] bootstrap | wiki

Phase A scaffold landed:

- `WIKI.md` written at repo root (schema, conventions, source-reliability rules, operations, index/log discipline).
- `wiki/` created with `entities/`, `concepts/`, `interpreter/`, `sources/` subdirectories (each carries a `.gitkeep` until pages land).
- `wiki/index.md` seeded with empty categorized sections (Quick refs / Entities / Concepts / Interpreter / Sources).
- `wiki/log.md` seeded with this bootstrap entry.
- `CLAUDE.md` redirect added under `### AGI Specification Reference`: future sessions consult `wiki/index.md` first for AGI format questions; `AGI_Specifications/` becomes the fallback for silence or contested-claim verification.

No entity, concept, interpreter, or source pages exist yet. Phase B (bootstrap ingest) starts with Group 1 — Files (`3-1` → `3-4`).

## [2026-05-10] ingest | 3-1-Files.html

Phase B Group 1 (Files), chapter 1 of 4 ingested.

- Added [[entities/dir-file]] — v2 (four separate flat files) and v3 (single file with 8-byte LE header) layouts; 3-byte entry decoding; resource-nonexistence sentinel folded in as a section rather than a standalone page.
- Added [[concepts/offset-encoding]] — primitive 3-byte (vol nibble, 20-bit big-endian offset) format used in every directory entry. Cross-cites [resource/directory.py:read_byte_triplet].
- Added [[sources/3-1-files]] — chapter summary citing the source path.
- Updated `wiki/index.md` with entries under Entities / Concepts / Sources.

Reviewer fixes applied to the subagent proposal before writing: dropped speculative "Lance Ewing / Internet Archive" attribution (vendored spec is Peter Kelly's); folded the standalone `resource-nonexistence` concept page into `entities/dir-file.md` as a section to avoid an orphan-thin page; corrected v3 header phrasing ("LOGDIR offset is always 8, encoded as `08 00` LE" — not "always 0x0800"); dropped wrong chapter-number predictions in the cross-reference section (`3-2`–`3-4` are still Files, not LOG/PIC/VIEW); standardized prose on "entry" with one "(triplet)" parenthetical at first introduction.

No conflicts observed against `resource/directory.py`.

## [2026-05-10] ingest | 3-2-Files.html

Phase B Group 1 (Files), chapter 2 of 4 ingested.

- Added [[entities/vol-file]] — VOL container format: 5-byte resource header (BE signature `0x1234`, 1-byte VOL number, LE length); resource-type-disambiguation note (type is implicit from which DIR supplied the offset, not encoded in the header); cross-cited `resource/header.py` and `resource/volume.py`.
- Extended [[entities/dir-file]] Overview with one sentence linking `(vol, offset)` resolution to the VOL header on the other side.
- Added [[sources/3-2-files]].
- Updated `wiki/index.md` with `vol-file` under Entities and `3-2-files` under Sources.

Reviewer fixes applied to the subagent proposal: dropped wrong "3-3 / 3-4 cover LOGIC / PIC / VIEW / SOUND" speculation in cross-reference candidates (those are still Files chapters; resource-internal formats start at 4-x and later); corrected `dir-file.md` insertion point (subagent referenced a line that doesn't exist in our actual page); added the resource-type-disambiguation sentence to `vol-file.md` capturing that the VOL header has no type tag; sharpened the `(agidev, unverified)` tag on the VOL-number-in-header so the verified part (byte 2 exists, is the VOL number, per `header.py:14`) is cleanly separated from the unverified rationale (why it's there).

Process note: during this ingest the user set up an Obsidian vault at `Sierra AGI Wiki/` (moving the existing wiki content into it). The vault was then renamed back to `wiki/` to keep the canonical path stable, and `wiki/.obsidian/` was added to `.gitignore` so personal UI state is not committed.

Process note: `CLAUDE.md` §Modules is stale — does not list `resource/header.py` or `resource/volume.py`, and `view.py`'s entry-point signature has changed. Caused me to almost reject this valid proposal as hallucination before reading the actual code. Refresh drafted out-of-band for the user to apply.

No conflicts observed against code in `resource/`.

## [2026-05-10] ingest | 3-3-Files.html

Phase B Group 1 (Files), chapter 3 of 4 ingested.

- Added [[concepts/lzw-compression]] — adaptive LZW (9-/10-/11-bit codes, start-over code 256, end code 257) used for most AGI v3 non-PICTURE resources.
- Added [[concepts/picture-compression]] — 4-bit color-packing scheme exploiting redundancy in `0xF0` / `0xF2` opcodes; PICTURE-specific.
- Extended [[entities/vol-file]] with a `### Version 3 resource header` subsection (7-byte layout: signature, VOL+flags byte where bit 7 = PICTURE flag, uncompressed size, compressed size) and revised the Design notes paragraph to cover both v2 and v3 size constraints plus the PICTURE-flag rationale.
- Added [[sources/3-3-files]].
- Updated `wiki/index.md` with two concept entries and one source entry; no new entity entries (v3 is a variant of [[entities/vol-file]], not its own entity).

Reviewer fixes applied to the subagent proposal: stripped three wrongly-applied `(agidev, unverified)` tags from "Implementation status" notes (those are observations about our own code, not spec claims that need agidev sourcing); skipped a proposed redundant Overview cross-link on `vol-file.md` (the new v3 subsection lives directly under the existing `## Resource header`, so a flow-disrupting forward pointer added noise without helping the reader).

Implementation gap noted (not a spec contradiction, a current-state observation): [resource/header.py] and [resource/volume.py] parse only the v2 5-byte header and implement no decompression. v3 games are not decodable by the Python prototype; documented in the v3 subsection and in the source page; flagged for the eventual Rust-rewrite phase.

No conflicts observed against code in `resource/`.

## [2026-05-10] ingest | 3-4-Files.html

Phase B Group 1 (Files), chapter 4 of 4 ingested. **Group 1 complete.**

Bibliographic chapter — titled "3.4 Sample Code", just a table of Lance Ewing's historical decoders (`agifiles.c`, `volx2.c`, `xv3.pas`, etc.). No new format content; no entity or concept pages added; no deltas to existing pages.

- Added [[sources/3-4-files]] — short source page documenting that the chapter is purely bibliographic and cross-referencing the Group-7 Sample Code chapter (`8-3-SampleCode.html`) that will be ingested later.
- Updated `wiki/index.md` Sources section with the new entry.

Reviewer notes: I initially suspected the subagent had hallucinated the "Sample Code" framing (since the plan separates `3-4-Files.html` from `8-3-SampleCode.html` and the duplicate-naming seemed implausible), but verifying the raw HTML confirmed the chapter title literally is "3.4 Sample Code". The plan's grouping of `3-4` under Files is a filename-based grouping, not a content-based one. Worth being aware of for future cold-resume sessions reading the plan.

Process note: the subagent's section-6 cross-references mentioned `util/crypto.py:xor_cycle` — I almost flagged it as hallucination because CLAUDE.md doesn't list `util/crypto.py`, but verified that the module exists and the function signature matches. Another instance of the stale-CLAUDE.md issue noted in the 3-2 entry. The CLAUDE.md refresh draft sent to the user should also add `util/crypto.py`.

No conflicts; no implementation gap (nothing to implement — chapter is non-prescriptive).

## [2026-05-10] ingest | 2-1-Interpreter.html

Phase B Group 2 (Interpreter), chapter 1 of 8 ingested.

- Added [[interpreter/overview]] — single hub page collecting 2-1's high-level VM-model points (~181 procedure commands / ~18 test commands; variables and flags; priority bands; control lines; ego; view objects; event loop; debug modes; resource types) with forward-references to the subsystem pages later Group-2 chapters will create: [[interpreter/commands]], [[interpreter/variables-and-flags]], [[interpreter/priority-bands]], [[interpreter/control-lines]], [[interpreter/view-objects]], [[interpreter/event-loop]], [[interpreter/debug-modes]].
- Added [[sources/2-1-interpreter]].
- Updated `wiki/index.md`: replaced the empty-Interpreter placeholder with the overview entry; added the 2-1 source entry under Sources.
- Removed `wiki/interpreter/.gitkeep` (directory now holds a real page).

Page-creation philosophy: 2-1 introduces almost every VM primitive at a paragraph's depth but defers detailed specification to chapters 2-2 through 2-8. To avoid producing 8 orphan-thin pages now, all primitives sit as named sections inside `overview.md` with forward-reference wiki-links. Phase C lint will resolve any forward-references that remain dangling at the end of Group 2.

Reviewer fixes applied to the subagent proposal: dropped a 10-line KQ4 script-example code block (couldn't verify whether quoted verbatim from spec or paraphrased as illustration, and the "what is the AGI command language" point reads fine without it); dropped speculative ego-name attributions beyond Rosella and Roger Wilco (the spec just says all games use the name "ego" — Manhunter attribution was filler); harmonized the source page back to the established 4-section format (title / Scope / Informs / Notes) used by all Files-group source pages, rather than the subagent's expanded Author / Last-updated / Implementation-status / Contradictions shape; trimmed the proposed index entry from an 8-link multi-line bullet to a single coherent line per WIKI.md "Index discipline."

`(agidev, unverified)` tag discipline maintained: applied to narrative claims about event-loop ordering, priority-band boundaries, and the cyan-water control-line semantics (spec assertions with no code to validate against — there is no LOGIC interpreter in `resource/`). Implementation-status notes about our own code remain unflagged (observations, not unverifiable claims).

No conflicts observed against Files-group pages.

## [2026-05-10] ingest | 2-2-Interpreter.html

Phase B Group 2 (Interpreter), chapter 2 of 8 ingested. Two forward-references from [[interpreter/overview]] now resolved.

- Added [[interpreter/variables-and-flags]] — full table of reserved `var(0)`–`var(26)` and `flag(0)`–`flag(15)`, semantics for each slot, shared-namespace scoping rules, and a "Spec ambiguities" note for `var(9)` / `var(17)` (both have inverted-looking phrasing in the source HTML, with translator's notes acknowledging the issue).
- Added [[interpreter/event-loop]] — eleven-step per-frame cycle with per-step state management (which variables/flags get read, written, or cleared at each step), control-mode (program-vs-player) handling for `var(6)`, and the post-LOGIC cleanup discipline that gives signaling flags strict cycle-scoped semantics.
- Updated [[interpreter/overview]]: shrank the "Variables and flags" and "The event loop" sections to one paragraph + cross-link each, now that dedicated subsystem pages exist. Other overview sections untouched.
- Added [[sources/2-2-interpreter]].
- Updated `wiki/index.md`: replaced the single-overview Interpreter entry with three entries (overview + variables-and-flags + event-loop); added the 2-2 source entry.

Reviewer fixes applied to the subagent proposal (five total, two of them substantive corrections to spec misreads):

1. **`var(0) = n | (var(n))` was misread as bitwise OR.** Agent annotated it as "a quirk of the spec as written". Verified directly against the chapter HTML: the `|` is the spec's alternation symbol, distinguishing `new_room n` (set `var(0) = n`) from `new_room_v n` (set `var(0) = var(n)`, where `n` is a variable index dereferenced to get the actual room number). Rewrote the cleanup-list entry accordingly.
2. **Step count inconsistency.** Agent's overview said "twelve ordered steps" but listed eleven (the twelfth was "Return to step 1", which is the loop-back, not an operation). Reconciled to eleven steps with the loop-back framed as a closing sentence in the room-transition step.
3. **`var(24)` / `var(25)` rows wrong.** Agent collapsed both as "Reserved for future use". Spec actually has `var(24)` = "29h" (literal hex with no further description; meaning unclear) and `var(25)` = "ID of item selected via `status` command, or 0xFF if Esc was pressed". Split the rows; tagged `var(24)` `(agidev, unverified)` since the spec's description is opaque.
4. **Speculative `[[concepts/egi]]` link.** Agent appended a "See also" link to a hypothetical `concepts/egi` page with the parenthetical "to be created if relevant ... definitions exist". Looks like a typo for `ego` and the speculation isn't worth a dangling forward-ref. Dropped.
5. **Misplaced `(agidev, unverified)` tag on `var(6)`.** Agent put the tag on the forward-reference clause ("exact control-flow semantics deferred to [[interpreter/event-loop]]") rather than on an unverifiable claim. Replaced with a plain cross-link.

Preserved as proposed: the spec's verbatim phrasing of `var(9)` and `var(17)` (both have inverted-logic descriptions in the source, both tagged `(agidev, unverified)` per WIKI convention); the full reserved-flag table; the eleven-step cycle structure and the post-LOGIC cleanup enumeration; the program-vs-player control-mode framing.

Verification touchpoints (against `AGI_Specifications/Specifications/2-2-Interpreter.html`): the `var(0) = n | (var(n))` correction, the `var(2)` border codes (0–4), the `var(24)` "29h" oddity, and the `var(9)` / `var(17)` translator's-note phrasing were all checked against the source HTML directly.

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-3-Interpreter.html

Phase B Group 2 (Interpreter), chapter 3 of 8 ingested.

- Added [[concepts/agi-data-types]] — full catalog of the seven AGI parameter types: Variable (8-bit), Flag (1-bit), String (40-char with zero terminator), Word (parsed-input token), Inventory Item (OBJECT-table index), Object (runtime VIEW-instance index), Message (LOGIC-resident text with `%g<n>` cross-LOGIC format code for LOGIC 0). Includes the per-version string-allocation table (12 strings for 2.089/2.411 and 3.002.107/3.002.149; 24 for intermediate versions, possibly unsupported) and explicitly clarifies the OBJECT-file vs. runtime-object nomenclature collision flagged in the spec itself.
- Added [[sources/2-3-interpreter]].
- Small delta to [[interpreter/overview]]: appended one sentence to the "Variables and flags" section cross-linking the broader data-types catalog.
- Small delta to [[interpreter/variables-and-flags]]: added a See-also entry pointing to [[concepts/agi-data-types]].
- Updated `wiki/index.md`: added `agi-data-types` under Concepts and the 2-3 source entry under Sources.

Placement decision: 2-3 is a cross-cutting type catalog rather than a VM-subsystem spec, so the new page lives under `concepts/` (alongside `offset-encoding`, `lzw-compression`, `picture-compression`) instead of `interpreter/`. The data types underpin command signatures, variable slots, and screen-object addressing — they aren't the property of any single VM subsystem.

Reviewer fixes applied to the subagent proposal:

1. Wrong group attribution. The proposal tagged `[[entities/object]]` (OBJECT file) as "to be ingested with Group 2 — Interpreter". Wrong: OBJECT is a file-system-layer resource and is covered by `8-1-OtherData.html` in Group 7 — Other. Same fix applied to the "see also" qualifier.
2. One inference beyond 2-3's content. The proposal added "Strings are populated by the `get_string` command and by string-formatting commands that interpolate variables, messages, and parsed words into display text." 2-3 itself doesn't specify how strings are populated — that's a Group 3 (Logic) concern. Trimmed to content actually in the chapter.

Verification touchpoints (against `2-3-Interpreter.html`): the version-by-version string table is verbatim from the spec; the `get(dagger)` LOGIC-source example and the KQ1 / Black Cauldron crocodile-moat illustration are verbatim from the spec; the OBJECT-file vs. runtime-object nomenclature clarification is the spec's own language.

No forward-references in `interpreter/overview.md` resolved by this chapter — 2-3 doesn't address any of the still-placeholdered subsystems (`commands`, `priority-bands`, `control-lines`, `view-objects`, `debug-modes`). Five forward-references remain dangling pending later Group-2 ingests (and Group-3 for `commands`).

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-4-Interpreter.html

Phase B Group 2 (Interpreter), chapter 4 of 8 ingested.

- Added [[interpreter/memory-layout]] — runtime heap reference: 17-row table from data-area header through "Other loaded resources", with sizes where the spec gives them and a top-of-page disclaimer that the layout is reverse-engineered from external memory instrumentation and unverifiable without original DOS hardware. Cross-links to [[interpreter/variables-and-flags]] for variable/flag content, [[concepts/agi-data-types]] for the string-version table, and forward-ref to [[interpreter/view-objects]].
- Added [[sources/2-4-interpreter]].
- Small delta to [[interpreter/variables-and-flags]]: added cross-link from the `var(8)` row to the new memory-layout page (var(8) reports free heap pages, which the layout page contextualizes).
- Small delta to [[interpreter/overview]]: appended a sentence to the Implementation-status paragraph noting the memory-layout page is also unverifiable against working code.
- Updated `wiki/index.md`: added `memory-layout` under Interpreter and the 2-4 source entry under Sources.

Page-placement decision: `interpreter/` rather than `concepts/` — runtime heap organization is a per-interpreter-instance concern, not a cross-cutting primitive. The page sits alongside other interpreter-internal subsystem references.

Reviewer fixes applied to the subagent proposal (four total, all spec-content corrections):

1. **Wrong string-version attribution.** Subagent annotated the strings row "12×40 bytes (AGI v1–v2) or 24×40 bytes (AGI v3)". Source HTML gives no version attribution at all, and our own [[concepts/agi-data-types]] (from 2-3 ingest) records the correct per-version mapping: 12 strings for 2.089/2.411 *and* for 3.002.107/3.002.149; 24 for intermediate versions (possibly unsupported). Stripped the subagent's mapping; cross-linked to the agi-data-types version table instead.
2. **`"Avis Durgan"` pinned to "LOGIC resource decryption" without source.** Source HTML says only `"Avis Durgan" encryption string` — it does not specify the encryption target. The Python prototype uses it as the OBJECT-file XOR key (`resource/objects.py`); whether LOGIC also uses it is a Group-3 ingest concern. Rewrote the row to state what 2-4 actually says, note our current code's use of the key, and defer the broader role to the LOGIC ingest.
3. **False var(8) chapter-summary claim.** Subagent's chapter summary said 2-4 "mentions `var(8)` indirectly". The chapter has no narrative beyond the table; var(8) is not mentioned. The cross-link from var(8) → memory-layout still makes conceptual sense (var(8) reports free heap pages and the layout page describes the heap) but isn't because 2-4 references var(8). Dropped the false claim.
4. **Misapplied `(agidev, unverified)` tag** on the "Timers, blocks" row, framed as "exact boundaries not specified". That's an incompleteness observation, not an unverifiable claim — the spec just doesn't say more. Replaced per-row tagging with a single top-of-page disclaimer covering the whole reverse-engineered layout.

Cold-resume note: when reading future spec chapters, do not strip non-Peter-Kelly author attributions reflexively. The 3-1 lesson ("vendored spec is Peter Kelly's") doesn't generalize — individual chapters in the corpus can have other authors, attributed in the HTML header. 2-4 is genuinely by Lance Ewing, "Retrived from the Internet Archive" per the source HTML (typo in original). Verify per-chapter authorship from the HTML rather than assuming.

No forward-references in [[interpreter/overview]] resolved by this chapter — 2-4 doesn't address `commands`, `priority-bands`, `control-lines`, `view-objects`, or `debug-modes`. Five forward-references remain dangling.

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-5-Interpreter.html

Phase B Group 2 (Interpreter), chapter 5 of 8 ingested. **Source-page-only ingest** — no entity, concept, or interpreter pages added; no deltas to existing pages.

- Added [[sources/2-5-interpreter]] — captures the chapter's content (game IDs and their `"eIDX"`-suffix byte format, `set.game.id` mechanism, the SIERRA.COM/LOAD loader programs, the 128-byte rolling-XOR algorithm with carry-feedback rotation, track-6 key fetching, ID-check bypass methods) as a bibliographic reference with explicit out-of-scope framing.
- Updated `wiki/index.md` Sources section with the new entry.

Scope decision: the chapter describes the loader's decryption of the AGI interpreter binary itself (the `.EXE` or `.COM` that the user runs), not encoding of any game-data resource. Andromeda reimplements the interpreter rather than running Sierra's original binary, so loader-side decryption never enters our implementation path. The XOR-rotate algorithm is preserved verbatim in the source page's Scope section in case a future use case (e.g., extracting data from a sealed original distribution, or fingerprinting an interpreter version) needs it. Promoting it to a `concepts/` page now would orphan with no inbound links per WIKI.md "no orphans" discipline.

Cross-reference added: source page notes that the 128-byte loader key is *unrelated* to the 12-byte `"Avis Durgan"` key documented in [[interpreter/memory-layout]] — different keys for different targets at different lifecycle stages. Worth recording explicitly because both will surface when "AGI encryption" comes up in future ingests.

Forward breadcrumbs left for Group 3 (Logic): `set.game.id` opcode semantics should reference this page when documented; the spec's unenumerated "about four AGI commands have changed the number of arguments" note will need per-version argument-count tables in the Group-3 opcode work.

Reviewer fixes applied to the subagent proposal (framing changes, not spec misreads — the subagent's content analysis was sound this ingest):

1. **"Informs: None" was framing-only dead weight.** Reworded to "No wiki entity or concept pages" + explicit Group-3 breadcrumbs (set.game.id, four-changed-commands note). The chapter does inform a future ingest even if not the current one; making this explicit helps the Group-3 reviewer find it.
2. **Scope/Notes split was inconsistent in the proposal.** Subagent placed the encryption algorithm and game-ID examples in Notes, leaving Scope vague. Consolidated into Scope as five clearly-labeled bullets (Game IDs / format / Loaders / encryption / bypass methods), mirroring the chapter's own structure. Notes section now carries only meta-commentary (authorship, scope rationale, the Avis-Durgan-vs-loader-key distinction).
3. **Intro paragraph trimmed** from the subagent's multi-clause description to one sentence + "bibliographic for this wiki's scope" framing.
4. **Authorship verified against HTML header**: explicitly "by Lance Ewing, with additions/modifications by Peter Kelly and Anders M Olsson; last updated 3 March 1998." Source page now notes the variation per-chapter and reminds the cold-resume reader to check HTML headers rather than assume Peter Kelly.

Authorship snapshot for the corpus so far:
- 2-1, 2-2, 2-3: Peter Kelly (assumed; not directly verified against HTML this session).
- 2-4: Lance Ewing solo, "Retrived from the Internet Archive".
- 2-5: Lance Ewing primary, with Peter Kelly and Anders M Olsson contributing.

No forward-references in [[interpreter/overview]] resolved. Five remain dangling (`commands`, `priority-bands`, `control-lines`, `view-objects`, `debug-modes`).

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-6-Interpreter.html

Phase B Group 2 (Interpreter), chapter 6 of 8 ingested.

- Added [[interpreter/input-parsing]] — input-preprocessing pipeline (punctuation, case, multi-space, vocabulary lookup) and the `said` test command's pattern-matching algorithm (preconditions on `flag(2)`/`flag(4)`, wildcards `1` and `9999`, equality match, explicit at-most-once-per-cycle semantics section).
- Added [[sources/2-6-interpreter]].
- Three deltas to [[interpreter/variables-and-flags]]: refined `var(9)` (1-indexed unparsed-word position; (agidev, unverified) tag dropped now that 2-6 resolves the 2-2 phrasing oddity); `flag(2)` (explicitly set only after *successful* preprocessing, not on raw input-entered); `flag(4)` (at-most-once-per-cycle `said` semantics — cleared by event-loop cleanup *and* on next successful input parse, NOT on failed `said`).
- Delta to [[concepts/agi-data-types]]: replaced the existing "to be added when later chapters cover input handling" forward-ref under the Word type with a concrete cross-link to [[interpreter/input-parsing]], plus an honest note that other input-handling commands (`read`, `get_string`) are LOGIC opcodes for Group 3 to cover. Also fixed the stale page name (`input-and-parsing` → `input-parsing`).
- Delta to [[interpreter/overview]]: added a new "## Input parsing" section between "The event loop" and "Debug modes", mirroring the existing one-paragraph-per-subsystem pattern with a forward-link to the detail page.
- Updated `wiki/index.md`: added `input-parsing` under Interpreter and the 2-6 source entry under Sources.

Authorship verified against HTML header: "from AGDS docs*" with footnote attributing translation from Russian to Vassili Bykov; italic "Retrived from the Internet Archive" (sic) annotation, identical to 2-4's provenance. Last updated 31 August 1997 — same date as 2-4. Plausibly both chapters were extracted in the same Internet Archive session.

Reviewer fixes applied to the subagent proposal (one substantive spec misread, plus framing refinements):

1. **WRONG `flag(4)` clearing rule.** Subagent claimed in both the page body and the `flag(4)` row delta that "`flag(4)` is cleared each time a `said` test fails to match." This is not in the spec — the chapter only specifies `flag(4)` clearing during input-preprocessing success ("Flag(4) ... is set to 0") and is silent on failed `said` tests. The actual semantics are: `flag(4)` is set to 1 on a successful `said` match, then stays set for the rest of the cycle, causing every subsequent `said` in that same cycle to fail the precondition and return FALSE. Combined with the event-loop cleanup (per 2-2) and the next input-parse (per 2-6), `flag(4)` gets cleared at cycle boundaries — but never inside a cycle on failed `said`. Rewrote both the page body and the `flag(4)` row delta to state the correct at-most-once-per-cycle semantics.
2. **Pseudo-section citations.** Subagent cited invented section names like `[2-6-Interpreter.html §How the input is matched]` and `[§If all elements match, Flag(4) is set]`. The chapter has no actual section headers — it's a single flowing block of HTML markup with `<ol>`, `<ul>`, and `<p>`. Stripped pseudo-section citations to plain `[2-6-Interpreter.html]`, matching the citation style used for the similarly-section-less 2-4 ingest.
3. **Overview delta placement.** Subagent proposed an awkward parenthetical insertion into the Variables-and-flags paragraph of overview.md ("...input state (player input is converted to word codes via the [[interpreter/input-parsing]] pipeline), error codes..."). Replaced with a proper one-paragraph "## Input parsing" section between "The event loop" and "Debug modes", matching the existing per-subsystem section pattern on the page.
4. **`agi-data-types` delta sharpened.** Subagent's proposed replacement silently dropped the existing mention of the `read` command without explaining why. 2-6 doesn't cover `read` — that's a separate LOGIC opcode in Group 3. New cross-link explicitly defers `read` / `get_string` to Group 3 rather than silently dropping them.
5. **Missed source-page details.** Subagent noted AGDS/Bykov attribution correctly but missed the "Retrived from the Internet Archive" annotation and the matching 31 August 1997 update date with 2-4. Added both to the source page Notes; flagged the IA-session-co-extraction hypothesis as a process observation.

`(agidev, unverified)` tag changes: dropped from `var(9)` (2-6 resolves the 2-2 inversion); applied to the new page's "longest character sequence matching the entered" discussion (vocabulary-lookup algorithm genuinely under-specified — could be longest-match, prefix-match, or other; ScummVM uses trie; no decoder code in `resource/` to validate either way).

Authorship snapshot for the corpus so far:
- 2-1, 2-2, 2-3: Peter Kelly (assumed; not directly verified against HTML this session).
- 2-4: Lance Ewing solo, "Retrived from the Internet Archive" (31 August 1997).
- 2-5: Lance Ewing primary, with Peter Kelly and Anders M Olsson contributing (3 March 1998).
- 2-6: AGDS manual, translated from Russian by Vassili Bykov, "Retrived from the Internet Archive" (31 August 1997).

No forward-references in [[interpreter/overview]] resolved by this chapter — 2-6 does not address `commands`, `priority-bands`, `control-lines`, `view-objects`, or `debug-modes`. Five remain dangling. The chapter's own forward-pointer to `4-3-Logic.html` (Group 3) is a separate concern noted in the source page Notes for the Group 3 reviewer.

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-7-Interpreter.html

Phase B Group 2 (Interpreter), chapter 7 of 8 ingested. **Source-page-only ingest** — no entity, concept, or interpreter pages added.

- Added [[sources/2-7-interpreter]] — captures the chapter's substance (enumeration of v2 and v3 interpreter versions seen in shipped games, game coverage, chronological span 1986-11 to 1989-08, multi-version re-release pattern) with explicit out-of-scope framing.
- Small delta to [[concepts/agi-data-types]]: appended a sentence to the string-allocation paragraph cross-linking [[sources/2-7-interpreter]] for the explicit enumeration of "intermediate versions" (the row covering 24-string allocation) — turns an abstract category into a concrete set: {2.272, 2.425, 2.426, 2.435, 2.439, 2.440, 2.915, 2.917, 2.936, 3.002.086, 3.002.098, 3.002.102}.
- Updated `wiki/index.md` Sources section with the new entry.

Editorial divergence from subagent recommendation: subagent proposed *no ingest at all* (not even a source page), arguing that the chapter is pure bibliography with zero format facts and that creating a source page would violate WIKI.md's "no orphans" rule. Main session kept a source page anyway, for two reasons:

1. **Consistency with 2-5 precedent.** 2-5 was equally out-of-scope (interpreter-binary encryption and loaders, not game-data format) and we made a source-page-only ingest. The pattern of "out-of-scope chapters get a source page documenting the scope call so a future cold-resume agent doesn't re-litigate it" is now established. Skipping 2-7 entirely would break that pattern.
2. **Referential value.** The version enumeration concretely grounds the abstract "intermediate versions" phrasing in [[concepts/agi-data-types]] and supplies Group 3's reviewer with explicit version names to index per-opcode-argument-count differences against (per the breadcrumb left in 2-5). With the agi-data-types delta, the source page is indexed *and* cross-linked from where the version-conditional claim lives, so it isn't an orphan.

Authorship verified against HTML header: no formal byline, only `mikeph@concentric.net` as the maintainer; "Retrived from the Internet Archive" annotation matches 2-4 and 2-6's IA provenance pattern. The chapter has its own internal versioning ("Version 4.0", with "What's New" sections going back to v2.0) — actively maintained community submission.

Authorship snapshot for the corpus so far:
- 2-1, 2-2, 2-3: Peter Kelly (assumed; not directly verified against HTML).
- 2-4: Lance Ewing solo, IA, 31 August 1997.
- 2-5: Lance Ewing primary + Peter Kelly + Anders M Olsson, 3 March 1998.
- 2-6: AGDS manual translated by Vassili Bykov, IA, 31 August 1997.
- 2-7: `mikeph@concentric.net` ("Version Control" v4.0), IA, no date.

Three of seven Group-2 chapters are explicitly IA-provenance; four of seven are non-Peter-Kelly contributions. The "Peter Kelly's AGI Specifications" framing in CLAUDE.md and elsewhere is more accurately "Peter Kelly's curated AGI specifications corpus" — multiple authors.

No forward-references in [[interpreter/overview]] resolved by this chapter. Five remain dangling. The chapter's own implicit forward-pointer is to Group 3's per-opcode-version work, via the 2-5 breadcrumb.

No conflicts observed against existing pages.

## [2026-05-10] ingest | 2-8-Interpreter.html

Phase B Group 2 (Interpreter), chapter 8 of 8 ingested. **Group 2 complete.**

- Added [[interpreter/command-evolution]] — version-conditional command-argument-count rules (`quit`: 0 args in 2.089, 1 in all later; `print.at` / `print.at.v`: 3→4 at a typo-buggy boundary; unknown #176: 1 arg in 3.002.086, 0 in later v3) plus a command-count summary table by interpreter version. Contains a `> [!conflict]` callout for the spec's "2.400" typo (no such version exists; plausibly meant 2.440).
- Added [[sources/2-8-interpreter]] — preserves the full 14-row interpreter fingerprint table verbatim (file size, AGIDATA.OVL size, command count, OBJECT-encryption flag, LZW flag), the four post-table observations, the COMMAND ARGUMENT NUMBER DESCREPENCIES section, the AGI VERSION THREE section (including the new v2-LOGIC-encryption inference), and the NUMBER OF STRINGS section. Forward breadcrumbs to [[entities/object]] (Group 7), [[entities/logic]] (Group 3), [[entities/picture]] (Group 4).
- Updated `wiki/index.md`: added `command-evolution` under Interpreter and the 2-8 source entry under Sources.

**Important new fact for Group 3:** 2-8 says "The LOGIC files do not encrypt the text messages with 'Avis Durgan' since there is no need to do this because it is compressed anyway" — this is a *v3* claim, but it *implicitly establishes* that **AGI v2 LOGIC files DO encrypt their text-message section with Avis Durgan**. This is the only direct evidence of v2 LOGIC text-message encryption in the Group-2 corpus, and is preserved as a forward breadcrumb in the 2-8 source page for the Group 3 reviewer to follow up. The Python prototype's [resource/objects.py] already uses Avis Durgan for OBJECT-file XOR; v2 LOGIC text-message decoding would reuse the same key.

Reviewer fixes applied to the subagent proposal (substantive; subagent overreached in several places):

1. **Invented per-version string-allocation data.** Subagent proposed an `agi-data-types` delta with "three discrete phases" {early v2 → 12, mid v2 / early v3 → 24, final v3 → 12}, attributed to 2-8. The chapter actually only says "at least 12; most have 24, but I don't know if the extra space is used" — abstract, no per-version breakdown. The fine-grained table the subagent constructed was unsourced extrapolation and contradicted our existing 2-3-sourced agi-data-types table. **Delta dropped entirely.**
2. **Picture-compression delta misplaced.** Subagent proposed adding the 0xF0/0xF2 4-bit-vs-8-bit color-encoding fact to `concepts/picture-compression.md`. Our existing picture-compression page documents the v3-specific 4-bit *resource-packing* compression from 3-3 — a different concept than the PICTURE *bytecode opcodes* 0xF0/0xF2. The 0xF0/0xF2 difference belongs in the future `entities/picture.md` (Group 4 territory). **Delta dropped; fact preserved as a Group 4 forward breadcrumb in the source page.**
3. **`entities/object-encryption.md` page is premature.** Subagent proposed a sub-page before the parent `entities/object.md` exists (Group 7 territory). Awkward parent-before-child situation. **Page dropped; OBJECT encryption timeline preserved as a Group 7 forward breadcrumb in the source page.**
4. **Overview control-lines delta unmotivated.** Subagent proposed touching the Control-lines paragraph of overview.md, but 2-8 doesn't discuss control lines. **Delta dropped.**
5. **Missed v2 LOGIC encryption inference.** Subagent did not capture the implication that v2 LOGIC files encrypt their text messages with Avis Durgan. Added explicit treatment in the source page and forward breadcrumb to Group 3.
6. **Wrong version count.** Subagent said "15 distinct versions" — the table has 14 rows.
7. **Spec discrepancies captured as conflicts.** The 2-8-vs-2-7 enumeration mismatch (2-7 has 2.425/2.426 missing from 2-8) and the "2.400" typo are flagged: the typo as a `> [!conflict]` callout on the command-evolution page, the enumeration mismatch as a Notes paragraph on the source page.

`(agidev, unverified)` tag usage: applied to the "2.400" typo correction (provisional reading 2.440); applied to the broader command-arg-evolution rules (no decoder code to validate against).

**Group 2 closure summary.**

Pages added across Group 2 (chapters 2-1 through 2-8): [[interpreter/overview]], [[interpreter/variables-and-flags]], [[interpreter/event-loop]], [[interpreter/memory-layout]], [[interpreter/input-parsing]], [[interpreter/command-evolution]], and [[concepts/agi-data-types]]. Eight source pages added.

Authorship snapshot for the corpus (Group 2 complete):
- 2-1, 2-2, 2-3: Peter Kelly (assumed; not directly verified against HTML).
- 2-4: Lance Ewing solo, IA, 31 August 1997.
- 2-5: Lance Ewing primary + Peter Kelly + Anders M Olsson, 3 March 1998.
- 2-6: AGDS manual translated from Russian by Vassili Bykov, IA, 31 August 1997.
- 2-7: hobbyist `mikeph@concentric.net` ("Version Control" v4.0), IA, no date.
- 2-8: Lance Ewing solo, IA, 27 January 1998.

Five of eight Group-2 chapters are explicitly IA-provenance; five are non-Peter-Kelly contributions. The "Peter Kelly's AGI Specifications" framing in CLAUDE.md is more accurately "Peter Kelly's curated AGI specifications corpus" with multiple per-chapter authors.

**Five forward-references remain dangling in [[interpreter/overview]]** after Group 2 close: `commands`, `priority-bands`, `control-lines`, `view-objects`, `debug-modes`. All five are deferred to later groups:
- `commands` and `debug-modes` → Group 3 (Logic).
- `priority-bands` and `control-lines` → Group 4 (Picture, where the priority screen is encoded) and Group 3 (Logic, where the runtime mechanics live).
- `view-objects` → Group 5 (View) and possibly Group 3.

Phase C lint will need to either resolve them once Groups 3–5 are complete or accept them as legitimately-deferred placeholders.

Group 3 should also follow up on these Group-2 breadcrumbs:
- 2-5: `set.game.id` opcode semantics; "about four AGI commands have changed argument count" (now concretized by 2-8 to {`quit`, `print.at`, `print.at.v`, unknown #176}).
- 2-6: forward-pointer to `4-3-Logic.html` (the `said` opcode's original AGDS chapter).
- 2-8: v2 LOGIC text-message encryption with Avis Durgan; PICTURE opcodes 0xF0/0xF2 4-bit-vs-8-bit color encoding.

No conflicts observed against existing pages within this ingest.

## [2026-05-10] ingest | 4-1-Logic.html

Phase B Group 3 (Logic), chapter 1 of 6 ingested.

- Added [[entities/logic]] — LOGIC resource on-disk format: 7-byte header (5-byte universal VOL header per [[entities/vol-file]] + 2-byte LE text offset); bytecode section dispatch ranges (`$00..$B5` AGI commands with `$00` doubling as `return`; `$00..$12` test condition codes; `$FC..$FF` control-flow opcodes); the four control-flow opcodes (`$FF` `if` open/close with 2-byte bracket distance, `$FE` `else/goto` with signed offset, `$FD` `not`, `$FC` `or` bracket); the `if/else` bracket-distance-inflated-by-3 rule; inner-loop encoding via `$FE` with negative offset; argument dispatch via AGIDATA.OVL bit-encoded type byte; text section structure (count + end pointer + offset table + null-terminated bodies XOR'd with "Avis Durgan"); `said` variable-argument encoding; entry-point control (`set.scan.start`/`reset.scan.start`); annotated x86 ASM decode loop from Manhunter: SF.
- Added [[sources/4-1-logic]] — chapter summary, deferrals, and notes including decoder-gap caveat, cross-key clarification (Avis Durgan vs. 128-byte loader key from 2-5), and section-citation verification (4-1's `<h3>` headers are real, unlike 2-6).
- Small delta to [[interpreter/overview]] §"The LOGIC virtual machine": added a sentence introducing the on-disk bytecode container with cross-link to [[entities/logic]] and `[4-1-Logic.html]` citation, kept the existing [[interpreter/commands]] forward-ref (still dangling, opcode table not in 4-1).
- Small delta to [[interpreter/overview]] §"Resource types": LOGIC entry no longer says "to be ingested with Group 3 — Logic"; entry sharpened to mention Avis Durgan encryption explicitly.
- Updated `wiki/index.md`: added `logic` under Entities and `4-1-logic` under Sources.

Reviewer fixes applied to the subagent proposal:

1. **v2 LOGIC text encryption framed as contrapositive inference from 2-8.** The subagent presented the Avis Durgan XOR claim as derived from 2-8's v3 "no need to encrypt" statement. Verified against the HTML: 4-1 line 302 (§THE TEXT SECTION) states the encryption directly with worked examples. Rewrote both pages to present it as a direct 4-1 spec claim that *corroborates* the 2-8 contrapositive — both sources agree. The `(agidev, unverified)` tag is preserved but reframed: it's there because there's no LOGIC decoder to test against, not because the source is unreliable.
2. **Header table conflated universal and LOGIC-specific bytes.** Subagent's 4-row header table re-documented the 5-byte VOL resource header (signature, VOL number, length) inline, duplicating [[entities/vol-file]] and creating a future-divergence risk. Restructured into a 2-row table: row 1 delegates the universal 5 bytes to [[entities/vol-file]] by cross-link; row 2 documents the LOGIC-specific 2-byte text-offset prefix. ASCII layout diagram added above the table. The spec's "seven-byte header" framing preserved with explicit "for brevity, 'the header' refers to the full 7-byte prefix" disclaimer.
3. **"(0x0006)" parenthetical was opaque.** Subagent's text-offset description said "byte offset from start of header (0x0006) where text section begins" — `(0x0006)` reads as if it's the field value (it isn't; example value is `0x02BA`). Replaced with explicit prose: "byte offset from the start of the LOGIC resource (byte 0 of the VOL resource header) at which the text section begins; also marks the end of the bytecode section. Bytecode therefore occupies bytes `7 .. text_offset - 1`."
4. **Proposed new `## LOGIC Bytecode` overview section was redundant.** Subagent proposed inserting a new section between §"Input parsing" and §"Debug modes". But overview.md already has §"The LOGIC virtual machine" (VM model) and §"Resource types" with a [[entities/logic]] mention. Folded the proposal into a one-sentence extension of §"The LOGIC virtual machine" plus a sharpened §"Resource types" entry, avoiding a third LOGIC-flavored section on the same page.
5. **Bytecode example corrected.** Subagent's "Simple `if (isset(5))`" example body looked right, but its else-block example introduced `FF 07 E7 FF 05 00` with internal-only attribution. Re-aligned the §THE LOGIC CODES walkthrough to the spec's actual Example 3 (KQ1 Room 2) with the `84 00` bracket distance, and rendered the else-block pattern abstractly to avoid spurious specifics.
6. **Section-citation verification.** Confirmed 4-1's `<h3><i>UPPERCASE</i></h3>` headers are real HTML tags before keeping `§THE HEADER` / `§THE LOGIC CODES` / `§TEST CONDITIONS` / `§THE TEXT SECTION` / `§THE ELSE COMMAND AND MORE ON BRACKETS` / `§THE 'SAID' TEST COMMAND` / `§INNER LOOPS` / `§ARGUMENTS` / `§HOW THE INTERPRETER HANDLES LOGIC CODE` / `§NEW INFORMATION ON LOGIC INTERPRETATION` citations. (Unlike 2-6's invented section names, these check out — discipline lesson held.)

`(agidev, unverified)` tag usage: applied to the page-level disclaimer (no LOGIC decoder in `resource/`); to AGIDATA.OVL argument-type byte bit-0 semantics (spec is silent); to the question of whether the message count / end pointer / offset table are themselves encrypted (spec doesn't say). Removed any reflexive tags on observations about our own code (gap notes are observations, not unverifiable spec claims).

**Decoder gap (recorded as forward-work):** validating any bytecode-level claim on [[entities/logic]] requires at minimum a 7-byte header parser, a control-flow walker honoring `$FF/$FE/$FD/$FC`, an AGIDATA.OVL-equivalent argument dispatch table, and the text-section XOR loop. The Avis Durgan XOR primitive in `util/crypto.py` is already validated against OBJECT files via [resource/objects.py] and will be directly reusable for LOGIC text decryption. This is the largest remaining decoder gap in the prototype and the natural next milestone after Group 3 ingest completes.

**Forward breadcrumbs for later Group 3 chapters (4-2..4-6):**
- Full opcode catalogue with semantics, return values, argument signatures — not in 4-1.
- `said` matching algorithm (wildcards `1` and `9999` semantics, prefix-vs-equality match) — 2-6 forward-pointed to 4-3.
- `set.game.id` opcode behavior — 2-5 breadcrumb.
- The four version-conditional argument-count mutations (`quit`, `print.at`, `print.at.v`, unknown #176) — 2-8 / [[interpreter/command-evolution]].
- v3 LOGIC header layout (4-1 confirms it differs but does not specify).

For Group 4 (Picture): PICTURE opcodes `0xF0`/`0xF2` color encoding (per 2-8 breadcrumb).

Authorship snapshot updated:
- 4-1: Lance Ewing solo, IA, 20 August 1997. (Fourth Lance-Ewing-primary chapter in the corpus, alongside 2-4, 2-5, 2-8.)

Four forward-references in [[interpreter/overview]] remain dangling: `commands` (opcode tables — deferred to later 4-x), `priority-bands`, `control-lines`, `view-objects`, `debug-modes`. (Five before this ingest; the [[entities/logic]] forward-ref under §"Resource types" was resolved.)

No conflicts observed against existing pages.

## [2026-05-10] ingest | 4-2-Logic.html

Phase B Group 3 (Logic), chapter 2 of 6 ingested. **Authoring-side reference** — 4-2 documents source-language syntax (action-command form, `if/else` with `&&`/`||`/`!`, test commands, labels/`goto`, comments, preprocessor directives, `return`), not bytecode encoding. The wiki is byte-level format only per the plan's "Out of scope" section, so 4-2 generates no new entity / interpreter pages.

- Added [[sources/4-2-logic]] — chapter summary with explicit scope-boundary framing (source language vs. bytecode), explanation of the Number-vs-Controller delta rationale, quote-mark/escape rules, said-word lookup-time semantics.
- Delta to [[concepts/agi-data-types]]: added a new "## Controller" section after "## Message" — Controller is a genuine new runtime data type introduced by 4-2 (binding between input events — menu items, key presses — and numeric IDs that LOGIC tests). The chapter's actual content on Controllers is one sentence ("Controllers are menu items and keys") plus the `c` source prefix; section preserves only that and defers `set.controller` / `set.menu` / `submit.menu` opcode semantics to later Group 3 chapters.
- Delta to [[concepts/agi-data-types]] opening: reworded "seven fundamental data types" → "eight fundamental data types" with explicit explanation of 4-2's 9-type enumeration and why we exclude Number (it's an immediate-literal addressing mode, not a distinct runtime type).
- Fix to [[concepts/agi-data-types]] §See also: broken wiki-link `[[interpreter/input-and-parsing]]` → `[[interpreter/input-parsing]]`. The 2-6 ingest log claimed to have fixed this rename but missed the See-also at the bottom of the data-types page. Caught here.
- Updated [[concepts/agi-data-types]] §See also: added [[sources/4-2-logic]] as a cross-reference for the source-syntax argument-type catalogue.
- Updated `wiki/index.md`: extended the Concepts entry for `agi-data-types` to mention controllers (now 8 types); added `4-2-logic` under Sources.

Reviewer fixes applied to the subagent proposal (one substantive miss, two framing improvements):

1. **Subagent missed the Controller delta.** Proposal verdict was "no new pages or deltas — 4-2 generates nothing because all nine parameter types are already enumerated in [[concepts/agi-data-types]]". Verification against 2-3-Interpreter.html confirmed it does **not** mention "controller" or "menu item" anywhere; our data-types page reflects 2-3's seven types. 4-2 introduces Controller as a real new runtime data type. The delta was identified during reviewer spot-check and applied.
2. **Subagent proposed a new "## Source syntax" section in [[interpreter/overview]].** Rejected: overview.md catalogues runtime VM subsystems, and source-language syntax is an authoring-layer concern (not runtime, not byte-level). Adding a section there would break the page's discipline. The source page is the right place for syntax conventions.
3. **Subagent proposed a note-style entry under "## Interpreter" in `wiki/index.md`.** Rejected as noise — the index discipline (per WIKI.md) is one line per page. Source-syntax facts live in [[sources/4-2-logic]] and are discoverable from there; the source-page index entry suffices.

`(agidev, unverified)` tag usage: applied to the inferred Controller bytecode encoding (presumed single-byte controller index per AGIDATA.OVL dispatch — 4-2 gives no bytecode-level information about controllers, and no LOGIC decoder exists in `resource/` to validate).

Section-citation verification: 4-2's `<h3><i>Title Case</i></h3>` headers are real HTML tags (`Action Commands`, `IF structures and test commands`, `Argument types`, `Labels and the goto command`, `Comments`, `Defines`, `Including files`, `More on messages`, `The return command`). Note the case difference from 4-1's `UPPERCASE` headers — different chapter, different author convention.

**Forward breadcrumbs for later Group 3 chapters (4-3..4-6):**
- Full opcode catalogue still missing — 4-2 explicitly defers: "A complete list of the commands and their argument types is available as part of AGI Specs" without identifying the chapter. The [[interpreter/commands]] forward-ref from [[interpreter/overview]] remains dangling.
- Controller opcode semantics: `set.controller`, `set.menu`, `submit.menu`, `key.pressed`, etc. — runtime binding mechanism not specified in 4-2.
- Preprocessor-directive semantics (`#define`, `#include`, `#message`) — 4-2 sketches form only; compiler-specific behavior may surface in a later chapter or remain authoring-tooling territory.

Authorship snapshot updated:
- 4-2: Peter Kelly solo (`ptrkelly@ozemail.com.au`), IA, 27 January 1998. **First directly HTML-verified Peter-Kelly-authored chapter** in the corpus (earlier ingests of 2-1/2-2/2-3 listed him as assumed-author without HTML verification; 2-5 lists him as a contributor).

Four forward-references in [[interpreter/overview]] remain dangling: `commands`, `priority-bands`, `control-lines`, `view-objects`, `debug-modes`. Unchanged from post-4-1 state.

No conflicts observed against existing pages.

## [2026-05-10] ingest | 4-3-Logic.html

Phase B Group 3 (Logic), chapter 3 of 6 ingested. **Largest Group-3 ingest** — 4-3 is the opcode catalogue, resolving the longest-standing dangling forward-reference in the wiki ([[interpreter/commands]], created at 2-1 ingest in Group 2). One new page, four cross-page deltas.

- Added [[interpreter/commands]] — full opcode catalogue with 18 test commands (`$01..$12`) and 182 action commands (`$00..$B5`), each row carrying mnemonic, declared argument count, and per-argument type signature. Organized into eleven sub-sections grouping adjacent opcodes by purpose (flow/arithmetic, rooms/LOGIC/PIC, views/screen-objects, motion/blocks, inventory/rooms, sound, print/display/screen, strings/parsing/input, input bindings, game lifecycle, late-v2 additions, eleven unknown commands). Includes argument-type legend, top-of-page table-artifact disclaimer, page-level `(agidev, unverified)` tag, and notes section covering source-prefix correspondence to 4-2, dangling-forward-ref resolution scope, and behavioral-semantics deferrals.
- Added [[sources/4-3-logic]] — chapter summary with explicit "this is the long-deferred opcode catalogue" framing, markup-artifact documentation (stray "string" cells in arg slots beyond declared count for `$3E..$71` rows), `said` opcode confirmation (`$0E` per 4-3, matches 4-1 ingest's transcription), and same-author corroboration of the "2.400" typo with 2-8.
- Delta to [[interpreter/command-evolution]]: opening paragraph now cites 4-3 as an independent source confirming all four version-conditional mutations; conflict callout rewritten to note both 2-8 and 4-3 carry the identical "2.400" string (strengthening the typo reading); See-also section updated to drop the "(Group 3, not yet ingested)" marker on [[interpreter/commands]] and add [[sources/4-3-logic]].
- Delta to [[interpreter/overview]] §"The LOGIC virtual machine": dropped "to be ingested with later Group 3 chapters" disclaimer; updated command counts from "approximately 181 / approximately 18" to concrete "182 / 18" per 4-3's authoritative tables; added [4-3-Logic.html] citation.
- Delta to [[concepts/agi-data-types]] §"Message": replaced placeholder cross-link with concrete list of message-consuming opcodes (`$65 print`, `$67 display`, `$76 get.num`, `$8F set.game.id`, `$90 log`, `$9C set.menu`, `$9D set.menu.item`, `print.at` family).
- Delta to [[concepts/agi-data-types]] §"Controller": dropped `(agidev, unverified)` tag on the bytecode-encoding inference (4-3 confirms the single-byte controller encoding via inline argument types); added enumeration of controller-consuming opcodes (`$0C controller` test; `$79 set.key`, `$9D set.menu.item`, `$9F enable.item`, `$A0 disable.item` actions).
- Updated `wiki/index.md`: added `commands` under Interpreter and `4-3-logic` under Sources.

Reviewer fixes applied to the subagent proposal (substantive — the subagent's tables contained fabricated content):

1. **Subagent fabricated `gte` and `lte` as test commands at `$0E`/`$0F`.** Verified against HTML lines 191-238: test command at `$0E` is **`said`** (variable args), at `$0F` is **`compare.strings`**. No `gte`/`lte` in the test-command range. The subagent's table was unreliable — full transcription redone from a direct HTML read of lines 21-2270.
2. **Subagent inconsistently claimed test commands ran `$01..$0C` and `$01..$10` in different places.** Actual range is `$01..$12` (18 conditions), matching 4-1's stated `$00..$12` outer range (where `$00` is unused as a test code, doubling as action-command `return`).
3. **Subagent placed `said` at `$0F` and `$0x10` in different places.** Verified: `said` is `$0E`.
4. **Subagent's mislabeled the ingest as "chapter 1 of 4" in the log draft.** Correct: chapter 3 of 6.
5. **Subagent gave only a partial action-command table with placeholder note "(Table omitted here for brevity)".** All 182 rows transcribed in full on [[interpreter/commands]] from a direct HTML read.
6. **Subagent missed the cross-reference value of the `$8F set.game.id` opcode signature.** 2-5 had a breadcrumb requesting `set.game.id` semantics — 4-3 partially answers it (source-syntax: 1 arg, `message` type), which now lives on [[interpreter/commands]] §"Quit, debug, misc" with an explicit pointer to [[sources/2-5-interpreter]] for the runtime/loader half.
7. **Subagent missed the markup-artifact issue.** The HTML has stray `<td>string</td>` cells in argument slots beyond the declared count for many `$3E..$71` rows. The declared-count column is authoritative; stray cells were dropped during transcription. Documented top-of-page on [[interpreter/commands]] and in the source page Notes.

`(agidev, unverified)` tag usage: applied at page level on [[interpreter/commands]] (no LOGIC decoder in `resource/` to validate any signature against working code); applied per-row to `???` argument types (`$9B set.upper.left`, several unknown commands) where spec itself doesn't specify; preserved on the "2.400" typo resolution.

**Dangling forward-references state.** Four remain in [[interpreter/overview]]: `priority-bands`, `control-lines`, `view-objects`, `debug-modes` (all runtime-state subsystems, not opcode dispatch — distinct from what 4-3 resolved). The [[interpreter/commands]] forward-ref previously dangling from overview, agi-data-types §Message, and command-evolution §See-also is **resolved**.

**Forward breadcrumbs for later Group 3 chapters (4-4..4-6):**
- Behavioral semantics — what each opcode actually does to the VM (mutate which slot, observe which state, when does the side effect commit relative to the event-loop step) — not in 4-3. Watch for chapters that elaborate.
- `said` matching algorithm — still distributed across 2-6 (algorithm) and 4-1 + this catalogue (bytecode encoding). Not specified in any single chapter.
- `???` argument-type resolution for `$9B set.upper.left` and the eleven `unknown*` commands. Likely requires ScummVM cross-check (post-Phase-B task).

**Forward breadcrumbs for later groups:**
- View/loop/cel data type semantics — opcode signatures use `S obj` (screen-object index, runtime VIEW instance) heavily; the underlying VIEW resource format is Group 5 territory.
- Sound opcode behavioral details (`$62 load.sound`, `$63 sound`, `$64 stop.sound`) — Group 6.
- `add.to.pic` / `add.to.pic.v` (`$7A`, `$7B`, both 7-arg, all `num` or all `var`) — PICTURE-runtime opcodes; semantics deferred to Group 4.
- `compare.strings` (`$0F`) and the v3 string-allocation count — touches the 24-vs-12 strings ambiguity from [[concepts/agi-data-types]] §"String". Whether v3 games actually use the larger allocation may show up in 4-4..4-6 or stay unresolved.

Authorship: Peter Kelly, 3 March 1998, IA-provenance. Second Peter-Kelly-primary Group-3 chapter (4-2 was first). Same date as 2-5 (Peter Kelly was a contributor there).

No conflicts observed against existing pages. The "2.400" typo cross-corroboration is captured in the conflict callout on [[interpreter/command-evolution]].

## [2026-05-10] ingest | 4-4-Logic.html

Phase B Group 3 (Logic), chapter 4 of 6 ingested. **Largest dangling-forward-ref resolution in the wiki so far** — 4-4 supplies the priority-band y-boundary table that has been dangling since 2-1.

- Added [[interpreter/priority-bands]] — NEW page documenting the 11-row y → priority auto-assignment table from `release.priority`: bands 4–14, y < 48 → 4 through 156 ≤ y < 168 → 14, with the noted non-uniformity (top band is 48 px tall; all others 12 px). Resolves the [[interpreter/priority-bands]] forward-ref originally placed by the 2-1 ingest. Cross-references to [[interpreter/control-lines]] (still pending — control-line color semantics deferred to Group 4) and [[entities/picture]] (priority screen layer; Group 4).
- Added [[interpreter/command-semantics]] — NEW page with focused high-value content (~300 lines): arithmetic edge cases (overflow/underflow/division-by-zero all `(agidev, unverified)` per Bykov's translator notes); resource auto-discard rule with mechanism unspecified; missing-command-variants table (`load.pic` asymmetry, no `load.sound.v`, no `discard.logic`/`discard.sound`); PICTURE composition ordering constraint (`load → draw → discard → ... → show`); the `new.room` 11-step procedure with full state-coordination details (var(0/1/2/4/5/16), flag(5)); `release.loop` direction → loop tables for both <4-loop and 4+-loop VIEWs; **two conflict callouts** (intra-4-4 base-point conflict between line 363 "bottom left" and line 854 "bottom right"; 4-3-vs-4-4 disagreement on `$9B set.upper.left` arity — 2 args with `???` vs 0-arg state toggle); mnemonic-variants table (`assign` vs `assignn`, `load.logic` vs `load.logics`, `right.position` vs `right.posn`, `upper.left` vs `set.upper.left`); `add.to.pic` margin rule with gap at value 4; `set.game.id` AGDS interpreter ID `TQ`; `said` algorithm corroborating 2-6 verbatim (same AGDS-Bykov source); AGDS-vs-AGI-Studio surface-syntax distinction (`if_/else_` underscore-suffixed vs `if() {}` C-like).
- Added [[sources/4-4-logic]] — chapter scope (12 numbered sections from arithmetic through "other"); informs / deferred lists; notes on AGDS-as-2-6's-same-source, mnemonic-variant decisions (canonical = 4-3 forms), and Bykov/Ewing exchanges preserved on `load.pic`, `load.sound`, missing discards, and `show.obj`.
- Delta to [[interpreter/overview]] §"Screen objects and priority bands": dropped the `(agidev, unverified — exact band boundaries and occlusion algorithm specified in later chapters)` qualifier — boundaries now documented in [[interpreter/priority-bands]]; occlusion algorithm still deferred to Group 4. Added 4-4-Logic.html citation alongside the existing 2-1 citation.
- Delta to [[interpreter/commands]] Notes section: behavioral-semantics pointer updated from "distributed across later Group 3 and Group 4/5 chapters" to a concrete cross-link to [[interpreter/command-semantics]]; new paragraph on `$9B set.upper.left` flagging the 4-4 conflict.
- Delta to [[interpreter/variables-and-flags]]: var(0/1/2/16) and flag(5) entries cross-link the `new.room` procedure with the specific step that touches each slot; var(9) entry cross-links the `said` algorithm and notes 4-4's corroboration of 2-6.
- Updated `wiki/index.md`: added `command-semantics` and `priority-bands` under Interpreter; added `4-4-logic` under Sources.

Reviewer fixes applied to the subagent proposal (the subagent produced ~2200 words of proposed `command-semantics.md` content with substantive errors):

1. **Three opcode-number errors in the subagent's body.** `clear.text.rect` placed at `$6A` (correct: `$9A`; `$6A` is `text.screen`); `close.window` placed at `$A5` (correct: `$A9`; `$A5` is `mul.n`); `upper.left` renamed and given `$A9` (correct: opcode is `$9B set.upper.left` per 4-3). Subagent's draft was not adopted as the basis for command-semantics.md — instead, the page was written from direct HTML reads with every opcode reference cross-validated against [[interpreter/commands]].
2. **Subagent's "comprehensive prose dump" approach.** The subagent proposed re-transcribing ~150 opcodes in wiki-page form, duplicating the chapter without adding value. Substituted a "focused page" approach: surface only items that are non-obvious from [[interpreter/commands]]'s signatures (multi-step procedures, edge cases, conflicts, hidden runtime constraints, mnemonic variants), and direct readers to `AGI_Specifications/Specifications/4-4-Logic.html` for full per-opcode prose. Reduces page size from ~2200 to ~300 lines without losing the high-value content.
3. **Subagent missed the priority-band y-table as a dangling-forward-ref resolution.** The subagent did not propose a dedicated `priority-bands.md` page despite 4-4 supplying the complete eleven-row table. The forward-ref had been dangling since the 2-1 ingest. New dedicated page created.
4. **Subagent missed the intra-4-4 base-point conflict.** Verified at HTML lines 363 ("bottom left") and 854 ("bottom right"). Conflict callout added to command-semantics.md.
5. **Subagent missed the `$9B set.upper.left` argument-count conflict** between 4-3 (2 args, `???`) and 4-4 (0-arg state toggle). Both verified directly. Conflict callout added; provisional reading favors 4-4's 0-arg form.
6. **Subagent missed the `add.to.pic` margin gap at value 4.** Verified at HTML line 509: spec covers `margin ∈ {0,1,2,3}` and `margin > 4`, leaving `margin == 4` unspecified. Documented.
7. **Subagent missed AGDS-vs-AGI-Studio surface-syntax distinction.** 4-4 uses `if_/else_/not_/or_` with trailing underscores (AGDS authoring convention); 4-2 uses `if() {}` C-like syntax (AGI Studio convention). Both compile to the same bytecode. Documented in command-semantics page-level caveats.
8. **Subagent claimed the `said` algorithm in 4-4 was a new corroboration.** It is corroboration of *the same Bykov AGDS translation* that 2-6 also draws from — same source, not independent. This nuance was added explicitly to [[sources/4-4-logic]] §Notes and to the said-algorithm section.
9. **Subagent missed mnemonic-variants opportunity.** 4-4 consistently uses slightly different mnemonics than 4-3 for the same opcodes. Cross-reference table added so future decoders can match either form.

`(agidev, unverified)` tag usage and resolutions:

- Applied: arithmetic edge cases (4 unresolved questions); resource-auto-discard mechanism; margin = 4 gap; both conflict callouts; the priority-bands page (process tag — no working renderer).
- Removed: the `(agidev, unverified — exact band boundaries and occlusion algorithm specified in later chapters)` qualifier from [[interpreter/overview]] §"Screen objects and priority bands" (boundaries now resolved).
- Preserved unchanged: var(9), var(17), var(24) translator-note flags in [[interpreter/variables-and-flags]] (4-4 corroborates 2-6 for var(9) but both come from the same Bykov source; consistency between translations is not validation against working code).

**Dangling forward-references state.** After this ingest, three remain in [[interpreter/overview]]: `control-lines`, `view-objects`, `debug-modes`. (Four before this ingest; `priority-bands` is now resolved.) `control-lines` partially touched by 4-4 in passing (priority-0 unconditional barrier, priority-1 conditional) but not all four colors documented — likely needs Group 4 (PICTURE). `view-objects` partially touched by 4-4 (direction → loop tables) but the full screen-object model is Group 5 (VIEW) territory. `debug-modes` minimally touched (trace.on / trace.info) but not enough for a dedicated page.

**Forward breadcrumbs for later chapters / groups:**

- Group 4 (PICTURE): per-pixel occlusion algorithm; control-line colors (black/blue/green/cyan); the relationship between `add.to.pic` runtime composition and PICTURE bytecode opcodes (`0xF0`/`0xF2` per 2-8 breadcrumb).
- Group 5 (VIEW): full screen-object model behind the direction → loop tables; base-point semantics resolution (which corner is the cel base — 4-4 contradicts itself).
- Group 3 (4-5, 4-6): may resolve resource-auto-discard mechanism details; may resolve the `$9B set.upper.left` arity conflict; may add 24-vs-12-strings v3 detail.
- Post-Phase-B: ScummVM cross-check for the four arithmetic edge cases (overflow/underflow/division-by-zero) and the eleven `unknown*` opcodes.

Authorship: AGDS manual translated from Russian by Vassili Bykov (`vbykov@cam.org`), annotated by Lance Ewing, IA, 4 December 1997. **Third AGDS-Bykov chapter in the corpus** (after 2-6 and the implicit AGDS-style sections in earlier chapters). Three of four Group-3 chapters so far have non-Peter-Kelly primary authors.

No conflicts observed beyond the two surfaced ones (intra-4-4 base-point; 4-3-vs-4-4 `$9B` arity).

## [2026-05-10] ingest | 4-5-Logic.html

Phase B Group 3 (Logic), chapter 5 of 6 ingested. **Sources-only ingest** — 4-5 is a KQ4 Room 7 code-walkthrough (five BOOK-pseudo-code vs. GAME-bytecode samples), not a format-specification chapter. Pattern matches earlier sources-only ingests (3-4 Sample Code, 2-5 loader, 2-7 versions).

- Added [[sources/4-5-logic]] — chapter summary; author-vs-compiler differences captured as authoring context (named-constants vs. numeric-indices via `#define`; `||` and `&&` boolean operators decomposed at compile-time to bytecode control flow; named variables vs. var-indexed access); spot-checked all opcodes against [[interpreter/commands]] with no conflicts; "anonymous chapter" framing (no HTML byline); IA-provenance date (31 August 1997) matches 2-4 and 2-6's dates exactly, suggesting same-session IA extraction.
- Small delta to [[sources/4-2-logic]]: added a "Said synonym-group syntax" Notes paragraph documenting the `said(OPEN, DOOR||DOORS||DOORWAY||DOORWAYS)` form observed in 4-5's GAME samples (alternative spellings sharing one WORDS.TOK code; `||` is source sugar with no bytecode effect). 4-2 itself does not document this convention; 4-5 surfaced it via real-game disassembly.
- Updated `wiki/index.md` with `4-5-logic` under Sources.

Reviewer fixes applied to the subagent proposal (the subagent's framing was correct but had three local errors):

1. **Subagent misread the smoke sample.** Claimed "`ignore.horizon` → `ignore.objs`" (substitution). Verified at HTML lines 28-49: GAME version *adds* `ignore.objs(7)` and `set.priority(7, 5)` to the BOOK version while keeping `ignore.horizon(7)`. The change is two new opcodes, not a substitution. Source page corrects this.
2. **Subagent attributed authorship to Peter Kelly.** Inferred from HTML meta-keywords, but the actual byline (line 15) has no author named — only the date and IA-provenance annotation. Source page records the chapter as anonymous, contrasting with the named authorship of 4-1/4-2/4-3/4-4.
3. **Subagent missed the `||` synonym-group syntax** in the GAME-form `said` samples. This is a real AGI Studio source-syntax convention not explicitly described in 4-2 itself; surfaced as a Notes delta to [[sources/4-2-logic]] with cross-reference back to 4-5.

`(agidev, unverified)` tag usage: no changes. 4-5 is exemplary, not specification — it does not introduce claims to validate or invalidate. All opcodes referenced exist with consistent argument counts in [[interpreter/commands]].

**Open items from the Group-3 dossier**: none closed by 4-5. The eleven unknown commands `$AA..$B5`, the `$9B set.upper.left` arity conflict, the intra-4-4 base-point conflict, the `add.to.pic` margin = 4 gap, the arithmetic edge cases, the v3 LOGIC header layout, the 24-vs-12 strings ambiguity, the control-line color semantics, view-objects subsystem mechanics, debug-modes details, and the resource auto-discard mechanism all remain pending. 4-5's value is forward-looking (post-Phase-B): once a LOGIC decoder lands in `resource/`, these five samples become round-trip test cases.

**Dangling forward-references state.** Three remain in [[interpreter/overview]]: `control-lines`, `view-objects`, `debug-modes`. Unchanged from post-4-4.

Authorship: anonymous within chapter; IA-provenance 31 August 1997. **Same-session IA extraction with 2-4 and 2-6** (both also IA, 31 August 1997) is plausible.

No conflicts observed against existing pages. The `||` synonym-group syntax is a documentation gap in 4-2 rather than a conflict; the delta to [[sources/4-2-logic]] fills the gap rather than flagging contradiction.

## [2026-05-10] ingest | 4-6-Logic.html

Phase B Group 3 (Logic), chapter 6 of 6 ingested. **Sources-only ingest, closes Group 3.** 4-6 is a 55-line bibliographic reference table (parallel to [[sources/3-4-files]] at the Files-group level): a 5-row `<table>` pointing at source files vendored under `AGI_Specifications/Code/`. No HTML byline; no date annotation; no format claims.

- Added [[sources/4-6-logic]] — chapter scope, file-by-file attribution table (Lance Ewing: `logic.c`, `logic.h`, `agifiles.c`, `agifiles.h`; Peter Kelly: `agicommands.pas`), post-Phase-B validation roles (`logic.c` plausibly informed 4-1's bytecode spec, `agicommands.pas` plausibly informed 4-3's opcode table), and explicit anonymity framing.
- Verified all five referenced files exist at `AGI_Specifications/Code/`.
- Updated `wiki/index.md` with the new source entry and a "closes Group 3" marker.

Reviewer fixes applied to the subagent proposal:

1. **Subagent inferred Peter Kelly as chapter author** from meta-keywords. Same mistake as 4-5: the HTML byline is bare (no chapter-level author). Source page records the chapter as anonymous at chapter level with per-row attribution only.
2. **Subagent invented an "IA-corpus format" provenance line.** The chapter HTML carries no Internet-Archive annotation at all — unlike 2-4, 2-6, 4-1, 4-5 which explicitly state "Retrived from the Internet Archive". The 4-6 source page records "No IA annotation in HTML" honestly rather than fabricating provenance.

No new conflicts. All five referenced source files exist; no opcode-table cross-reference required (4-6 contains no opcode mentions).

---

## Group 3 closure summary

**Phase B Group 3 (Logic) is complete.** All six chapters ingested on 2026-05-10. Group 3 contributed the bulk of the LOGIC subsystem documentation and resolved the longest-standing dangling forward-reference in the wiki ([[interpreter/commands]], created in the 2-1 ingest).

**Pages added across Group 3:**

- [[entities/logic]] — LOGIC resource on-disk format (4-1).
- [[interpreter/commands]] — full opcode catalogue, 18 test + 182 action (4-3).
- [[interpreter/command-semantics]] — selected behavioral semantics + conflicts (4-4).
- [[interpreter/priority-bands]] — y → priority eleven-band auto-assignment (4-4).
- Six source pages: [[sources/4-1-logic]] through [[sources/4-6-logic]].

Plus deltas to existing pages: [[interpreter/overview]] (LOGIC VM model concretized, priority-bands resolved); [[interpreter/command-evolution]] (4-3 corroboration of 2-8; sharpened "2.400" typo callout); [[concepts/agi-data-types]] (Controller section added by 4-2; opcode-consumer lists for Message and Controller added by 4-3; broken See-also link fixed); [[interpreter/variables-and-flags]] (var(0/1/2/9/16) and flag(5) cross-linked to new.room and said procedures); [[sources/4-2-logic]] (`||` said-synonym-group syntax noted from 4-5).

**Dangling forward-references state.** Three remain in [[interpreter/overview]] after Group 3 close: `[[interpreter/control-lines]]`, `[[interpreter/view-objects]]`, `[[interpreter/debug-modes]]`. One (`[[interpreter/priority-bands]]`) was resolved by 4-4; one (`[[interpreter/commands]]`) was resolved by 4-3. Phase C lint will need to accept the remaining three as legitimately-deferred placeholders (Groups 4/5 will resolve `control-lines` and `view-objects`; `debug-modes` may remain a thin section in [[interpreter/overview]] without a dedicated page unless later chapters supply more content).

**Open items unresolved at Group 3 close** (tracked across the ingest log; expected resolution sources noted):

1. **Eleven unknown commands `$AA..$B5`** (`unknown170..unknown181`) — Group 3 did not identify them. Resolution requires ScummVM `engines/agi/op_*.cpp` cross-check or AGI Studio source (post-Phase-B).
2. **`$9B set.upper.left` arity conflict** — 4-3 says 2 args (`???`), 4-4 says 0-arg state toggle. Provisional reading favors 4-4. Conflict callout on [[interpreter/command-semantics]]. May resolve via Group 5 (VIEW) if `upper.left` is a VIEW-rendering concern, or post-Phase-B.
3. **Intra-4-4 base-point conflict** — line 363 says cel base is bottom-left; line 854 says bottom-right. Conflict callout on [[interpreter/command-semantics]]. Likely resolved by Group 5 (VIEW), which specifies the cel coordinate system.
4. **`add.to.pic` margin = 4 gap** — spec covers `{0,1,2,3}` (priority-margin rectangle) and `> 4` (no margin); leaves `== 4` undefined. May resolve via Group 4 (PICTURE) if margin semantics are PICTURE-resource-level.
5. **Arithmetic edge cases** (`addn`/`addv` overflow, `subn`/`subv` underflow, `muln`/`mulv` overflow, `divn`/`divv` division by zero) — Bykov translator notes flagged all four as unspecified. Resolution requires ScummVM cross-check or instrumented testing on original interpreter binary (post-Phase-B).
6. **v3 LOGIC header layout** — 4-1 confirms v3 differs from v2's 7-byte header but does not specify the v3 layout. May resolve via Group 4/5/6 (which use v3 resource formats) or remain open until ScummVM cross-check.
7. **24-vs-12 strings in v3** — [[concepts/agi-data-types]] §"String" notes the spec itself is unsure whether v3 games actually use the larger allocation. Empirical enumeration of v3 games via [[sources/2-7-interpreter]] grounds the abstract category but doesn't resolve usage. Post-Phase-B.
8. **Resource auto-discard mechanism** — 4-4 documents the rule ("all resources loaded after an unloaded one are also unloaded") but not the tracking mechanism. May surface in Group 4/5 when PICTURE/VIEW lifecycle is documented, or in [[interpreter/memory-layout]] if [[sources/2-4-interpreter]] re-read reveals it.
9. **Control-line color semantics** (black/blue/green/cyan) — 4-4 touched priority-0 (unconditional barrier) and priority-1 (conditional barrier) but not the full color set. Awaits Group 4 (PICTURE), which encodes the priority screen.
10. **View-objects subsystem mechanics** — 4-4 supplied direction → loop tables but not the full screen-object state model. Awaits Group 5 (VIEW).
11. **Debug-modes details** — 4-4 minimally touched `trace.on`/`trace.info`/Scroll-Lock activation. May remain thinly documented without a dedicated chapter.

**Conflicts in the wiki at Group 3 close** (preserved as `> [!conflict]` callouts):

- **"2.400" version-string typo** in [[interpreter/command-evolution]] — replicated by both 2-8 and 4-3, strengthening typo reading. Provisional resolution: 2.440. Post-Phase-B ScummVM check.
- **`$9B set.upper.left` arity** in [[interpreter/command-semantics]] and [[interpreter/commands]] §Notes — 4-3 vs 4-4 disagreement, see open item #2 above.
- **Intra-4-4 base-point** in [[interpreter/command-semantics]] §"Base-point semantics" — same chapter, two contradictory locations, see open item #3.
- **`add.to.pic` margin = 4 gap** in [[interpreter/command-semantics]] §`add.to.pic` — see open item #4.

**Authorship snapshot for the corpus (Group 3 complete):**

- 2-1, 2-2, 2-3: Peter Kelly (assumed; not HTML-verified).
- 2-4: Lance Ewing solo, IA 31 Aug 1997.
- 2-5: Lance Ewing primary + Peter Kelly + Anders M Olsson, 3 Mar 1998.
- 2-6: AGDS / Vassili Bykov, IA 31 Aug 1997.
- 2-7: hobbyist `mikeph@concentric.net`, IA, no date.
- 2-8: Lance Ewing solo, IA 27 Jan 1998.
- 3-1, 3-2, 3-3, 3-4: Peter Kelly (3-4 is also a bibliographic table).
- 4-1: Lance Ewing solo, IA 20 Aug 1997.
- 4-2: Peter Kelly solo, IA 27 Jan 1998. **First HTML-verified Peter Kelly chapter.**
- 4-3: Peter Kelly solo, IA 3 Mar 1998.
- 4-4: AGDS / Vassili Bykov / Lance Ewing, IA 4 Dec 1997. **Third Bykov-AGDS chapter** (the others are 2-6 and the AGDS-influenced 4-5).
- 4-5: anonymous, IA 31 Aug 1997. Same-session extraction with 2-4 and 2-6.
- 4-6: anonymous (per-row author cells only), no date.

The "Peter Kelly's AGI Specifications" framing in CLAUDE.md describes the corpus curator, not most chapter authors. Lance Ewing is primary on 4 chapters; Vassili Bykov on 2 (translations); Peter Kelly on 3 (4-2/4-3/3-x); hobbyist contributions on 2; anonymous on 2.

**Phase B status after Group 3 close:** Groups 1 (Files, complete) and 2 (Interpreter, complete) and 3 (Logic, complete) done. Groups 4 (PICTURE), 5 (VIEW), 6 (Sound), 7 (Other), 8 (Intro/Info) remain. Next chapter: `5-1-PICTURE.html` (Group 4, chapter 1 of 3).

## [2026-05-10] ingest | 5-1-PICTURE.html

Phase B Group 4 (PICTURE), chapter 1 of 3 ingested. **Opens Group 4.** First split-subagent ingest (two parallel Explore agents, disjoint scopes — format-bytes and rendering-semantics) per the plan's "split if a chapter risks ballooning past ~3K words" risk-mitigation. Worked cleanly: the two halves produced non-overlapping proposals and each came in well under 2500 words.

- Added [[entities/picture]] — full PICTURE bytecode opcode catalogue (`0xF0..0xFF`): set-visual-color, disable-visual, set-priority-color, disable-priority, Y/X corner, absolute line, relative line (with sign-magnitude displacement layout for `0xF7`), flood fill, set pen style, plot with pen (with solid/splatter argument-grouping), reserved range `0xFB..0xFE`, terminator `0xFF`. Coordinate encoding (160×168 logical pixel frame). Pen-style byte layout (splatter bit / shape bit / 3-bit size; visual extent `2·size+1`). Verbatim transcription of the 32-byte splatter-texture bit array and the 128-entry offset table. Screen initialization (visual → white 15; priority → red 4). Wrap-at-255 splatter quirk. Page-level `(agidev, unverified)` (no decoder in `resource/`).
- Added [[interpreter/control-lines]] — NEW page resolving the long-dangling `[[interpreter/control-lines]]` forward-ref originally placed by the 2-1 ingest into [[interpreter/overview]]. Four-color table with EGA palette mapping (black=0 barrier, blue=1 conditional barrier, green=2 alarm, cyan=3 surface confinement). Search-downwards algorithm for priority recovery under a control pixel, with KQ1 room 20 cited as the canonical visual-artifact case. Flood-fill / control-line interaction. SCI-divergence note. Page-level `(agidev, unverified)` process tag.
- Added [[concepts/screen-layers]] — NEW page for the visual / priority dual-screen model. 160×168 logical pixel frame, 320×200 doubled-horizontal display. Per-screen encoding (visual = EGA color, priority = 0..3 control / 4..14 band / 15 unused). Initial state (white visual / red priority). Drawing-mode flags and common-pattern recipes. Object composition / occlusion stub with explicit deferral (occlusion algorithm still open). SCI-divergence note. Shared-primitive page — will be extended by Group 5 (VIEW) from the screen-object side.
- Added [[sources/5-1-picture]] — chapter scope; informs / deferred lists; authorship (Lance Ewing, IA, 5 December 1997, Trivette-adaptation note); meta-keywords trap explicitly called out (HTML keywords list "peter kelly" but byline is Lance Ewing only); open-items resolution table.
- Delta to [[concepts/picture-compression]] — added "Relation to PICTURE bytecode dispatch" section clarifying that decompression precedes opcode dispatch (no compressed-vs-expanded ambiguity for the opcode catalogue).
- Delta to [[interpreter/overview]] §"Screen objects and priority bands" — occlusion-deferral pointer updated to cite [[concepts/screen-layers]] and explicitly note that 5-1 documents screen-layer structure and search-downwards but not the object-vs-screen comparison procedure.
- Delta to [[interpreter/overview]] §"Control lines" — added priority indices to each color (black=0, blue=1, green=2, cyan=3); removed the `(agidev, unverified — exact constraint semantics deferred to [[interpreter/control-lines]])` qualifier on cyan (now fully documented); cited 5-1 alongside existing 2-1 citation; added pointer paragraph to the new control-lines page.
- Delta to [[interpreter/overview]] §"Resource types" — removed `(to be ingested with Group 4 — Picture)` deferral on the PICTURE entry; added pointer to [[concepts/screen-layers]].
- Updated `wiki/index.md`: added `entities/picture`, `concepts/screen-layers`, `interpreter/control-lines`, `sources/5-1-picture` under their respective sections; the 5-1-picture entry includes the "Opens Group 4" marker symmetric with 4-6's "closes Group 3".

Split-subagent quality (first run of the parallel pattern):

- **Format-bytes subagent (A)** — Substantively correct. Used the visible byline rather than HTML meta-keywords (this confirms the Group-3 lesson is generalizable — the meta-keywords trap is real on 5-1 as well). All opcode hex values cross-validated against the chapter and against existing wiki pages. The `0xF7` displacement bit-layout and pen-style byte layout are internally consistent across the table summary and the detailed sections. Splatter-texture tables transcribed verbatim. Minor cleanups during apply: smoothed the sign-magnitude prose for clarity; no factual corrections needed.
- **Rendering-semantics subagent (B)** — Substantively correct on color semantics, search-downwards, and SCI-divergence framing, but **two dimension errors in the proposed screen-layers.md** required in-place fixing during apply: claimed "320 pixels wide and 200 pixels tall in the on-disk PICTURE resource" (the resource is bytecode, not a pixel grid; the logical frame is 160×168 with display-time horizontal doubling to 320×200). Corrected to 160×168 logical, with the doubling and the 168-vs-200 consistency-with-[[interpreter/priority-bands]] explicit. Also softened the forward-promise in control-lines.md ("documented in [[interpreter/commands]]") to "behavioral binding surfaces in subsequent Group 4/5 chapters; not yet pinned" — `commands.md` does not specifically document blue/green opcode bindings, so the original wording would have been a dead promise.

Main session verified the byline directly (40-line targeted read of 5-1-PICTURE.html top-of-file before applying any wiki edits) per reviewer concern #3 above. Author: Lance Ewing `<be@ihug.co.nz>`, last updated 5 December 1997, IA-provenance with original "Retrived" typo preserved. The Trivette adaptation note is verbatim from line 19.

`(agidev, unverified)` tag usage:

- Applied (page-level, process tag): [[entities/picture]], [[interpreter/control-lines]], [[concepts/screen-layers]] — no PICTURE/control-line/renderer code in `resource/` to validate against.
- Applied (per-claim): wrap-at-255 splatter quirk; sign-bit polarity of `0xF7` displacements (inferred from chapter's worked example).
- Removed: the `(agidev, unverified — exact constraint semantics deferred to [[interpreter/control-lines]])` qualifier from the cyan-line bullet in [[interpreter/overview]] §"Control lines" (now resolved in the dedicated page).

**Dangling forward-references state.** After this ingest, two remain in [[interpreter/overview]]: `view-objects`, `debug-modes`. (Three before this ingest; `control-lines` is now resolved.) `view-objects` awaits Group 5 (VIEW). `debug-modes` may remain a thin section in [[interpreter/overview]] without a dedicated page unless later chapters supply more content (4-4 minimally touched it; no other Group-3 chapter expanded it).

**Open items state (carried from Group 3 closure summary, updated):**

| # | Item | Status after 5-1 |
|---|------|-------------------|
| 1 | Eleven unknown commands `$AA..$B5` | Unchanged. Awaits post-Phase-B ScummVM check. |
| 2 | `$9B set.upper.left` arity conflict (4-3 vs 4-4) | Unchanged. May resolve in Group 5 (VIEW). |
| 3 | Intra-4-4 base-point conflict (bottom-left vs bottom-right) | Unchanged. 5-1 doesn't discuss cel base-points. Deferred to Group 5. |
| 4 | `add.to.pic` margin = 4 gap | Unchanged. 5-1 doesn't discuss `add.to.pic`'s LOGIC-side margin parameter; may be a 4-4 spec oversight rather than a PICTURE-side concern. |
| 5 | Arithmetic edge cases | Unchanged. Awaits post-Phase-B. |
| 6 | v3 LOGIC header layout | Unchanged. May resolve via Group 4/5/6 v3 framing or post-Phase-B. |
| 7 | 24-vs-12 strings in v3 | Unchanged. Post-Phase-B. |
| 8 | Resource auto-discard mechanism | Unchanged. |
| 9 | **Control-line color semantics (black/blue/green/cyan)** | **RESOLVED.** All four colors documented in [[interpreter/control-lines]] with EGA-palette mapping. |
| 10 | View-objects subsystem mechanics | Unchanged. Awaits Group 5. |
| 11 | Debug-modes details | Unchanged. |

New open items introduced by 5-1:

- **Per-pixel occlusion algorithm.** 5-1 documents the screen-layer structure and the search-downwards rule for *recovering* a band value under a control pixel, but not the object-vs-screen comparison procedure that drives screen-object visibility. Deferred to Group 5 (VIEW) or ScummVM.
- **Object-vs-control-line interaction.** When an object pixel lands on a control-line position, behavior is unspecified (search-downwards applies to recovering priority for *non-object* purposes).
- **Wrap-at-255 splatter quirk.** Documented as `(agidev, unverified)`; needs decoder cross-check.
- **Sign-bit polarity of `0xF7` displacements.** Inferred from chapter example; needs cross-check.
- **Opcodes `0xFB..0xFE`.** "Unused in most AGI games" with no enumeration.

Authorship: Lance Ewing solo, IA, 5 December 1997. Same author and same IA-extraction window as [[sources/4-4-logic]] (which was AGDS/Bykov-primary with Ewing annotation). Consistent with Ewing's `logic.c` / `agifiles.c` work listed in [[sources/4-6-logic]] §Bibliographic table — Ewing as the PICTURE/LOGIC pairing author across the corpus.

No conflicts observed against existing wiki content. Cyan-confinement semantics from 2-1 are corroborated. The control-line-priority numeric mapping (black=0, blue=1, green=2, cyan=3) is consistent with the priorities-0–3-reserved note already in [[interpreter/priority-bands]] line 7 (the page noted "priority 0 = unconditional barrier, priority 1 = conditional barrier, priority 2/3 = other control roles" — 5-1 fills in the green=2, cyan=3 specifics).

## [2026-05-10] ingest | 5-2-PICTURE.html

Phase B Group 4 (PICTURE), chapter 2 of 3 ingested. **Corroborating-source ingest, no new pages.** 5-2 is the AGDS-manual's parallel documentation of the same PICTURE format that 5-1 already established; the value is independent corroboration plus one refinement on `0xF8`'s target-selection rule.

- Added [[sources/5-2-picture]] — chapter scope, authorship (Vassili Bykov translator, AGDS, IA, 27 January 1998), open-items table, the "fourth Bykov/AGDS chapter" framing, the shared 27-January-1998 IA-extraction date with [[sources/4-2-logic]] and [[sources/2-8-interpreter]] (three chapters from three authors uploaded the same day).
- Delta to [[entities/picture]] — added "Flood-fill target rule (`0xF8`)" subsection with 5-2's more-specific wording on what `0xF8` chooses to fill (white-on-visual when visual-draw enabled and color ≠ 15; priority-4-on-priority when visual-draw cancelled; both-screens simultaneous when both enabled). Added Notes paragraph documenting the AGDS "dot parameters / dot plotting" terminology for `0xF9`/`0xFA` (vs 5-1's "pen" framing); same bytecode, different framing.
- Delta to [[concepts/screen-layers]] §"Initial state" — added 5-2 corroboration: "Initially all pixels of the background are white and priority 4".
- Delta to [[interpreter/control-lines]] §"Color semantics" — added 5-2 corroboration of the four-color mapping with the "alarm barrier" wording note for green.
- Updated `wiki/index.md` with `5-2-picture` under Sources.

Reviewer fixes applied to the subagent proposal:

1. **Recategorized the dot-vs-pen terminology divergence** from `> [!conflict]` callout to a Notes paragraph. Not a contradiction; both descriptions match the same bytecode; the framing difference is reader-aid material rather than wiki-conflict material. Keeps the conflicts surface (currently four callouts across the wiki) genuinely about contradictions.
2. **Promoted the `0xF8` flood-fill refinement** from a cell-text inline note in the opcode table to a dedicated short subsection ("Flood-fill target rule (`0xF8`)") in [[entities/picture]]. The refinement is a real semantics clarification, not a table-cell footnote, and several pages (control-lines, screen-layers) link to "flood fill" — they now have a more specific anchor target.

Subagent quality: substantively correct, byline verified directly in the proposal (line 20 quoted verbatim: "Translated from Russian by Vassili Bykov"), meta-keywords trap caught and explicitly called out (the third live confirmation after 5-1, 4-5, 4-6 — pattern is reliable now). All opcode hex values cross-validated against [[interpreter/commands]] and [[entities/picture]]. No fabricated opcodes, no inferred authorship.

`(agidev, unverified)` tag usage: no changes. 5-2 introduces no new claims requiring tagging; the existing page-level tags on [[entities/picture]], [[interpreter/control-lines]], [[concepts/screen-layers]] continue to apply (no PICTURE decoder in `resource/`).

**Independent corroboration question raised by the subagent.** 5-1 (Lance Ewing English-original) and 5-2 (AGDS Russian-original via Bykov translation) agree on init colors, control-line colors, opcode catalogue, and flood-fill behavior. The subagent suggested this might warrant downgrading the page-level `(agidev, unverified)` process tag on [[entities/picture]]. Reviewer reading: both sources are agidev-corpus regardless of authorship variety; the process tag tracks "no working decoder in `resource/` to validate against", not "single-source claim". Tag stays. Phase C lint can revisit if a per-claim downgrade is justifiable for the specific claims that both sources independently corroborate.

**Dangling forward-references state.** Unchanged from post-5-1: two remain in [[interpreter/overview]] (`view-objects`, `debug-modes`). 5-2 does not introduce or resolve forward-refs.

**Open items state.** Unchanged from post-5-1; 5-2 resolved nothing new. All eleven Group-3 carry-forwards + 5-1's five new items + Group-3 items #3 / #4 remain open. The `0xFB..0xFE` reserved-range question now has corroborating *absence* from a second source (5-2's A.2.1 catalogue also ends at `0xFF`) — strengthens the reading that these opcodes are genuinely unused rather than just under-documented.

**Bykov/AGDS corpus tally.** Now four chapters from this source family:
- [[sources/2-6-interpreter]] — input preprocessing and `said` semantics, IA 31 August 1997.
- [[sources/4-4-logic]] — LOGIC command-set prose, IA 4 December 1997 (Bykov primary, Lance Ewing annotations).
- [[sources/5-2-picture]] — PICTURE format, IA 27 January 1998.
- (Plus AGDS-style sections influencing 4-5's KQ4 sample code per its noted "AGDS-style" framing.)

The AGDS manual is now confirmed as a parallel canonical source for AGI internals — not a single-chapter outlier. Worth noting in any future cross-source consolidation that AGDS material is at least as authoritative as Lance Ewing's English-original chapters; both predate the public ScummVM AGI implementation.

**Three-author 27-January-1998 IA-extraction window.** [[sources/2-8-interpreter]] (Lance Ewing), [[sources/4-2-logic]] (Peter Kelly), and [[sources/5-2-picture]] (Vassili Bykov / AGDS) all share the same upload date. Three different authors, three different topics, uploaded the same day — suggests a coordinated late-January-1998 preservation effort by an unidentified curator. Worth noting if a Phase C cross-source consolidation surfaces patterns that line up with this window.

No conflicts observed against existing wiki content. Independent corroboration of init colors, control-line color mapping, and opcode catalogue. The dot-vs-pen terminology is divergent framing, not contradiction.

## [2026-05-10] ingest | 5-3-PICTURE.html

Phase B Group 4 (PICTURE), chapter 3 of 3 ingested. **Closes Group 4.** 5-3 is the "Sample Code" chapter — a thin HTML pointer to two vendored C files at `AGI_Specifications/Code/`. The substance lives in the code: `showpic.c` (650 lines, Allegro-based PICTURE viewer by Lance Ewing) and `picv3-v2.c` (67-line v3→v2 transcoder, also Ewing). This ingest is structurally different from 5-1/5-2: the subagent read both C files and reported algorithm-level findings rather than chapter prose.

**Significant validation-status change.** Prior to 5-3, [[entities/picture]] and [[concepts/screen-layers]] carried page-level `(agidev, unverified)` banners on the premise "no PICTURE decoder in `resource/` to validate against". 5-3 surfaced that `showpic.c` IS a working PICTURE decoder — just vendored at `AGI_Specifications/Code/` rather than built into andromeda. The page-level banners were replaced with per-claim verification citations distinguishing code-verified claims from genuinely-unverified claims. [[interpreter/control-lines]] retains its page-level tag (showpic.c is a pic viewer, not a game runtime — it doesn't decode control-line semantics).

- Added [[concepts/picture-rendering]] — NEW page documenting the rendering algorithms code-verified against showpic.c: additive-fixed-point line drawing with direction-sensitive rounding (lines 191-231); BFS flood-fill with 4000-entry queue (lines 249-293); brush plotting with precomputed circle/rectangle masks (lines 305-340); splatter texture masking with wrap-at-255 (lines 425-478). This is the page that captures what 5-1 deliberately punted on as "chapter pseudocode is the source of truth" — except the source of truth is showpic.c, not pseudocode.
- Added [[sources/5-3-picture]] — chapter scope (code-pointer chapter, no specification prose), authorship (anonymous chapter byline / Lance Ewing on both files, "Lange Ewing" typo on picv3-v2.c noted), the **fifth confirmed meta-keywords trap** (peter-kelly keyword vs. Ewing actual authorship), open-items resolution table, and the AGI_Specifications/Code/-as-validation-surface framing.
- Delta to [[entities/picture]]: page-level `(agidev, unverified)` banner replaced with a verification-status banner pointing to showpic.c; per-claim code-verified citations added for coordinate encoding (`[showpic.c:113-114]`), `0xF7` sign-bit polarity (`[showpic.c:369-372]`, **previously inferred from a single worked example, now resolved**), wrap-at-255 splatter quirk (`[showpic.c:428-429]`), and `0xFB..0xFE` reserved range (`[showpic.c:627]`); Implementation-guidance section now cross-links [[concepts/picture-rendering]] for the three items 5-1 punted on; new "Reference implementation" section listing showpic.c line ranges for opcode dispatch / line drawing / flood fill / pen plotting / splatter.
- Delta to [[entities/picture]] §"Splatter texture data": **new `> [!conflict]` callout** documenting a 4-position discrepancy in the splatter offset table between 5-1 prose (current wiki transcription) and showpic.c reference implementation (indices 11, 15, 124, 125). Both sources are Lance Ewing. Verified directly by main session: 5-1-PICTURE.html line 316 / 329 vs showpic.c line 461 / 474. The wiki retains the 5-1 prose values pending ScummVM `engines/agi/picture.cpp` cross-check (post-Phase-B); the conflict callout is the proper documentation for an unresolvable-with-in-corpus-sources discrepancy.
- Delta to [[concepts/screen-layers]]: page-level banner downgraded from `(agidev, unverified)` process tag to verification-status banner noting which subsystems are code-verified by showpic.c (dimensions / init colors / drawing-mode flags) vs. still-open (per-pixel occlusion — showpic.c is a pic viewer, not a game runtime).
- Delta to [[concepts/picture-compression]]: NEW "Reference implementation: picv3-v2.c" section. Replaces 5-1's example-derived bit-packing description with picv3-v2.c's literal two-state machine (NORMAL ↔ ALTERNATE) — clarifies the previously-`(agidev, unverified)` bit-packing rule.
- Updated `wiki/index.md`: added `picture-rendering` under Concepts; added `5-3-picture` under Sources (with "closes Group 4" marker symmetric with 4-6's "closes Group 3" and 5-1's "opens Group 4").

Reviewer fixes / discretionary calls applied during ingest:

1. **Conflict callout, not silent patch, for splatter table.** Subagent recommended replacing the wiki's four discrepant values with showpic.c's. Reviewer judgment: both 5-1 and showpic.c are Ewing-authored agidev-corpus material; unilateral preference for one over the other is not justifiable without ScummVM tiebreaker. Documented the divergence; deferred resolution.
2. **Verification banner downgrade scope.** Subagent suggested wholesale removal of `(agidev, unverified)` tags. Reviewer judgment: [[interpreter/control-lines]] retains its banner — showpic.c doesn't decode control-line semantics — but [[entities/picture]] and [[concepts/screen-layers]] are downgraded to per-claim. This preserves accurate verification status per-subsystem rather than per-Group.
3. **Inline citations over dedicated source/code/ pages.** Per user direction, `[AGI_Specifications/Code/showpic.c:LINE]` citations are inline in the relevant pages; no new directory or page-per-codefile.
4. **Algorithms captured in a new concept page.** Per user direction, new [[concepts/picture-rendering]] page rather than pointer-only notes on [[entities/picture]]. The Bresenham-variant rounding, BFS queue sizing, and splatter wrap mechanics are genuine rendering algorithms — they deserve a dedicated page that future Rust-rewrite work can consult as a single artifact.

Main session direct verification on the splatter-table conflict: read showpic.c lines 455-475 and 5-1-PICTURE.html grep around lines 313-329. Confirmed the four byte-value discrepancies (indices 11: 0x04 vs 0x05; 15: 0x6d vs 0x7d; 124: 0x75 vs 0xa4; 125: 0xa3 vs 0x75). Three of four are 1-bit-flip distance; the 124/125 pair is not a clean swap (5-1 has 0xa3 where showpic has 0xa4 at index 125).

Authorship: chapter byline empty ("5.3 Sample Code", no author named in HTML header). File table cells attribute both files to Lance Ewing (with picv3-v2.c misspelled "Lange Ewing" — preserved in source-page documentation as a literal HTML typo). Code copyright headers confirm Lance Ewing 1997 for both. Meta-keywords trap: fifth live confirmation in the corpus (after 4-5, 4-6, 5-1, 5-2). The HTML `<meta name="keywords">` pattern lists "peter kelly" universally regardless of chapter byline — the rule "trust only the visible byline" is fully generalized.

Group 4 closure follows below.

---

## Group 4 closure summary

**Phase B Group 4 (PICTURE) is complete.** All three chapters ingested on 2026-05-10. Group 4 contributed the PICTURE bytecode subsystem documentation, resolved the long-dangling `[[interpreter/control-lines]]` forward-ref, and shifted the wiki's validation surface to include vendored reference C code at `AGI_Specifications/Code/`.

**Pages added across Group 4:**

- [[entities/picture]] — PICTURE resource on-disk format, opcode catalogue, encoding details, splatter texture data, screen initialization, reference-implementation pointers.
- [[interpreter/control-lines]] — Black/blue/green/cyan control-line semantics with EGA-palette mapping, search-downwards algorithm, KQ1 room 20 artifact case, two-source corroboration.
- [[concepts/screen-layers]] — Visual/priority dual-screen model with code-verified dimensions and init colors.
- [[concepts/picture-rendering]] — Bresenham-variant line drawing, BFS flood-fill, brush plotting, splatter mechanics — every algorithm code-verified against showpic.c.
- Three source pages: [[sources/5-1-picture]], [[sources/5-2-picture]], [[sources/5-3-picture]].

Plus deltas to existing pages: [[interpreter/overview]] §"Screen objects and priority bands" (occlusion-deferral pointer); [[interpreter/overview]] §"Control lines" (full color-priority mapping and pointer); [[interpreter/overview]] §"Resource types" (PICTURE no longer deferred); [[concepts/picture-compression]] (decompression-precedes-dispatch note + picv3-v2.c two-state-machine clarification).

**Dangling forward-references state.** Two remain in [[interpreter/overview]] after Group 4 close: `[[interpreter/view-objects]]` (Group 5 territory), `[[interpreter/debug-modes]]` (may remain thin). `[[interpreter/control-lines]]` was resolved by 5-1.

**Open items resolved by Group 4:**

- **Group-3 Item #9 (control-line color semantics)** — RESOLVED. 5-1 fully documented black/blue/green/cyan; 5-2 independently corroborated.
- **5-1 `0xF7` sign-bit polarity** — RESOLVED by showpic.c:369-372. No longer inferred from a single worked example.
- **5-1 wrap-at-255 splatter quirk** — CODE-VERIFIED by showpic.c:428-429. Whether intentional or a Sierra bug remains philosophical; the wrap must be replicated either way.
- **5-1 `0xFB..0xFE` reserved range** — STRENGTHENED. Three independent sources agree (5-1 prose, 5-2 catalogue ending at `0xFF`, showpic.c "Unknown picture code" fall-through). Not 100% closed (no exhaustive game scan) but as resolved as feasible in-corpus.

**Open items NOT resolved by Group 4 (carry to Group 5/post-Phase-B):**

- **Per-pixel occlusion algorithm.** showpic.c is a pic viewer; object-vs-priority-screen comparison is runtime LOGIC concern. Likely Group 5 (VIEW) territory.
- **Object-vs-control-line interaction.** Same.
- **Group-3 #3 base-point conflict** (bottom-left vs bottom-right). Untouched by Group 4. Group 5 likely resolves.
- **Group-3 #4 `add.to.pic` margin = 4 gap.** Untouched. Possibly a 4-4 spec oversight, not a PICTURE-side concern.

**New open items introduced by Group 4:**

- **Splatter offset table 4-position discrepancy** between 5-1 prose and showpic.c at indices 11, 15, 124, 125. Resolution requires ScummVM `engines/agi/picture.cpp` cross-check. `> [!conflict]` callout on [[entities/picture]].

**Conflicts in the wiki at Group 4 close** (preserved as `> [!conflict]` callouts):

- "2.400" version-string typo in [[interpreter/command-evolution]] — carried forward from Group 3; post-Phase-B ScummVM check.
- `$9B set.upper.left` arity in [[interpreter/command-semantics]] / [[interpreter/commands]] — 4-3 vs 4-4 disagreement; carried forward.
- Intra-4-4 base-point in [[interpreter/command-semantics]] — same chapter, two locations; carried forward.
- `add.to.pic` margin = 4 gap in [[interpreter/command-semantics]] — carried forward.
- **Splatter offset table indices 11/15/124/125** in [[entities/picture]] — NEW from 5-3. 5-1 prose vs showpic.c.

**Authorship snapshot for Group 4:**

- 5-1: Lance Ewing solo, IA 5 December 1997.
- 5-2: Vassili Bykov (translator), AGDS, IA 27 January 1998. **Fourth Bykov/AGDS chapter.** Same date as [[sources/4-2-logic]] (Peter Kelly) and [[sources/2-8-interpreter]] (Lance Ewing) — three-author January-1998 IA-extraction window confirmed.
- 5-3: anonymous chapter byline, file attribution Lance Ewing (with "Lange Ewing" typo on picv3-v2.c). No date in chapter HTML; file copyright headers 1997.

Lance Ewing as PICTURE-subsystem author across the corpus is now consolidated: 5-1 prose + 5-3 reference code + the AGDS-translation companion 5-2. The trio gives the wiki strongest single-subsystem coverage of any group so far.

**Validation surface expansion.** Group 4 changed the wiki's relationship to `AGI_Specifications/Code/`. Prior groups treated it as bibliographic-only reference (per [[sources/3-4-files]], [[sources/4-6-logic]]). Group 4 promoted `showpic.c` to a per-claim citation target for [[entities/picture]] and [[concepts/picture-rendering]], and `picv3-v2.c` for [[concepts/picture-compression]]. Going forward, Group 5 should consider whether `viewview.pas` (vendored at `AGI_Specifications/Code/`) similarly validates [[entities/view]] claims when that page lands.

**Phase B status after Group 4 close:** Groups 1 (Files), 2 (Interpreter), 3 (Logic), 4 (PICTURE) done. Groups 5 (VIEW), 6 (Sound), 7 (Other), 8 (Intro/Info) remain. Next chapter: `6-1-VIEW.html` (Group 5, chapter 1 of 3) — **the validation-case group**, since andromeda has a working `resource/view.py` decoder. The wiki claims for VIEW format will be cross-checkable against running Python code, not just vendored C reference code.
