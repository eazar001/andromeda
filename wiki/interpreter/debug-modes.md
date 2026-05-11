# Debug Modes

The AGI interpreter ships with a built-in debugger that most Sierra games left active in their released binaries. Activation and command vocabulary are documented in [2-1-Interpreter.html §What are the debug modes?].

## Activation

**Universal:** ALT-D toggles the debugger (`flag(10)`).

**Per-game magic phrases** — typed at the in-game input prompt, they activate (or in some games deactivate) the debugger:

| Game | Magic phrase |
|---|---|
| Gold Rush | `bird man` |
| King's Quest 3 | `rats ass` |
| Police Quest | `stink bug` |

(Other AGI titles have their own phrases; the above are the examples enumerated in 2-1.)

## Debug command vocabulary

When debug mode is active, the in-game input prompt accepts these commands in addition to normal game commands:

| Command | Action |
|---|---|
| `TP` | Teleport to another room |
| `GET OBJECT` / `GIMME GIMME` | Acquire all inventory items |
| `SHOW PRIORITY` | Overlay the priority screen on the display |
| `SHOW FLAG` | Display all flag values |
| `SHOW VAR` | Display all variable values |
| `SET FLAG <n>` | Set `flag(n)` to 1 |
| `SET VAR <n> <v>` | Set `var(n)` to value `v` |
| `POSITION` | Print ego's current `(x, y)` |
| `SHOW POSITION` | Same as POSITION |
| `OBJECT NUMBER` | List all inventory items and their indices |
| `OBJECT ROOM` | Print the room each inventory item is in |
| `ROOM` | Print current room number |
| `SET PRIORITY <n>` | Set ego's priority band to `n` |
| `RELEASE PRIORITY` | Re-enable auto-priority from the y-band table |

## Command-trace mode

Scroll-Lock activates a single-step trace mode that displays — on every `if` evaluation — the LOGIC index, the test command being evaluated, its parameter values, and the boolean result. Useful for tracing room-script branching in real time [2-1-Interpreter.html §What are the debug modes?]. Related LOGIC opcodes: `$95 trace.on`, `$96 trace.info` (see [[interpreter/commands]]).

## Flag

`flag(10)` is the interpreter-managed activation flag for the built-in debugger. See [[interpreter/variables-and-flags]] §"Reserved flags (0–15)".

## See also

- [[interpreter/variables-and-flags]] — `flag(10)` reserved-flag semantics.
- [[interpreter/commands]] — `$95 trace.on`, `$96 trace.info` opcodes.
- [[sources/2-1-interpreter]] — source chapter.
