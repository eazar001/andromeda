# Source: 9-3-MakingOfThunderstorm.html

**Chapter:** §9.3 The Making of Thunderstorm
**Path:** `AGI_Specifications/Specifications/9-3-MakingOfThunderstorm.html`
**Author:** A. V. Horev (developer narrative, August 1991)
**Translator:** Vassili Bykov (Russian → English)

## Scope

Fan postmortem of *Thunderstorm*, an educational AGI game on weather and electricity, written ~1991. Narrates the author's design process, team coordination (designer / artist / programmer), LOGIC programming workflow, and practical debugging using AGDS tools (`SE`, `VIM`, `PM`, `DUU`, `VM`). Anecdotal and heuristic.

## Format claims surfaced

**None new.** Where the chapter touches interpreter behavior, it corroborates material already documented from 2-2, 2-6, and 4-4:

- The cyclic call/return event-loop model (already on [[interpreter/event-loop]] from 2-2/2-6).
- `flag(5)` as the "first cycle in a new room" sentinel set by `new.room` (already on [[interpreter/variables-and-flags]] and [[interpreter/command-semantics]] from 4-4).
- `flag(6)` as the post-`restart_game` sentinel (already on [[interpreter/variables-and-flags]] from 2-2).
- The interpreter-handles-drawing rule that warns scripts not to cyclically blit objects themselves (consistent with [[interpreter/event-loop]]).

No extensions written. Per wiki convention, "9-3 also confirms this" annotations on existing pages are padding and have been skipped.

## Reference-implementation notes (workflow only)

- Uses AGDS underscore mnemonic forms (`new_room_v`, `end_of_loop`) reflecting MASM assembly conventions in the original AGDS docs; not a format claim, just an authoring-time mnemonic variant. Wiki uses period-separated forms canonically (see [[interpreter/command-semantics]] §"Mnemonic variants across chapters").
- Mentions specific source files (`log0.asm`, `log05.asm`, `log07.asm`) and AGDS tool quirks (DUU debugger-include bug, VM link failure on IBM XT) that are not vendored or independently verifiable.

## Informs

Nothing. No extensions, no new pages, no cross-references.

## Notes

- **Closes Group 8 (Intro/Info)** and with it **closes Phase B (Bootstrap ingest)**. All thirty-four chapters of the AGI Specifications corpus are now ingested.
- Reliability tier: anecdotal. Tag `(agidev, workflow/anecdotal)` if cited for an interpreter behavior claim. The chapter is useful for "what did 1991 AGI authoring actually look like" questions; not useful for "what is the byte layout of X" questions.
- Fifth AGDS-connected chapter in the corpus (after 2-6, 4-4, 5-2, and 9-2). AGDS's footprint on the spec is substantial — five of thirty-four chapters trace back to it.
