# Source: 5-3-PICTURE.html

The third and final chapter in Group 4 (PICTURE). **A reference-implementation pointer chapter, not specification prose.** The HTML body is a single table indexing two vendored C files at `AGI_Specifications/Code/`; the actual content lives in the code.

## Scope

5-3 itself contains:

- Chapter title "5.3 Sample Code".
- IA-provenance annotation ("Retrieved from the Internet Archive").
- A two-row table:
  - `picv3-v2.c` — "Lange Ewing" (typo for Lance Ewing) — v3 → v2 PICTURE transcoder, 67 lines.
  - `showpic.c` — Lance Ewing — working Allegro-based PICTURE viewer, 650 lines.

What the **referenced code** contains (the substance of 5-3):

- **showpic.c**: opcode dispatch (lines 610-628); line drawing with additive fixed-point arithmetic and direction-sensitive rounding (lines 191-231); flood-fill BFS with 4000-entry queue (lines 249-293); brush plotting with circle/rectangle masks (lines 305-340); splatter mechanics including wrap-at-255 (lines 425-478); the splatter offset table (lines 459-475).
- **picv3-v2.c**: two-state machine (NORMAL ↔ ALTERNATE) for v3 → v2 byte expansion (lines 37-62).

## Authorship and provenance

- **Chapter byline** — None (the visible header has no author). Files are attributed to "Lange Ewing" [sic, picv3-v2.c] and "Lance Ewing" [showpic.c] in the table cells.
- **File copyright lines** — `picv3-v2.c` line 7: "(c) Lance Ewing 1997". `showpic.c` header comment names Lance Ewing.
- **IA-provenance** — "Retrieved from the Internet Archive" (chapter HTML line 15).
- **Meta-keywords trap** — Fifth confirmed instance in the corpus. HTML `<meta>` keywords list "peter kelly"; visible attribution is Lance Ewing only.

Consistent authorship with [[sources/5-1-picture]] (Lance Ewing, 5 December 1997), [[sources/4-1-logic]] (Lance Ewing, 20 August 1997), and the Code/ files referenced in [[sources/4-6-logic]] (logic.c, agifiles.c).

## Informs (substantial)

5-3 reframes the wiki's verification status for the PICTURE subsystem. **`showpic.c` is a working PICTURE decoder** — not in andromeda's `resource/`, but in `AGI_Specifications/Code/`. This changes the validation calculus: the previous "no decoder to validate against" page-level `(agidev, unverified)` tags on [[entities/picture]] and [[concepts/screen-layers]] are no longer accurate. Downgraded during this ingest to per-claim citations distinguishing code-verified claims from genuinely-unverified claims.

Page changes:

- **NEW** [[concepts/picture-rendering]] — Bresenham-variant line drawing, BFS flood-fill, brush plotting, splatter mechanics. Every algorithm code-verified against `showpic.c` with line citations. This is the page that captures what 5-1 deliberately punted on ("chapter pseudocode is the source of truth").
- [[entities/picture]] §verification banner — replaced page-level `(agidev, unverified)` with verification-status banner pointing to showpic.c.
- [[entities/picture]] §"Coordinate encoding" — code-verified citation `[showpic.c:113-114]`.
- [[entities/picture]] §"Relative-line displacement encoding" — code-verified citation `[showpic.c:369-372]` for sign-bit polarity (previously inferred from a single worked example).
- [[entities/picture]] §"Splatter texture data" — **`> [!conflict]` callout for 4-position discrepancy** between 5-1 prose (current wiki table values) and showpic.c reference implementation. Both Ewing-authored; no unilateral resolution. Wrap-at-255 quirk upgraded to code-verified.
- [[entities/picture]] §Opcode-catalogue `0xFB..0xFE` row — code-verified citation `[showpic.c:627]` (switch default falls through to "Unknown picture code"). Strengthens the "genuinely unused" reading.
- [[entities/picture]] §"Implementation guidance" — items 1, 2, 4 now cross-link [[concepts/picture-rendering]] instead of vaguely pointing at "chapter pseudocode".
- [[entities/picture]] §"Reference implementation" — NEW short section listing showpic.c sections with line-range citations.
- [[concepts/screen-layers]] §verification banner — page-level tag downgraded; dimensions/init/drawing-mode-flags code-verified via showpic.c.
- [[concepts/picture-compression]] §"Reference implementation: picv3-v2.c" — NEW section with the two-state-machine framing (NORMAL ↔ ALTERNATE). Replaces 5-1's example-derived prose with picv3-v2.c's literal implementation.

