# Variables and Flags

The LOGIC interpreter maintains 256 8-bit variables (`var(0)`–`var(255)`) and 256 single-bit flags (`flag(0)`–`flag(255)`) as the primary game-state store. All entries are initialized to 0 on interpreter startup [2-2-Interpreter.html §Variables used by the interpreter, §Flags used by the interpreter].

Variables and flags share a single global namespace across every loaded LOGIC resource: there is no per-LOGIC scope, and a write in any LOGIC is immediately visible to every other LOGIC executing in the same cycle [2-2-Interpreter.html §How AGI works]. This design pushes game scripts toward stateless, event-driven procedures that communicate entirely through shared state.

## Reserved variables (0–26)

`var(0)` through `var(26)` are reserved for interpreter use; programmers may use `var(27)`–`var(255)` freely [2-2-Interpreter.html §Variables used by the interpreter].

| Variable | Semantics |
|---|---|
| `var(0)` | Current room number (parameter to the most recent `new_room` command). Initialized to 0. Coordinated with var(1), var(2), var(4), var(5), var(16), and flag(5) during room transitions — see [[interpreter/command-semantics]] §"`new.room` — the eleven-step room transition". |
| `var(1)` | Previous room number. Written by step 6 of the `new.room` procedure (saved from var(0) before var(0) is overwritten). |
| `var(2)` | Code of the border touched by EGO: `0` = nothing, `1` = top edge / horizon, `2` = right edge, `3` = bottom edge, `4` = left edge. Read by the `new.room` procedure (step 8) to reposition EGO into the new room; cleared to 0 by step 9. |
| `var(3)` | Current score. The interpreter monitors changes to this variable to redraw the on-screen status line. |
| `var(4)` | Object number (≠ EGO) that touched a screen border. |
| `var(5)` | Border-touch code for the object in `var(4)`; same encoding as `var(2)`. |
| `var(6)` | Direction of EGO's motion. Compass mapping: `0` = motionless, `1` = N, `2` = NE, `3` = E, `4` = SE, `5` = S, `6` = SW, `7` = W, `8` = NW. The interpreter reads from or writes to this slot depending on whether the game is in *program control* or *player control* mode (see [[interpreter/event-loop]]). |
| `var(7)` | Maximum achievable score. |
| `var(8)` | Free memory: number of 256-byte pages still available in the interpreter's heap. See [[interpreter/memory-layout]]. |
| `var(9)` | 1-indexed position of the first word the input parser failed to match in the player's input; 0 if all words parsed successfully. Set only when vocabulary lookup fails [2-6-Interpreter.html; 4-4-Logic.html §TEST COMMANDS, `said`]. The 2-2 phrasing ("if = 0, it is the number of the word ... that was not found") reads as inverted but is semantically consistent with this once read as "if non-zero, gives the unparsed-word position; if zero, all words parsed." 4-4 corroborates 2-6 verbatim (both are Bykov AGDS translations). See [[interpreter/input-parsing]] and [[interpreter/command-semantics]] §"`said` test command — algorithm". |
| `var(10)` | Inter-cycle delay, in 1/20-second units (50 ms per unit). Games typically set this to 2–4. |
| `var(11)`–`var(14)` | Interpreter's internal clock: seconds, minutes, hours, days respectively. |
| `var(15)` | Joystick sensitivity, used when `flag(8) = 1`. |
| `var(16)` | VIEW resource ID associated with EGO. Written by step 6 of the `new.room` procedure (preserved across room transitions). |
| `var(17)` | Interpreter error code. Spec phrasing is "(if = 0)"; translator's note again suggests the intended meaning is "if != 0" [2-2-Interpreter.html §Variables used by the interpreter] (agidev, unverified — inverted phrasing in source). |
| `var(18)` | Additional information accompanying the error code in `var(17)`. |
| `var(19)` | Last key pressed on the keyboard. |
| `var(20)` | Computer type (for hardware compatibility). For IBM PC it is always 0. |
| `var(21)` | Window auto-close delay. If `flag(15) = 0` (window-auto-close mode) and `var(21) ≠ 0`, message windows automatically close after `0.5 × var(21)` seconds. |
| `var(22)` | Sound generator type: `1` = PC speaker, `3` = Tandy. |
| `var(23)` | Sound volume (Tandy only), range `0x0`–`0xF`. |
| `var(24)` | Spec lists this as `29h` with no further description; meaning unclear (agidev, unverified). |
| `var(25)` | ID of the item selected via the `status` command, or `0xFF` if the player pressed Esc. |
| `var(26)` | Monitor type: `0` = CGA, `2` = Hercules, `3` = EGA. |

