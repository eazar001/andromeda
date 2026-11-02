# Interpreter Overview

The LOGIC interpreter is the runtime that executes game logic scripts (LOGIC resources) and manages world state: player character position and animation, controllable and non-controllable objects on screen, variables and flags, screen rendering with priority-based occlusion, and input handling. This page introduces the major components; subsequent Interpreter pages detail each subsystem.

## What is AGI?

AGI stands for *Adventure Game Interpreter* — Sierra On-Line's 2D adventure-game engine that shipped roughly 1984–1989 [2-1-Interpreter.html §What is AGI?]. It powered titles including Kings Quest 1–3, Space Quest 1–2, Police Quest, Leisure Suit Larry, Black Cauldron, Gold Rush, Mixed Up Mother Goose, and Manhunter 1–2 before being superseded by SCI for later Sierra titles. Three major versions shipped: v1 (CGA graphics, KQ1–2), v2 (16-color EGA, most games), and v3 (data compression, used by five games before being replaced by SCI) [2-1-Interpreter.html §How many versions].

## The LOGIC virtual machine

The interpreter runs compiled scripts stored in LOGIC resources. The command language contains 182 action commands (imperative opcodes `$00..$B5`) and 18 test commands (boolean predicates `$01..$12`), plus standard control-flow keywords (`if`, `else`, `not`, `or`, `and`, `goto`, `return`) [2-1-Interpreter.html §What are the AGI commands?; 4-3-Logic.html §Action commands, §Text commands]. The bytecode container — header layout, control-flow opcodes (`$FF` `if`, `$FE` `else/goto`, `$FD` `not`, `$FC` `or` brackets), argument dispatch via AGIDATA.OVL, and the Avis-Durgan-encrypted text-message section — is documented in [[entities/logic]] [4-1-Logic.html]. The full opcode catalogue with per-argument signatures lives at [[interpreter/commands]] [4-3-Logic.html].

## Variables and flags

The interpreter maintains 256 8-bit variables (`var(0)`–`var(255)`) and 256 single-bit flags (`flag(0)`–`flag(255)`) as the primary game-state store. Reserved variables `var(0)`–`var(26)` track current/previous room, score, EGO motion and border collisions, input state, error codes, the internal clock, and hardware configuration; reserved flags `flag(0)`–`flag(15)` carry input signals, animation state, debug mode, sound on/off, and window behavior [2-2-Interpreter.html §Variables used by the interpreter, §Flags used by the interpreter]. Variables and flags share a single global namespace across all loaded LOGIC resources. See [[interpreter/variables-and-flags]] for the complete table and shared-state scoping rules.

Variables and flags are two of seven semantic data types that AGI commands consume as parameters; see [[concepts/agi-data-types]] for the full catalog (variables, flags, strings, words, objects, inventory items, messages).

## Screen objects and priority bands

The visible screen consists of *screen objects* — controllable view objects (ego, NPCs) and non-controllable ones (animated props, scenery elements) — each with position `(x, y)`, view/loop/cel animation state, and a priority value. The screen is divided into eleven horizontal priority bands (indices 4..14) [2-1-Interpreter.html §What are the priority bands?, 4-4-Logic.html §OBJECT DESCRIPTION COMMANDS]; an object's vertical position determines its band per the y → priority table in [[interpreter/priority-bands]]. The dual-screen model (visual + priority) and per-screen init colors are documented in [[concepts/screen-layers]]; the per-pixel priority screen carried by PICTURE resources controls occlusion so objects appear behind trees, rocks, and other scenery. The per-pixel comparison is in [[interpreter/priority-bands]] §"How a cel pixel is compared".

## Control lines

The priority screen also encodes *control lines* — colored lines that trigger interpreter behavior when objects cross or touch them [2-1-Interpreter.html §What are the priority bands?; 5-1-PICTURE.html §CONTROL LINES]:

- **Black** (priority 0) — unconditional obstacle; motion is blocked.
- **Blue** (priority 1) — conditional obstacle; LOGIC can permit or forbid crossing.
- **Green** (priority 2) — alarm line; typically triggers a script (falling, drowning, scene transition).
- **Cyan** (priority 3) — water boundary; objects flagged `object.on.water` are confined to cyan regions, and `object.on.land` refuses a baseline that is entirely cyan. See [[interpreter/control-lines]].

