# Source: 4-3-Logic.html

**Chapter:** 4.3 Command List & Argument Types
**Path:** `AGI_Specifications/Specifications/4-3-Logic.html`
**Author:** Peter Kelly (`ptrkelly@ozemail.com.au`)
**Last updated:** 3 March 1998
**Provenance:** "Retrived from the Internet Archive" (sic, in HTML)

## Scope

The opcode catalogue. Two tables:

- **Test commands** (§Text commands) — 18 boolean-test opcodes `$01..$12` with argument counts and per-argument type signatures (`var`, `num`, `flag`, `S obj`, `I obj`, `cntrl`, `string`, plus variable-count `said`).
- **Action commands** (§Action commands) — 182 imperative opcodes `$00..$B5`. Each row: opcode hex, mnemonic, argument count, per-argument types. Argument counts are authoritative; per-argument type cells are reliable except for markup artifacts (stray "string" entries in slots beyond the declared count for many `$3E..$71` rows, identifiable by being unreferenced by the count column).
- Inline version-conditional argument-count notes on four commands: `$86 quit` (0 args in 2.089, 1 in later); `$97 print.at` / `$98 print.at.v` (3 args "before 2.400", 4 later — the "2.400" version doesn't exist; see [[interpreter/command-evolution]] §conflict callout); `$B0 unknown176` (1 arg in 3.002.086, 0 in later v3).
- Eleven explicitly-unnamed action commands `$AA..$B5` (`unknown170..unknown181`), with `???` argument types in several rows — matches the [2-8-Interpreter.html] statement "the last eleven we do not know the names of".

No semantics, behavioral descriptions, or execution rules — purely opcode-to-signature lookup tables.

## Informs

- [[interpreter/commands]] — **new page**, the full opcode catalogue. Resolves the long-standing dangling forward-reference originally created in the 2-1 ingest from [[interpreter/overview]] §"The LOGIC virtual machine", and subsequently referenced by [[concepts/agi-data-types]] §"Message" and [[interpreter/command-evolution]] §"See also".
- [[interpreter/command-evolution]] — corroborates 2-8's four argument-count mutations. Same "2.400" spec typo reproduced verbatim by 4-3, strengthening the case that it is a typo (both Peter-Kelly-curated 1998 chapters carry the same error rather than independently agreeing on a real version). Conflict callout updated to cite both sources.
- [[entities/logic]] — implicit: the bytecode dispatch ranges (`$00..$B5` action, `$01..$12` test) documented in 4-1 are now populated with full mnemonic/signature data on the [[interpreter/commands]] page; 4-3 supplies the missing labels.
- [[concepts/agi-data-types]] — Controller (added by 4-2) is consumed by test opcode `$0C controller` and action opcodes `$79 set.key`, `$9D set.menu.item`, `$9F enable.item`, `$A0 disable.item`. Added to the Controller section.
- [[sources/2-5-interpreter]] — `set.game.id` opcode (`$8F`) now has its source-syntax signature (1 arg, `message` type). Runtime semantics (what the interpreter does with the ID at game-load time) remain in 2-5's loader-side discussion; the LOGIC-side call form is now on [[interpreter/commands]].

Deferred:

- Opcode behavioral semantics — what `animate.obj` actually mutates, the exact priority-band rules for `set.priority`, the RNG used by `random`, etc. — not in 4-3. Later Group 3 chapters and Groups 4/5 may address.
- Resolution of `???` argument types for the eleven `unknown*` commands and a few documented commands (`$9B set.upper.left`). Recovery requires ScummVM source or AGI Studio cross-check (a future, post-Phase-B task).
- The `said` matching algorithm (wildcards `1`/`9999`, longest-match vs. equality) — the 2-6 forward-pointer to 4-3 is **not** answered here. 4-3 confirms `said` is opcode `$0E` with variable-count word-code arguments, but the matching algorithm itself remains documented in [[interpreter/input-parsing]] from the 2-6 AGDS chapter. This is a corpus gap, not a wiki gap; cross-referenced explicitly on both pages.

## Notes

**Largest single Group-3 ingest so far.** 4-3 generates a 200-row opcode catalogue page and touches five other pages. The corpus's longest-standing dangling forward-ref ([[interpreter/commands]], created at 2-1 ingest in Group 2) is finally resolved.

**Spec markup artifacts.** Many action-command rows from `$3E..$71` carry an extra `<td>string</td>` cell in the table beyond the declared argument count (e.g. `$3E observe.horizon` has count = 1, arg 1 = `S obj`, then a stray `string` in the arg-2 slot; `$67 display` has count = 3 then an unreferenced `string` in arg-4). These appear to be editing accidents — the argument-count column is authoritative and matches the established AGIDATA.OVL bit-encoded type byte (per [[entities/logic]] §"Argument dispatch"). Transcribed the catalogue against the declared counts, dropping the stray cells. Worth flagging for any future agent that hits a discrepancy between this wiki's catalogue and a direct read of 4-3.

**`said` confirmation.** 4-3 places `said` at test opcode `$0E` with argument count `-` (variable). This matches the bytecode example in [[entities/logic]] §"The `said` test command" (`FF 0E 01 1E 01 FF` for `if (said("marble"))`).  Confirms the 4-1 ingest's transcription.

**Same-author corroboration of the "2.400" typo.** Both 2-8-Interpreter.html and 4-3-Logic.html — different Lance Ewing / Peter Kelly chapters from 1998 — contain the identical "2.400" version string. The conflict callout on [[interpreter/command-evolution]] is updated to cite both sources. Provisional reading remains 2.440 `(agidev, unverified)`; conclusive resolution requires ScummVM cross-check.

**Authorship.** Peter Kelly, 3 March 1998, IA-provenance. Same date as 2-5-Interpreter.html (which Peter Kelly contributed to alongside Lance Ewing and Anders M Olsson). This is the second Peter-Kelly-primary Group-3 chapter (4-2 was first).
