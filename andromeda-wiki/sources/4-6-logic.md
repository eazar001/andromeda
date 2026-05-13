# Source: 4-6-Logic.html

**Chapter:** 4.6 Sample Code
**Path:** `AGI_Specifications/Specifications/4-6-Logic.html`
**Author:** No chapter-level byline. Per-row attribution: Lance Ewing (four files), Peter Kelly (one file).
**Last updated:** Not stated in HTML.
**Provenance:** No IA annotation in HTML. Chapter consists solely of a 5-row reference table.

## Scope

Bibliographic reference — **not** a format-specification chapter. The chapter is a single `<h1>` + 5-row table pointing to source files vendored at `AGI_Specifications/Code/`:

| File | Author | Description |
|---|---|---|
| `Code/logic.c` | Lance Ewing | Loads LOGIC resources into a `LOGICFile` structure. |
| `Code/logic.h` | Lance Ewing | Header for `logic.c`. |
| `Code/agifiles.c` | Lance Ewing | Resource-loading routines (shared across resource types). |
| `Code/agifiles.h` | Lance Ewing | Header for `agifiles.c`. |
| `Code/agicommands.pas` | Peter Kelly | Delphi/Pascal unit listing commands and argument types. |

All five files verified present in `AGI_Specifications/Code/`. The chapter's value is bibliographic — pointing at reference implementations — not specification. Structurally identical to [[sources/3-4-files]] (which was the same form at the Files-group level).

## Informs

Sources-only ingest, **parallel to [[sources/3-4-files]], [[sources/4-5-logic]], [[sources/2-5-interpreter]], and [[sources/2-7-interpreter]]**. No new entity / concept / interpreter pages. No deltas to existing pages.

Post-Phase-B validation value:

- `Code/logic.c` (Lance Ewing) is plausibly the reverse-engineering work that informed [4-1-Logic.html]'s bytecode-format spec. When a LOGIC decoder lands in `resource/`, it can be cross-validated against this `LOGICFile`-structure decoder for round-trip parity.
- `Code/agicommands.pas` (Peter Kelly) is plausibly the table that informed [4-3-Logic.html]'s opcode catalogue. It serves as a secondary source for resolving the eleven `unknown170..unknown181` opcodes and the `$9B set.upper.left` arity conflict that remain open at Group 3 close.
- `Code/agifiles.c` overlaps the scope of [[entities/vol-file]] and [[entities/dir-file]]; cross-checking against `resource/header.py`, `resource/volume.py`, and `resource/directory.py` may surface implementation differences.

## Notes

**No HTML date.** Unlike most chapters in the corpus, 4-6 carries no "Last updated" annotation. The chapter is plausibly auto-generated (table-only structure) and was not maintained as prose.

**Author attribution.** 4-6 contains no chapter-level byline. The meta-keywords mention `peter kelly` but that is corpus boilerplate present on every Specifications HTML (also on 4-5, where it does not constitute authorship). Per-row table attribution is the only author signal: Lance Ewing wrote four of the five files; Peter Kelly wrote `agicommands.pas`. Both are dominant Group-3 contributors.

**Closes Group 3 — Phase B Group 3 (Logic) complete after this ingest.** Detailed closure notes in `wiki/log.md` for the 4-6 entry. Eleven open items and three dangling forward-references carry forward into Groups 4/5/6 and post-Phase-B ScummVM cross-check.