## Reserved flags (0–15)

`flag(0)` through `flag(15)` are reserved for interpreter use; programmers may use `flag(16)`–`flag(255)` freely [2-2-Interpreter.html §Flags used by the interpreter].

| Flag | Semantics |
|---|---|
| `flag(0)` | Set when EGO's baseline is completely on water-surface pixels (priority = 3). |
| `flag(1)` | Set when EGO is completely obscured (invisible on screen). |
| `flag(2)` | Set when the player has entered a command line *and* the interpreter has successfully parsed every word against the vocabulary [2-6-Interpreter.html]. If any word fails to parse, `flag(2)` is left unset and `var(9)` reports the failure position. Cleared at the start of each cycle. See [[interpreter/input-parsing]]. |
| `flag(3)` | Set when EGO's baseline touches a signal-line pixel (priority = 2). |
| `flag(4)` | Set when a `said` test command has successfully matched player input [2-6-Interpreter.html]. Cleared at the start of each cycle (event-loop cleanup step) and re-cleared each time input preprocessing succeeds. Once set within a cycle, all subsequent `said` tests in that cycle short-circuit to FALSE on the `flag(4) = 1` precondition — at-most-once-per-cycle `said` semantics. The spec does *not* clear `flag(4)` on a failed `said` match. See [[interpreter/input-parsing]]. |
| `flag(5)` | Set on the very first cycle a room is entered; cleared by the interpreter after that cycle's cleanup. Set by step 10 of the `new.room` procedure [4-4-Logic.html §PROGRAM CONTROL COMMANDS, emphasized as "VERY IMPORTANT"] — see [[interpreter/command-semantics]] §"`new.room`". |
| `flag(6)` | Set when `restart_game` has been executed; cleared after the current cycle completes. |
| `flag(7)` | If set, writing to the script/log buffer is blocked. |
| `flag(8)` | If set, `var(15)` controls joystick sensitivity. |
| `flag(9)` | Sound on/off state. The interpreter monitors this flag to redraw the on-screen status line. |
| `flag(10)` | Built-in debugger activation (also accessible via ALT-D in most shipped games; see [[interpreter/debug-modes]]). |
| `flag(11)` | Set during the very first execution of LOGIC 0; distinguishes cold-start initialization from subsequent cycles. |
| `flag(12)` | Set when `restore_game` has been executed; cleared after the current cycle. |
| `flag(13)` | If set, the `status` command lets the player select inventory items. |
| `flag(14)` | If set, the menu system is enabled. |
| `flag(15)` | Print-window mode: `1` = window persists until the user dismisses it; `0` = window closes on Enter/Esc, or automatically after `0.5 × var(21)` seconds if `var(21) ≠ 0`. |

## Spec ambiguities

Two reserved-variable descriptions in the spec read with apparently-inverted logic (`var(9)` and `var(17)`, both quoted above) and are flagged with translator's notes in the source HTML. The wiki preserves the spec's phrasing verbatim and tags the entries `(agidev, unverified)`; cross-check against ScummVM's AGI interpreter when validating against a real game.

## See also

- [[interpreter/event-loop]] — the per-frame cycle that reads, clears, and writes the reserved variables and flags
- [[interpreter/debug-modes]] — runtime inspection / mutation of variables and flags (uses `flag(10)`)
- [[concepts/agi-data-types]] — the broader catalog of parameter types (strings, words, objects, inventory items, messages) that variables and flags belong to
