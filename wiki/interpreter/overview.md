# Interpreter Overview

The LOGIC interpreter is the runtime that executes game logic scripts (LOGIC resources) and manages world state: player character position and animation, controllable and non-controllable objects on screen, variables and flags, screen rendering with priority-based occlusion, and input handling. This page introduces the major components; subsequent Interpreter pages detail each subsystem.

## What is AGI?

AGI stands for *Adventure Game Interpreter* — Sierra On-Line's 2D adventure-game engine that shipped roughly 1984–1989 [2-1-Interpreter.html §What is AGI?]. It powered titles including Kings Quest 1–3, Space Quest 1–2, Police Quest, Leisure Suit Larry, Black Cauldron, Gold Rush, Mixed Up Mother Goose, and Manhunter 1–2 before being superseded by SCI for later Sierra titles. Three major versions shipped: v1 (CGA graphics, KQ1–2), v2 (16-color EGA, most games), and v3 (data compression, used by five games before being replaced by SCI) [2-1-Interpreter.html §How many versions].

## The LOGIC virtual machine

The interpreter runs compiled scripts stored in LOGIC resources. The command language contains approximately 181 procedure-type commands (imperative actions) and approximately 18 test commands (boolean predicates), plus standard control-flow keywords (`if`, `else`, `not`, `or`, `and`, `goto`, `return`) [2-1-Interpreter.html §What are the AGI commands?]. See [[interpreter/commands]] for the full opcode tables (to be ingested with Group 3 — Logic).

## Variables and flags

The interpreter maintains 256 8-bit variables (`var(0)`–`var(255)`) and 256 single-bit flags (`flag(0)`–`flag(255)`) as the primary game-state store. Reserved variables `var(0)`–`var(26)` track current/previous room, score, EGO motion and border collisions, input state, error codes, the internal clock, and hardware configuration; reserved flags `flag(0)`–`flag(15)` carry input signals, animation state, debug mode, sound on/off, and window behavior [2-2-Interpreter.html §Variables used by the interpreter, §Flags used by the interpreter]. Variables and flags share a single global namespace across all loaded LOGIC resources. See [[interpreter/variables-and-flags]] for the complete table and shared-state scoping rules.

Variables and flags are two of seven semantic data types that AGI commands consume as parameters; see [[concepts/agi-data-types]] for the full catalog (variables, flags, strings, words, objects, inventory items, messages).

## Screen objects and priority bands

The visible screen consists of *screen objects* — controllable view objects (ego, NPCs) and non-controllable ones (animated props, scenery elements) — each with position `(x, y)`, view/loop/cel animation state, and a priority value. The screen is divided into approximately eleven invisible horizontal priority bands [2-1-Interpreter.html §What are the priority bands?]; an object's vertical position determines its band, and the per-pixel priority screen (encoded in PICTURE resources alongside the visual screen) controls occlusion so objects appear behind trees, rocks, and other scenery (agidev, unverified — exact band boundaries and occlusion algorithm specified in later chapters). See [[interpreter/priority-bands]].

## Control lines

The priority screen also encodes *control lines* — colored lines that trigger interpreter behavior when objects cross or touch them [2-1-Interpreter.html §What are the priority bands?]:

- **Black** — unconditional obstacle; motion is blocked.
- **Blue** — conditional obstacle; LOGIC can permit or forbid crossing.
- **Green** — alarm line; typically triggers a script (falling, drowning, scene transition).
- **Cyan** — water boundary; objects flagged `object.on.water` are confined to cyan regions (agidev, unverified — exact constraint semantics deferred to [[interpreter/control-lines]]).

## Ego

*Ego* is the conventional name for the main player character in interpreter commands (e.g., `follow.ego`, `position.ego`). Every AGI game uses the name "ego" in its LOGIC scripts regardless of the in-fiction character (Rosella, Roger Wilco, and so on) [2-1-Interpreter.html §What is ego?].

## View objects and animation