Page changes NOT made:

- [[interpreter/control-lines]] page-level tag is **left in place.** Control-line semantics describe how the LOGIC interpreter responds to control-line pixels during object motion. showpic.c is a pic viewer, not a game runtime — it doesn't decode control-line semantics. The two-source corroboration (5-1 prose + 5-2 AGDS) still applies but isn't code verification.

## Open items 5-3 resolves vs. leaves open

| Item | Status after 5-3 |
|------|-------------------|
| **`0xF7` sign-bit polarity** | **RESOLVED.** Code-verified at showpic.c:369-372. |
| **Wrap-at-255 splatter quirk** | **CODE-VERIFIED** (Ewing's reference implementation does the wrap; agnostic on whether it's "intentional"). |
| **`0xFB..0xFE` reserved range** | **STRENGTHENED.** showpic.c's switch falls through to "Unknown picture code" for these. Combined with 5-1 prose ("unused in most AGI games") and 5-2 catalogue ending at `0xFF`, three independent sources agree these are unused. Not 100% resolved (no enumeration of games that might use them) but as resolved as feasible without exhaustive game scan. |
| **Per-pixel occlusion algorithm** | NOT RESOLVED. showpic.c is a pic viewer, not a game runtime. Awaits Group 5 (VIEW) or ScummVM. |
| **Object-vs-control-line interaction** | NOT RESOLVED. Same reason. |
| **Group-3 #3 base-point conflict** | NOT TOUCHED. Group 5 territory. |
| **Group-3 #4 `add.to.pic` margin = 4 gap** | NOT TOUCHED. |

## New open items introduced by 5-3

- **Splatter offset table discrepancy at indices 11, 15, 124, 125.** Conflict callout on [[entities/picture]]. Resolution: ScummVM `engines/agi/picture.cpp` cross-check (post-Phase-B).
- **showpic.c queue-overflow behavior.** The 4000-entry flood-fill queue is a hard limit with no graceful degradation; a reimplementation needs to decide whether to faithfully reproduce this or grow dynamically.

## Notes

- **5-3 is the second "code-pointer chapter"** in the corpus, after [[sources/3-4-files]] (which similarly indexed reference code without specification prose) and [[sources/4-6-logic]] (bibliographic table for `logic.c`, `agifiles.c`, `agicommands.pas`). Pattern: each format group's last chapter is the reference-code index. Group 5 will likely follow this pattern (6-3-VIEW.html); Group 6 might (7.2-SOUND.html).
- **`AGI_Specifications/Code/` is now established as a validation surface for the wiki**, not just bibliographic reference. Where any wiki claim has a corresponding line range in one of those files, the citation belongs in-line. Inline citations chosen over dedicated `wiki/sources/code/` pages per minimal-tooling principle (the format `[showpic.c:LINE]` is plain enough to grep and link).
- **Both files are pre-ScummVM** (1997 vs. ScummVM AGI port circa 2005). They predate even the public spec corpus's circulation. Treating them as ground truth for AGI internals is conservative — only one Sierra-internal source disagrees (the AGDS manual, which itself isn't a decoder but the Russian-language reverse-engineering effort that produced [[sources/2-6-interpreter]], [[sources/4-4-logic]], [[sources/5-2-picture]]). Where AGDS and Ewing-code agree, we have strong cross-source corroboration.

## Relation to 5-1 and 5-2

5-1 (Lance Ewing prose), 5-2 (AGDS translation), and 5-3 (Lance Ewing reference code) form a three-source set on PICTURE:

- **5-1**: narrative specification with diagrams. Source for the opcode-byte format, splatter texture tables (with the 4-position prose/code discrepancy surfaced by 5-3), bit layouts.
- **5-2**: independent narrative corroboration from the AGDS manual. Confirms init colors, control-line colors, opcode catalogue. Different terminology ("dots" vs "pen") but same bytecode.
- **5-3**: reference implementation. Working decoder for everything in 5-1's catalogue (plus algorithms 5-1 punted on, plus the four-position splatter table conflict).

Where any two of these agree, the wiki claim is well-supported. Where all three agree, it's nearly definitive (only ScummVM cross-check would add further confidence). Where 5-1 and 5-3 disagree (the splatter table), the wiki preserves both and defers — exactly the case the `> [!conflict]` callout pattern was designed for.
