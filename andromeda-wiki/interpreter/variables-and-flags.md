# Variables and Flags

The LOGIC interpreter maintains 256 8-bit variables (`var(0)`–`var(255)`) and 256 single-bit flags (`flag(0)`–`flag(255)`) as the primary game-state store. All entries are initialized to 0 on interpreter startup [2-2-Interpreter.html §Variables used by the interpreter, §Flags used by the interpreter]. Startup in 2.917 then sets `var(20)`, `var(22)`, `var(24)`, `var(26)`, `flag(5)` and `flag(9)`, and on some machines `flag(11)` [AGI 2.917 1000:1080–1000:10C7, 1000:0F97].

Variables and flags share a single global namespace across every loaded LOGIC resource: there is no per-LOGIC scope, and a write in any LOGIC is immediately visible to every other LOGIC executing in the same cycle [2-2-Interpreter.html §How AGI works]. This design pushes game scripts toward stateless, event-driven procedures that communicate entirely through shared state.

## Reserved variables (0–26)

`var(0)` through `var(26)` are reserved for interpreter use; programmers may use `var(27)`–`var(255)` freely [2-2-Interpreter.html §Variables used by the interpreter].

| Variable | Semantics |
|---|---|
| `var(0)` | Current room number (parameter to the most recent `new_room` command). Initialized to 0. Coordinated with var(1), var(2), var(4), var(5), var(16), and flag(5) during room transitions — see [[interpreter/command-semantics]] §"`new.room` — the eleven-step room transition". |
| `var(1)` | Previous room number. Written by step 6 of the `new.room` procedure (saved from var(0) before var(0) is overwritten). |
| `var(2)` | Code of the border touched by EGO: `0` = nothing, `1` = top edge / horizon, `2` = right edge, `3` = bottom edge, `4` = left edge. One code per step, with y overriding x, and a refused step records none [AGI 2.917 1000:15A6–1000:15FB, 1000:1643]. Cleared at the start of the step pass whenever an object is active [AGI 2.917 1000:151E]. Read by the `new.room` procedure (step 8) to reposition EGO into the new room; cleared to 0 by step 9. |
| `var(3)` | Current score. The interpreter monitors changes to this variable to redraw the on-screen status line. |
| `var(4)` | Object number (≠ EGO) that touched a screen border [AGI 2.917 1000:164E]. Cleared at the start of the step pass, after LOGIC 0, and by `new.room` [AGI 2.917 1000:1519, 1000:0220, 1000:1812]. |
| `var(5)` | Border-touch code for the object in `var(4)`; same encoding as `var(2)` [AGI 2.917 1000:1654]. Cleared with `var(4)`. |
| `var(6)` | Direction of EGO's motion. Compass mapping: `0` = motionless, `1` = N, `2` = NE, `3` = E, `4` = SE, `5` = S, `6` = SW, `7` = W, `8` = NW. Before LOGIC 0, program control copies EGO's direction into this slot and player control copies this slot to EGO. After LOGIC 0 it is always copied to EGO [AGI 2.917 1000:017B, 1000:01EA]. Also written by `stop.motion` and `start.motion` on EGO, `move.obj` on EGO (its direction, then 0 at the finish), `wander` on EGO, the block box stopping EGO, and a type 2 input event [AGI 2.917 1000:6E2D, 1000:6E66, 1000:16A5, 1000:16E4, 1000:3F85, 1000:079D, 1000:3613]. See [[interpreter/event-loop]]. |
| `var(7)` | Maximum achievable score. |
| `var(8)` | Free heap, in whole 256-byte pages rounded down, starting near `0xE1`. Updated by allocations, the heap release, `discard.pic` and `discard.view`, but not by every release, so it can read low until the next allocation [AGI 2.917 1000:14A0]. See [[interpreter/memory-layout]]. |
| `var(9)` | Position of the first unknown word in the player's input, or 0 if there was none. It counts only the words kept so far, plus 1, so filler words don't count. That contradicts the spec's position "in the original input" [AGI 2.917 1000:190C; 2-6-Interpreter.html]. The 2-2 phrasing ("if = 0, it is the number of the word ... that was not found") is inverted. Cleared at the start of input handling every cycle, and again on a room change [AGI 2.917 1000:3586, 1000:01C9]. See [[interpreter/input-parsing]]. |
| `var(10)` | Minimum time per cycle, in 1/20-second units (50 ms per unit). Time spent on the cycle counts toward it [AGI 2.917 1000:7EB1, 1000:7E4E]. Games typically set this to 2–4. |
| `var(11)`–`var(14)` | Interpreter's internal clock: seconds, minutes, hours, days respectively. Rolls over at 60, 60 and 24, and stops during `pause`, `save.game` and `restore.game` [AGI 2.917 1000:7E35]. |
| `var(15)` | Joystick sensitivity, used when `flag(8) = 1`. |
| `var(16)` | VIEW resource ID associated with EGO, copied from EGO's object entry by the `new.room` core [AGI 2.917 1000:1819]. |
| `var(17)` | Interpreter error code. Set by the error routine, which cleans up and returns to the main loop's return point [AGI 2.917 1000:3FE8]. Examples: `1` `discard.view` of an unloaded view, `3` `set.view` of an unloaded view, `0x0B` script buffer full, `0x10` an action opcode above the limit, `0x12` drawing an unloaded picture, `0x15` `discard.pic` of an unloaded picture, `0x17` item out of bounds [AGI 2.917 1000:3F28, 1000:3B08, 1000:701D, 1000:4AED, 1000:4BE8]. The spec's "(if = 0)" is inverted. |
| `var(18)` | Additional information accompanying the error code in `var(17)` [AGI 2.917 1000:3FE8]. |
| `var(19)` | Last key pressed on the keyboard. |
| `var(20)` | Machine type: `0` = IBM PC and compatibles, `1` = PCjr, `2` = Tandy, `8` = model byte `FA` [AGI 2.917 1000:1080]. The spec's "for IBM PC it is always 0" is true but incomplete. SQ1 tests it 119 times [SQ1 data check, log 2026-11-01]. See [[entities/sound]] §"Machine types". |
| `var(21)` | One-shot window delay, in units of 0.5 seconds (10 ticks of 20 Hz). The next `print`, if `flag(15)` is clear, closes after that time or on Enter or Esc, then sets `var(21)` to 0 [AGI 2.917 1000:1D39]. See [[interpreter/command-semantics]] §"`print` windows". |
| `var(22)` | `1` on machine type 0, otherwise `3` [AGI 2.917 1000:10AD]. So type 8 gets 3 even though it uses the PC speaker. No read found in the interpreter, and SQ1 never tests it [SQ1 data check, log 2026-11-01]. |
| `var(23)` | Sound attenuation, added to each note during its envelope, so higher values are quieter. Sound chip only, on voices 1–3, with the result capped at 15 [AGI 2.917 1000:80F3]. This refines the spec's "sound volume". See [[entities/sound]] §"Attenuation envelope". |
| `var(24)` | Maximum input line length. The spec's bare `29h` is its startup value, 41 [AGI 2.917 1000:108C, 1000:3681]. See [[interpreter/event-loop]] §"Input line". |
| `var(25)` | Set by `status` only with `flag(13)` set: item number on Enter, 255 on Esc, and 0 if the list was empty. Also the item that starts highlighted [AGI 2.917 1000:3203, 1000:3305]. |
| `var(26)` | Monitor type: `0` and `1` are both CGA mode `04h`; `0` programs the mode register directly (high-res with color burst, which suggests composite) and `1` selects a BIOS palette and dithers by row. `2` = Hercules, `3` = EGA, `4` = VGA mode `13h`, selected by `-v` or detected on machine type 8 [AGI 2.917 1000:1086, 1000:00E0, 1000:8160]. A copy made at startup and restore, so `toggle.monitor` changes the internal type but not this variable [AGI 2.917 1000:1089, 1000:265A, 1000:78A9]. See [[concepts/ega-palette]]. SQ1 tests it 113 times [SQ1 data check, log 2026-11-01]. |

