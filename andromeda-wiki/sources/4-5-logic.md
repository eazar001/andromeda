# Source: 4-5-Logic.html

**Chapter:** 4.5 Discussion of Sample LOGIC Code from KQ4
**Path:** `AGI_Specifications/Specifications/4-5-Logic.html`
**Author:** No byline in HTML header (anonymous within the chapter; meta-keywords mention "peter kelly" but no attribution line).
**Last updated:** 31 August 1997
**Provenance:** "Retrived from the Internet Archive" (sic)

## Scope

A code-walkthrough — **not** a format-specification chapter. The author quotes three LOGIC pseudo-code fragments published in *The Official Book of King's Quest* alongside the actual bytecode (decompiled) from KQ4 Room 7, with brief side-by-side commentary. Five samples in total:

- *Animating the smoke* — VIEW lifecycle: `animate.obj`, `set.view`, `set.loop`, `position`, `step.time`, `cycle.time`, `draw`.
- *Opening the door* — conditional logic with `said`, `posn`, `isset`, view-object animation, `prevent.input`, `sound`.
- *Unlocking the door* — conditional with `said` synonym groups and flag tests.
- *Knocking on the door* — multi-branch input routing via `said` patterns.
- *Fall rocks* — state machine over `move.obj.v`, nested `if`, flag tests, loop control.

No new opcodes, no new format claims, no semantic extensions. Sample-only.

## Informs

Sources-only ingest, **parallel to 3-4 (Sample Code reference), 2-5 (loader/encryption), and 2-7 (version cross-reference)** — all chapters that are part of the corpus but do not generate entity / concept / interpreter pages.

Light delta:

- [[sources/4-2-logic]] — appended a note recording the `||` source-syntax synonym-group convention observed in 4-5's GAME-form samples (e.g., `said(OPEN, DOOR||DOORS||DOORWAY||DOORWAYS)`). 4-2 documents the AGI Studio source syntax but does not mention this `||` form explicitly. The synonym groups compile to a single 2-byte vocabulary word code at the bytecode level (all four words share one WORDS.TOK group code), so the bytecode encoding documented in [[entities/logic]] §"The `said` test command" is unaffected.

Validation value (post-Phase-B):

- When a LOGIC decoder is implemented in `resource/`, these five KQ4 Room 7 samples become **round-trip test cases**: decoding the bytecode from KQ4's LOGIC.7 (or wherever Room 7 lives) and pretty-printing should produce code resembling the "FROM THE GAME" pseudo-code shown in 4-5. Discrepancies between our output and 4-5's quoted output point to decoder bugs or opcode-table errors.

## Notes

**Author-vs-compiler differences observed in the samples** (useful authoring context, not format facts):

- Pseudo-code (BOOK) uses named constants and symbolic variables (`v.fish.cabin`, `smoke`, `work`, `priorx`, `tempx`, `notCloseEnough`); decompiled bytecode (GAME) uses numeric indices (`114`, `7`, `152`, `113`). This reflects the AGI Studio preprocessor's `#define` aliasing per [[sources/4-2-logic]] §Scope and the broader "type prefix + number" argument convention from [[concepts/agi-data-types]].
- The GAME version of "Animating the smoke" *adds* two opcodes to the BOOK version (`ignore.objs(7)` and `set.priority(7, 5)`) — both present in the final game but absent from the published pseudo-code. This is an addition, not a substitution; `ignore.horizon(7)` appears in both versions.
- The BOOK version's `step.time(smoke, work)` corresponds to GAME `assignn(152, 3); step.time(7, 152);` — the named constant `work = 3` is pre-assigned to var(152) by the compiler.
- BOOK uses `||` and `&&` as boolean operators in `if` conditions; GAME decomposes them into sequential bytecode (per the `$FC..$FF` control-flow opcodes documented in [[entities/logic]]).
- BOOK uses `said(open, door)`; GAME uses `said(OPEN, DOOR||DOORS||DOORWAY||DOORWAYS)` — the `||` inside a `said` argument denotes a synonym group at source-syntax level, collapsing to one vocabulary word code at the bytecode level.

**Anonymous chapter.** Unlike 4-1 (Lance Ewing), 4-2 (Peter Kelly), 4-3 (Peter Kelly), 4-4 (AGDS / Bykov / Ewing), 4-5 has no byline. The 31 August 1997 date matches 2-4 and 2-6's IA-provenance dates exactly, suggesting all three were extracted in the same Internet Archive session.

**Opcode references in the samples were spot-checked against [[interpreter/commands]]** — all named opcodes exist with consistent argument counts. No conflicts.

**Scope decision.** Sources-only ingest matches the established 3-4 / 2-5 / 2-7 pattern: file the chapter, document why it doesn't generate format pages, and preserve it for future validation use. The wiki is byte-level format only per the plan's "Out of scope" section; sample code is authoring artifact, not format spec.
