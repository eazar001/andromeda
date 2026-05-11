# Event Loop

The LOGIC interpreter runs an unbounded cycle of eleven ordered operations per frame, repeating until the game ends or a room transition requires the cycle to restart. This page documents the per-frame sequence in detail, including which reserved variables and flags are read, written, or cleared at each step [2-2-Interpreter.html §Interpreter work cycle].

## Cycle at a glance

Each interpreter cycle performs the following operations, in order:

1. **Time delay** — sleep for `var(10) × 50` ms.
2. **Clear keyboard buffer.**
3. **Clear transient input flags** — `flag(2)` and `flag(4)` set to 0.
4. **Poll input** — sample keyboard and joystick.
5. **Update EGO direction** — read or write `var(6)` depending on control mode.
6. **Recalculate object motion** — for objects under `animate_obj` / `start_update` / `draw`.
7. **Status-line refresh** — if `var(3)` (score) or `flag(9)` (sound) has changed since last cycle.
8. **Execute LOGIC 0** — and any LOGICs it calls.
9. **Post-LOGIC cleanup** — fixed sequence of cleanup commands and variable resets.
10. **Update all on-screen objects** — animate next cels, reposition, redraw.
11. **Room-transition check** — if `new_room` or `new_room_v` was issued during LOGIC, re-enter step 1 for the new room; otherwise loop back to step 1 in the current room.

The cycle is described in the spec as a block diagram; the rest of this page expands each step with the state-management details.

## Step 1: Time delay

The interpreter sleeps for the delay interval given by `var(10)`, in units of 1/20 second (50 ms per unit). On startup `var(10) = 0`; games typically set it to 2–4 to target ~10–20 FPS on original hardware [2-2-Interpreter.html §Variables used by the interpreter, §Interpreter work cycle]. The delay sits at the start of the cycle so input arriving during the sleep is queued and visible to step 4.

## Step 2: Clear keyboard buffer

The keyboard input buffer is flushed, discarding any queued keypresses left over from before this cycle [2-2-Interpreter.html §Interpreter work cycle].

## Step 3: Clear transient input flags

`flag(2)` (player-input-received) and `flag(4)` (said-command-accepted) are reset to 0 [2-2-Interpreter.html §Interpreter work cycle]. These are signaling flags that LOGIC sets to communicate input/parsing results within a single cycle; the interpreter clears them every cycle so each LOGIC run starts from a clean slate.

## Step 4: Poll input

The interpreter samples the keyboard and joystick [2-2-Interpreter.html §Interpreter work cycle].

## Step 5: Update EGO direction

`var(6)` (EGO direction) is then read or written depending on the control mode in effect [2-2-Interpreter.html §Interpreter work cycle]:

- **Program control** — EGO direction is read *from* `var(6)`. LOGIC has set the value via `move_obj`, `set_dir`, or similar; keyboard input is ignored for motion purposes.
- **Player control** — Keyboard/joystick input from step 4 is written *into* `var(6)`, so LOGIC sees the player's intended direction.

Control mode is switched by the LOGIC commands `player_control` and `program_control` (semantics deferred to [[interpreter/commands]]).

## Step 6: Recalculate object motion

For every object on which `animate_obj`, `start_update`, and `draw` have been issued, the interpreter recalculates its direction of motion in preparation for the next render [2-2-Interpreter.html §Interpreter work cycle].

## Step 7: Status-line refresh

If `var(3)` (score) or `flag(9)` (sound on/off) has changed since the last cycle, the on-screen status line is redrawn [2-2-Interpreter.html §Interpreter work cycle].

## Step 8: Execute LOGIC 0

LOGIC resource 0 is loaded at game start and remains resident for the entire session; it is the entry point for every interpreter cycle [2-2-Interpreter.html §General principles of the interpreter operation, §Interpreter work cycle]. LOGIC 0 typically dispatches to room-specific LOGICs, which may load and call further LOGICs in turn. The number of commands executed per cycle varies with the runtime state (puzzle progress, conditional branches, input flags). When LOGIC 0 returns, control flows to step 9.

At the end of LOGIC 0 execution the interpreter re-checks the status-line triggers from step 7 (`var(3)` and `flag(9)`) — LOGIC may have mutated either, and the status line is redrawn if so.

## Step 9: Post-LOGIC cleanup

A fixed sequence of commands runs after every LOGIC 0 return [2-2-Interpreter.html §Interpreter work cycle]:

- `stop_update` for all animated objects
- `unanimate_all` — reset every view object to its base cel
- Destroy every loaded LOGIC resource *except* LOGIC 0, freeing their memory
- `player_control` — switch control mode for EGO
- `unblock` — clear any motion-blocking state
- `set_horizon 36` — reset the horizon line to Y = 36
- `var(1) = var(0)` — save current room as previous room for next cycle
- `var(0) = n` if `new_room n` was issued, or `var(0) = var(n)` if `new_room_v n` was issued (the latter takes a variable index that is dereferenced to get the actual room number)
- `var(4) = 0`, `var(5) = 0`, `var(9) = 0` — clear border-touch object, border-touch code, unparsed-word index
- `var(16) = ` VIEW ID of EGO (looked up via the OBJECT resource)
- `var(2) = 0` — clear EGO border-touch code
- `flag(2) = 0` — clear player-input-received flag
- `flag(5) = 1` — set first-room-execution flag for the next cycle

These resets enforce the discipline that signaling flags and per-frame state variables expire at cycle boundaries: if LOGIC doesn't observe an event during the cycle in which it occurs, the next cycle treats it as if it never happened (agidev, unverified — staleness semantics inferred from the clearing list; not made explicit in the spec).

## Step 10: Update all on-screen objects

All screen objects (visible view objects, animated props, controllable actors) are repositioned and animated to their next cel, and the screen is redrawn [2-2-Interpreter.html §Interpreter work cycle]. This is the rendering pass; everything LOGIC set up during step 8 lands on screen here.

## Step 11: Room-transition check

The interpreter tests whether a `new_room` or `new_room_v` command was issued during LOGIC 0 (step 8). If so, control flows back to step 1 with the new room's state active (room-resource loading timing across the transition not fully specified at this chapter's depth — agidev, unverified). Otherwise, the cycle loops back to step 1 with the current room's state intact.

## Transient-state discipline

Several reserved variables and flags carry strict per-cycle semantics that derive from steps 3 and 9 above:

- **Input-received flags** (`flag(2)`, `flag(4)`) signal *this* cycle's parsing results; they are cleared at the start of the next cycle.
- **Border-touch variables** (`var(2)`, `var(4)`, `var(5)`) and `var(9)` (unparsed-word index) are cleared during post-LOGIC cleanup; their values are only valid within the cycle in which the event occurred.
- **First-room-execution flag** (`flag(5)`) is set on the first cycle of every new room and cleared after that cycle's cleanup, so room-initialization LOGIC has exactly one frame to run.

See [[interpreter/variables-and-flags]] for the complete table of reserved slots and their semantics.

## See also

- [[interpreter/variables-and-flags]] — every reserved variable and flag referenced by the cycle
- [[interpreter/commands]] — full opcode catalogue; control-flow and object-animation commands that interact with the cycle.
- [[interpreter/view-objects]] — on-screen object state model (43-byte table entry for SQ2), animation-cel sequencing via `cycle_time` and `cycle_type` fields, and collision-test commands