## Reserved flags (0–15)

`flag(0)` through `flag(15)` are reserved for interpreter use; programmers may use `flag(16)`–`flag(255)` freely [2-2-Interpreter.html §Flags used by the interpreter]. One exception in 2.917: `restart.game` skips its prompt when `flag(16)` is set [AGI 2.917 1000:2480].

| Flag | Semantics |
|---|---|
| `flag(0)` | Written by each baseline test on EGO, which runs when EGO steps or the placement search tests a position. Set if the scanned pixels so far were all water (priority 3). Any other pixel clears it, except that a stop on a black pixel leaves it as it stood, so it can be set after a failed test. Clear at priority 15 [AGI 2.917 1000:55F0, 1000:5677]. |
| `flag(1)` | Written by each cel draw of object 0: set if no pixel of the cel was drawn, otherwise cleared [AGI 2.917 1000:9E2C]. So it means "completely obscured" for EGO. `add.to.pic` uses a private object numbered 0, so it also rewrites this flag, `flag(0)` and `flag(3)`; that side effect is Runtime only. |
| `flag(2)` | Set when a parsed line contained an unknown word or at least one non-filler word. It stays clear only for a line of nothing but filler or punctuation. An unknown word does set it, which contradicts [2-6-Interpreter.html] [AGI 2.917 1000:1948]. Cleared at the start of each cycle. See [[interpreter/input-parsing]]. |
| `flag(3)` | Written by each baseline test on EGO: set if a signal pixel (priority 2) was scanned before any stop, whether or not the test passed. Clear at priority 15 [AGI 2.917 1000:5669]. |
| `flag(4)` | Set when a `said` test matches, after which every later `said` is false until it clears. Cleared at the start of each cycle (event-loop step 3) and by the `parse` command [AGI 2.917 1000:09AB, 1000:1958]. A failed `said` leaves it alone. See [[interpreter/input-parsing]]. |
| `flag(5)` | Set when a room is entered; cleared at the next event-loop step 9, after one LOGIC 0 pass. Set by step 10 of the `new.room` procedure [4-4-Logic.html §PROGRAM CONTROL COMMANDS, emphasized as "VERY IMPORTANT"] — see [[interpreter/command-semantics]] §"`new.room`". |
| `flag(6)` | Set by `restart.game` [AGI 2.917 1000:24C5]. Stays set while LOGIC 0 reruns, and clears at event-loop step 12. |
| `flag(7)` | If set, script buffer entries aren't written and the high-water count isn't updated [AGI 2.917 1000:6FEF, 1000:6FF3]. |
| `flag(8)` | If set, `var(15)` controls joystick sensitivity. |
| `flag(9)` | Sound on. Set at startup [AGI 2.917 1000:0F97]. Clearing it ends a playing sound on the next timer tick, with the completion flag set [AGI 2.917 1000:7F5A]. The interpreter monitors this flag to redraw the on-screen status line. |
| `flag(10)` | Gates the command trace: `trace.on` and Scroll Lock open it only while this is set [AGI 2.917 1000:8BF3]. The interpreter was not found writing it or responding to ALT-D, which contradicts the spec, on negative evidence; see [[interpreter/debug-modes]]. |
| `flag(11)` | Set at startup and after a restore, on any machine other than type 0 [AGI 2.917 1000:10BB, 1000:2670]. No code clearing or testing it was found, and SQ1's scripts don't touch it [SQ1 data check, log 2026-11-01]. This contradicts the spec, which has it set during the first run of LOGIC 0 [2-2-Interpreter.html §Flags used by the interpreter]. |
| `flag(12)` | Set by a successful `restore.game` [AGI 2.917 1000:2684]. Stays set while LOGIC 0 reruns, and clears at event-loop step 12. |
| `flag(13)` | If set, the `status` command lets the player select inventory items. |
| `flag(14)` | Tested only when `menu.input` runs. If set, the menu opens at the next cycle's input step [AGI 2.917 1000:92F3, 1000:358B]. |
| `flag(15)` | One-shot "leave the window open". The next `print` returns at once with its window still open, and clears this flag [AGI 2.917 1000:1CFE]. That contradicts the spec's reading of it as a mode where the player dismisses the window. When clear, the window closes after `var(21)` or on Enter or Esc. `show.pic` also clears it [AGI 2.917 1000:4B8B]. `quit`, `pause` and `version` share this wait, so `quit(0)` exits without confirmation when this flag or `var(21)` is set [AGI 2.917 1000:0296, 1000:1D16, 1000:1D7D]. See [[interpreter/command-semantics]] §"`print` windows". |

## Spec ambiguities

The spec's `var(9)` and `var(17)` descriptions read as inverted, and the source HTML flags them with translator's notes. Both are now settled for 2.917 in the table above.

## See also

- [[interpreter/event-loop]] — the per-frame cycle that reads, clears, and writes the reserved variables and flags
- [[interpreter/debug-modes]] — runtime inspection / mutation of variables and flags (uses `flag(10)`)
- [[concepts/agi-data-types]] — the broader catalog of parameter types (strings, words, objects, inventory items, messages) that variables and flags belong to
