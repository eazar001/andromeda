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
9. **Post-LOGIC reset** — apply `var(6)` to EGO's direction, refresh the status line if needed, and clear `var(4)`, `var(5)`, `flag(5)`, `flag(6)`, `flag(12)`.
10. **Update all on-screen objects** — animate next cels, reposition, redraw.
11. **Room-transition check** — if `new_room` or `new_room_v` was issued, run the room-change procedure and re-enter **step 8** directly; otherwise loop back to step 1.

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

## Step 9: Post-LOGIC reset

This small reset runs after every LOGIC 0 return [2-2-Interpreter.html §Interpreter work cycle]:

- EGO's direction of motion is taken from `var(6)`.
- If `var(3)` (score) or `flag(9)` (sound) changed, the status line is redrawn.
- `var(4) = 0`, `var(5) = 0`.
- `flag(5) = 0`, `flag(6) = 0`, `flag(12) = 0`.

## Step 10: Update all on-screen objects

All screen objects (visible view objects, animated props, controllable actors) are repositioned and animated to their next cel, and the screen is redrawn [2-2-Interpreter.html §Interpreter work cycle]. This is the rendering pass; everything LOGIC set up during step 8 lands on screen here.

## Step 11: Room-transition check

The interpreter tests whether a `new_room` or `new_room_v` command was issued. If not, the cycle loops back to step 1 with the current room's state intact. If so, it runs the room-change procedure below and returns directly to step 8, skipping the delay, keyboard clear, and input poll [2-2-Interpreter.html §Interpreter work cycle, block diagram].

> [!conflict] When `new.room` takes effect
> The 2-2 diagram tests for `new_room` at the end of the cycle, after LOGIC 0 and the object update. [4-4-Logic.html §PROGRAM CONTROL COMMANDS] describes `new.room` as performing the procedure itself and then returning to the main loop, which reads as taking effect at the call. Neither source says whether commands after `new.room` in the same LOGIC still run. Unresolved; needs a ScummVM cross-check (agidev, unverified).

### Room-change procedure

This runs **only** when a room change was issued, never on an ordinary cycle [2-2-Interpreter.html §Interpreter work cycle, block diagram]. See [[interpreter/command-semantics]] §"`new.room`" for the 4-4 version of the same procedure.

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
- EGO's coordinates are set from `var(2)`, then `var(2) = 0`
- `flag(2) = 0` — clear player-input-received flag
- `flag(5) = 1` — set first-room-execution flag, which LOGIC 0 sees when step 8 re-runs
- The status line's stored score is updated from `var(3)`

## Transient-state discipline

Several reserved variables and flags carry strict per-cycle semantics that derive from steps 3 and 9 above:

- **Input-received flags** (`flag(2)`, `flag(4)`) signal *this* cycle's parsing results; they are cleared at the start of the next cycle.
- **Object border-touch variables** (`var(4)`, `var(5)`) are cleared at step 9 of every cycle, so they are valid only until LOGIC 0 returns.
- **EGO's border code and the unparsed-word index** (`var(2)`, `var(9)`) are cleared only by the room-change procedure; the diagram shows no per-cycle reset for them.
- **First-room-execution flag** (`flag(5)`) is set by the room-change procedure and cleared at the next step 9, so room-initialization LOGIC sees it for exactly one LOGIC 0 pass.

See [[interpreter/variables-and-flags]] for the complete table of reserved slots and their semantics.

## See also

- [[interpreter/variables-and-flags]] — every reserved variable and flag referenced by the cycle
- [[interpreter/commands]] — full opcode catalogue; control-flow and object-animation commands that interact with the cycle.
- [[interpreter/view-objects]] — on-screen object state model (43-byte table entry for SQ2), animation-cel sequencing via `cycle_time` and `cycle_type` fields, and collision-test commands