See [[interpreter/control-lines]] for the per-color semantics, the search-downwards algorithm that recovers a priority-band value under a control-line pixel, and the relationship to flood-fill boundary detection in [[entities/picture]].

## Ego

*Ego* is the conventional name for the main player character in interpreter commands (e.g., `follow.ego`, `position.ego`). Every AGI game uses the name "ego" in its LOGIC scripts regardless of the in-fiction character (Rosella, Roger Wilco, and so on) [2-1-Interpreter.html §What is ego?].

## View objects and animation

All visible on-screen content — props, controllable actors, animated background elements, and inventory-item icons — is rendered from VIEW resources. A VIEW contains animation *loops* (cycles), each of which holds a sequence of *cels* (individual frames) [2-1-Interpreter.html §What are the LOGIC, PICTURE, SOUND, and VIEW data files?]. See [[interpreter/view-objects]] (screen-object model and animation timing) and [[entities/view]] (byte-level VIEW resource format).

## The event loop

Each interpreter cycle waits for the timer, clears the controller table and transient flags, drains queued input, syncs EGO's direction, updates object motion, runs LOGIC 0, redraws the status line if needed, and updates objects on screen. Input is polled by a timer routine and queued, not read once per cycle. A room change takes effect straight after LOGIC 0. The spec's eleven-step version differs in several places; see [[interpreter/event-loop]].

## Input parsing

When the player presses Enter on a command line, the interpreter preprocesses the input, then looks each word up in the vocabulary to get a numeric code. `var(9)` reports the position of any unknown word, `flag(2)` signals that the line produced an unknown word or at least one kept word, and `flag(4)` signals that a `said` test has already matched. The `said` test matches the word codes against patterns with two wildcards: `1` matches any single word, and `9999` matches the rest of the input. See [[interpreter/input-parsing]].

## Debug modes

In 2.917 the interpreter's own debugging features are a command trace, which Scroll Lock toggles while `flag(10)` is set, and a few commands such as `show.mem` and `obj.status.v`. The spec describes a built-in debugger with ALT-D and typed commands, but in SQ1 those are ordinary LOGIC script, written per game. See [[interpreter/debug-modes]].

## Resource types

Game content is organized into five resource categories [2-1-Interpreter.html §What are the LOGIC, PICTURE, SOUND, and VIEW data files?]:

- **LOGIC** — script bytecode driving a single room's behavior, with an appended Avis-Durgan-XOR'd text-message section. See [[entities/logic]] for the on-disk format.
- **PICTURE** — vector-based room drawings; encodes both a visual screen and a priority/control-line screen. See [[entities/picture]] for the on-disk format and [[concepts/screen-layers]] for the dual-screen model.
- **VIEW** — sprite and animation data: actors, NPCs, props, inventory icons. See [[entities/view]] for the on-disk format and [[interpreter/view-objects]] for the runtime screen-object model.
- **SOUND** — musical scores and sound effects (PC-speaker mono, PCjr polyphonic four-voice). 8-byte header of per-voice offsets pointing to four streams of 5-byte notes (duration, frequency divisor or noise selector, attenuation). See [[entities/sound]] for the on-disk format and [[concepts/pcjr-sound-encoding]] for the tone/noise/attenuation encoding primitives.

`WORDS.TOK` (the parser dictionary) and `OBJECT` (the inventory list) are auxiliary files at the file-system layer; their formats are documented at [[entities/words-tok]] and [[entities/object]] respectively. The on-disk container — VOL files and the DIR index that points into them — is documented under [[entities/dir-file]] and [[entities/vol-file]].

## Implementation status

The Python prototype implements only the file-system layer (DIR/VOL parsing, OBJECT decryption, VIEW decoding). There is no LOGIC VM, event loop, or screen renderer wired up — those subsystems are the focus of the planned Rust rewrite. Spec claims in this overview about command semantics, variable scoping, priority occlusion, and event-loop ordering therefore cannot be cross-checked against working project code at present. They are being checked against the AGI 2.917 binary instead; see [[sources/agi-2917-binary]]. That includes the heap layout in [[interpreter/memory-layout]].
