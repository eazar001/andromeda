# Source: 2-1-Interpreter.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/2-1-Interpreter.html`. High-level entry chapter for the LOGIC interpreter — introduces the major VM primitives at the conceptual level.

## Scope

Conceptual overview only: what AGI is, the three versions (v1 / v2 / v3), the main file types referenced from the runtime, the five resource categories (LOGIC, PICTURE, VIEW, SOUND, plus auxiliary `WORDS.TOK` / `OBJECT`), the command language at headline depth (~181 procedures, ~18 tests, control-flow keywords), the priority-band / control-line / ego model in summary form, debug modes, and the event-loop sketch. Byte-level formats, opcode tables, exact band boundaries, and event-loop timing are all deferred to subsequent Interpreter chapters (2-2 through 2-8) and to the resource-format groups.

## Informs

- [[interpreter/overview]] — single hub page collecting this chapter's headline points, with forward-references to the subsystem pages that later Group-2 chapters will create.

## Notes

- The Python prototype implements no interpreter code, so spec claims here (event-loop ordering, control-line semantics, priority occlusion algorithm) are unverifiable against working code; they are tagged `(agidev, unverified)` on the overview page where appropriate.
- No conflicts observed against Files-group pages.