All visible on-screen content — props, controllable actors, animated background elements, and inventory-item icons — is rendered from VIEW resources. A VIEW contains animation *loops* (cycles), each of which holds a sequence of *cels* (individual frames) [2-1-Interpreter.html §What are the LOGIC, PICTURE, SOUND, and VIEW data files?]. See [[interpreter/view-objects]] (screen-object model and animation timing) and [[entities/view]] (byte-level VIEW resource format — to be ingested with Group 5).

## The event loop

Each interpreter cycle is an ordered sequence of eleven operations: time delay, keyboard-buffer clear, transient-flag clear, input poll, EGO-direction update, object-motion recalculation, status-line refresh, LOGIC 0 execution, post-LOGIC cleanup, on-screen object update, and room-transition check [2-2-Interpreter.html §Interpreter work cycle]. The cleanup step also clears most signaling flags and per-frame variables, giving those slots strict cycle-scoped semantics. See [[interpreter/event-loop]] for the step-by-step sequence and the state-management details.

## Input parsing

When the player enters a command line (step 4 of the event loop), the interpreter preprocesses the input — punctuation removal, lowercase normalization, multi-space collapsing — then performs vocabulary lookup to convert each surviving word into a numeric code. `var(9)` reports the position of any unparsed word; `flag(2)` signals that the input line parsed successfully; `flag(4)` signals that a `said` test has already consumed the input this cycle. The `said` test command matches the resulting word-code sequence against patterns with two wildcards: `1` matches any single word, `9999` matches the rest of the input [2-6-Interpreter.html]. See [[interpreter/input-parsing]].

## Debug modes

Most shipped games left debug mode active. It is activated via ALT-D or a per-game magic phrase (e.g., "bird man" in Gold Rush, "rats ass" in Kings Quest 3, "stink bug" in Police Quest) [2-1-Interpreter.html §What are the debug modes?]. Standard debug commands include:

- `TP` — teleport to another room.
- `GET OBJECT` / `GIMME GIMME` — acquire inventory items.
- `SHOW PRIORITY` / `SHOW FLAG` / `SHOW VAR` — inspect game state.
- `SET FLAG` / `SET VAR` — mutate game state.
- `POSITION` / `SHOW POSITION` — inspect or move ego.
- `OBJECT NUMBER` / `OBJECT ROOM` — list inventory or locate items.
- `ROOM` — show current room number.
- `SET PRIORITY` / `RELEASE PRIORITY` — adjust ego's priority band.

Most games also support a command-trace mode (Scroll-Lock) that single-steps through executed test commands, displaying the LOGIC index, parameter values, and the boolean result [2-1-Interpreter.html §What are the debug modes?]. See [[interpreter/debug-modes]].

## Resource types

Game content is organized into five resource categories [2-1-Interpreter.html §What are the LOGIC, PICTURE, SOUND, and VIEW data files?]:

- **LOGIC** — script bytecode driving a single room's behavior, with optional appended encrypted text messages. See [[entities/logic]] (to be ingested with Group 3 — Logic).
- **PICTURE** — vector-based room drawings; encodes both a visual screen and a priority/control-line screen. See [[entities/picture]] (to be ingested with Group 4 — Picture).
- **VIEW** — sprite and animation data: actors, NPCs, props, inventory icons. See [[entities/view]] (to be ingested with Group 5 — View).
- **SOUND** — musical scores and sound effects (PC-speaker mono, PCjr polyphonic). See [[entities/sound]] (to be ingested with Group 6 — Sound).

`WORDS.TOK` (the parser dictionary) and `OBJECT` (the inventory list) are auxiliary files at the file-system layer; their formats will be detailed when the relevant chapters are ingested. The on-disk container — VOL files and the DIR index that points into them — is already documented under [[entities/dir-file]] and [[entities/vol-file]].

## Implementation status

The Python prototype implements only the file-system layer (DIR/VOL parsing, OBJECT decryption, VIEW decoding). There is no LOGIC VM, event loop, or screen renderer wired up — those subsystems are the focus of the planned Rust rewrite. Spec claims in this overview about command semantics, variable scoping, priority occlusion, and event-loop ordering therefore cannot be cross-checked against working code at present. The runtime heap layout documented in [[interpreter/memory-layout]] is similarly unverifiable without external memory instrumentation on original hardware.
