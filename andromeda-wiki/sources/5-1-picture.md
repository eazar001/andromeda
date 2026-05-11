# Source: 5-1-PICTURE.html

The first of three chapters in Group 4 (PICTURE). Specifies the PICTURE resource bytecode format, drawing primitives, screen-layer composition, control-line semantics, and pen/splatter rendering [5-1-PICTURE.html].

## Scope

Covered in 5-1:

- The PICTURE bytecode dispatch model and full opcode catalogue (`0xF0..0xFF`).
- Coordinate, color, displacement, pen-style, and splatter-texture encodings.
- The visual / priority dual-screen model, init colors, and per-screen draw-enable state.
- Control-line colors (black/blue/green/cyan) with their barrier / alarm / surface semantics.
- The search-downwards algorithm that recovers priority under a control-line pixel (with KQ1 room 20 as an artifact case study).
- Line-drawing pseudocode, brush-shape diagrams, the 32-byte splatter-texture table, and the 128-entry offset table.

NOT covered:

- v3 PICTURE compression byte-packing (already in [[concepts/picture-compression]] from 3-3).
- LOGIC-side PICTURE composition (`$7A add.to.pic`, `$7B add.to.pic.v`) — those are LOGIC opcodes whose semantics surface in 4-4 and beyond; 5-1 documents the PICTURE-side state machinery they invoke but not the LOGIC argument list (already in [[interpreter/commands]] / [[interpreter/command-semantics]]).
- Per-pixel occlusion algorithm (deferred to a later Group-4 chapter or to ScummVM cross-check; only the screen-layer structure is here).
- Full screen-object model and base-point conventions (Group 5 / VIEW).

## Authorship and provenance

- **Author** — Lance Ewing `<be@ihug.co.nz>` (visible byline, line 15).
- **Last updated** — 5 December 1997 (line 16).
- **Provenance** — "Retrived from the Internet Archive" (line 17, original typo preserved).
- **Adaptation note** — "Some of this first section has been taken from 'The Official Book of King's Quest' written by Donald B. Trivette" (line 19).
- **Meta-keywords trap** — The HTML `<meta name="keywords">` tag lists "peter kelly" among the keywords, but the chapter byline is Lance Ewing only. Per the Group-3 lesson on 4-5 and 4-6 subagent errors, only the visible byline counts.

Same author and same IA-extraction window (December 1997) as [[sources/4-4-logic]] — both Lance Ewing primary in [[sources/4-4-logic]]'s authorship triple. The PICTURE/LOGIC pairing is consistent with Lance Ewing's role on `logic.c`, `agifiles.c` listed in [[sources/4-6-logic]].

## Informs

- [[entities/picture]] — NEW. Full on-disk format and opcode catalogue. Page-level `(agidev, unverified)` (no decoder in `resource/`).
- [[interpreter/control-lines]] — NEW. Resolves the long-dangling forward-ref originally placed by the 2-1 ingest into [[interpreter/overview]] §"Control lines".
- [[concepts/screen-layers]] — NEW. The visual/priority dual-screen model; will be extended by Group 5 (VIEW) from the screen-object/composition side.
- [[concepts/picture-compression]] — extended with a one-paragraph note clarifying that v3 decompression precedes bytecode dispatch (no compressed-vs-expanded ambiguity for the opcode table).
- [[interpreter/overview]] §"Screen objects and priority bands" — occlusion-deferral pointer updated to cite [[concepts/screen-layers]].
- [[interpreter/overview]] §"Control lines" — cyan-semantics `(agidev, unverified)` qualifier removed (now fully documented in [[interpreter/control-lines]]); 5-1 cited alongside existing 2-1 citation.

## Conflicts / contradictions noticed

None against existing wiki pages. Cyan-confinement semantics from 2-1 are corroborated by 5-1. Control-line colors black/blue/green/cyan map to priorities 0/1/2/3 (this follows from the EGA palette equivalence and is consistent with the priorities-0–3-reserved note already in [[interpreter/priority-bands]]).

## Open items resolved

- **#9 (control-line color semantics)** — RESOLVED. Black = unconditional barrier; blue = conditional barrier; green = alarm; cyan = water/surface confinement.
- **Dangling `[[interpreter/control-lines]]` forward-ref** — RESOLVED.

## Open items still open after this ingest

- **#3 base-point conflict (cel base bottom-left vs bottom-right)** — 5-1 does not discuss cel base-points; deferred to Group 5 (VIEW).
- **#4 `add.to.pic` margin = 4 gap** — 5-1 does not discuss `add.to.pic`'s LOGIC-side margin parameter at all; remains open. May be a 4-4 spec oversight rather than a Group-4 PICTURE concern.
- **Per-pixel occlusion algorithm** — 5-1 documents the screen-layer structure and search-downwards control-line resolution but does not give the per-object occlusion check. Still deferred.
- **Wrap-at-255 splatter quirk** — Documented but `(agidev, unverified)`; will need ScummVM cross-check or a working PICTURE decoder.
- **Sign-bit polarity of `0xF7` displacements** — Inferred from the chapter's worked example (`0xCC` = `(−4, −4)`); will need cross-check.
- **Opcodes `0xFB..0xFE`** — Described as "unused in most AGI games"; no enumeration of which games (if any) use them and to what effect.

## Notes

- 5-1 makes the visual-screen-initializes-to-white and priority-screen-initializes-to-red claim explicit; this is foundational for flood-fill boundary correctness and is captured in [[entities/picture]] §"Screen initialization".
- The KQ1 room 20 artifact (blue control line obscuring priority bands beside the left tree) is the only worked example of search-downwards behavior; documented as a citation case study in [[interpreter/control-lines]].
- Mathematical rigidity of the priority-band grid is noted ("artist must use them like a horizontal grid"); the 168-tall framing aligns with [[interpreter/priority-bands]]'s y-band table without overlap.
