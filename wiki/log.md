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
