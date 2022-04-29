# Source: 2-2-Interpreter.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/2-2-Interpreter.html`. Detailed specification of the interpreter's state machine and per-frame work cycle.

## Scope

Complete table of the 27 reserved variables (`var(0)`–`var(26)`) and 16 reserved flags (`flag(0)`–`flag(15)`), including semantics and initial values. Block diagram and textual specification of the per-frame interpreter cycle: eleven ordered steps from inter-cycle delay through room-transition check, with the exact list of variable/flag resets performed in post-LOGIC cleanup. Shared-namespace scoping (every LOGIC sees the same variable/flag store) is also established here.

## Informs

- [[interpreter/variables-and-flags]] — reserved-slot assignment tables, scoping rules, spec ambiguities.
- [[interpreter/event-loop]] — eleven-step per-frame cycle with per-step state-management detail.
- Updated [[interpreter/overview]]: the "Variables and flags" and "The event loop" sections are now one-paragraph hubs that link to the dedicated subsystem pages.

## Notes

- The Python prototype has no interpreter code, so claims about cycle ordering, flag-clearing timing, and shared-state scoping cannot be cross-checked against working code yet. Unverifiable claims are tagged `(agidev, unverified)` on the subsystem pages.
- The spec's original HTML contains translator's notes flagging `var(9)` and `var(17)` as having apparently-inverted phrasing ("if = 0" where "if != 0" would be the natural reading). The wiki preserves the spec's wording verbatim and tags both entries `(agidev, unverified)`.
- No conflicts observed against [[interpreter/overview]] or Files-group pages.
