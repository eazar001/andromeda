# Building an AGI 2.917 Interpreter

A start-to-finish guide to reimplementing the AGI interpreter that ships with Space Quest 1, built from the audited wiki in `andromeda-wiki/`. It follows the order you'd build in, and for each stage it gives the rules that matter, the traps, and the wiki pages that hold the full detail. It's prose and tables only: the algorithms are yours to design.

## How to read this

**Scope.** AGI v2, interpreter 2.917, as shipped with the local SQ1. Every rule here was checked against that interpreter, first by reading its code and then, for anything load-bearing, by running it whole under emulation. Other v2 versions differ in small ways ([interpreter/command-evolution](andromeda-wiki/interpreter/command-evolution.md)), and v3 isn't covered.

**Sources.** Each section names its wiki pages. The pages carry the citations: `[AGI 2.917 …]` for code that was read, and `[2.917 runtime: …]` for behavior observed on the running interpreter. The runtime citations name scenarios in `tools/agi_emu/scenarios.py`, which you can rerun.

**Fidelity policy.** The interpreter has two kinds of odd behavior. Some of it is observable by a well-formed game and should be reproduced. The rest only happens when a game does something invalid, and it should be treated as an error. The last section lists which is which.

**An oracle.** `tools/agi_emu/` runs the real interpreter on the real game files, with your own test LOGIC, PICTURE, VIEW or SOUND substituted. For any stage below, you can run the same input through it and compare your result with the interpreter's buffer, variables, flags or port writes. "Using the harness as an oracle" at the end says how.

## Build order

| Stage | Build | Wiki pages | Check against |
|---|---|---|---|
| 1 | Game files: directories, VOL, OBJECT, WORDS.TOK | `entities/dir-file`, `entities/vol-file`, `entities/object`, `entities/words-tok` | SQ1 data |
| 2 | Machine state and startup | `interpreter/variables-and-flags`, `interpreter/memory-layout` | `boot()` in the harness |
| 3 | The screen buffer and PICTURE | `concepts/screen-layers`, `entities/picture`, `concepts/picture-rendering`, `concepts/ega-palette` | `tools/picture_emu/`, `ega_display_matches_buffer` |
| 4 | LOGIC and the VM | `entities/logic`, `interpreter/commands`, `interpreter/command-semantics` | Synthetic LOGIC 0 in the harness |
| 5 | The cycle and rooms | `interpreter/event-loop`, `interpreter/command-semantics` §`new.room` | `priority_table_and_cycle_delay` |
| 6 | Objects | `entities/view`, `concepts/rle-encoding`, `interpreter/view-objects`, `interpreter/priority-bands`, `interpreter/control-lines` | The object and drawing scenarios |
| 7 | Input and the parser | `interpreter/event-loop` §"Input events", `interpreter/input-parsing` | `said_with_filler_words` |
| 8 | Text, windows, menus, inventory | `interpreter/command-semantics` §§"Text output", "Menus", "`status`" | `menu_delivery_and_look`, `status_selection` |
| 9 | Sound | `entities/sound`, `concepts/pcjr-sound-encoding` | The sound scenarios |
| 10 | Save, restore, restart | `interpreter/save-restore`, `interpreter/memory-layout` §"The script buffer" | `save_file_bytes` |
| 11 | Debugging aids | `interpreter/debug-modes` | `trace_window_output` |

This matches the milestones in `DEVELOPMENT_PLAN.md`, with sound and save last because nothing else depends on them.

## Stage 1: game files

### Directories

Each of `LOGDIR`, `PICDIR`, `VIEWDIR` and `SNDDIR` is a flat array of 3-byte entries with no header. **The entry's position is the resource number**, so keep empty slots in place. An entry is absent when the high nibble of its first byte is `F`, whatever the other 20 bits hold. Otherwise the high nibble is the VOL number and the remaining 20 bits, big-endian, are the byte offset into that VOL file.

2.917 opens only `VOL.0` to `VOL.4`. A number past the end of a directory isn't checked and reads whatever follows in memory; treat it as absent. Loading an absent resource is fatal: the interpreter names the type, says it wasn't found, and exits.

### VOL files

Each resource starts with a 5-byte header: the signature `12 34`, the VOL number, and a little-endian payload length. 2.917 checks the signature and that the VOL byte equals the directory's VOL number, and treats a mismatch as the wrong disk. With no disk swapping, any read failure can be fatal.

### OBJECT

The whole file is XOR-encrypted with the repeating key `Avis Durgan`, starting at key index 0 at file byte 0. Decrypted:

| Bytes | Meaning |
|---|---|
| 0–1 | Offset of the name section, little-endian, counted from byte 3 |
| 2 | Highest object-table slot number. The table has this many plus 1 slots; SQ1 has 18 |
| 3 onward | 3-byte entries up to the name section: a name offset from byte 3, then the starting room |

**Resolve each name through its entry's pointer.** The names aren't one per item in order: SQ1 starts with a `?` placeholder, and two items share it. Room 255 means carried. The prototype reads names in sequence and misnumbers items 18–24; pointer lookup fixes it.

### WORDS.TOK

A 52-byte index of 26 big-endian offsets, one per starting letter, then the entries. Each entry is a count of leading characters kept from the previous word, then the rest of the word with each byte XORed with `7F` and the last byte's top bit set, then a big-endian group number. Entries are sorted, and the file ends with one extra 0 byte. Group 0 marks filler words, which parsing drops. In patterns, 1 matches any one word and 9999 the rest of the line; no vocabulary word has 9999.

## Stage 2: machine state and startup

### State to hold

| State | Size | Notes |
|---|---|---|
| Variables | 256 × 8 bits | `var(0)`–`var(26)` reserved |
| Flags | 256 × 1 bit | `flag(0)`–`flag(15)` reserved, plus `flag(16)`, which `restart.game` reads |
| Strings | 24 × 40 bytes | 39 characters and a terminator |
| Object table | slots from OBJECT byte 2, plus 1 | See stage 6 |
| Controller table | 50 entries | Cleared every cycle |
| Event queue | 20 entries of type and value | Newest dropped when full |
| `set.key` table | 39 bindings | A key code to a controller number |
| Script buffer | 50 entries by default | Stage 10 |
| Screen buffer | 160 × 168 bytes | Stage 3 |
| Clock | `var(11)`–`var(14)` | Driven at 20 Hz |

All variables and flags start at 0, and every LOGIC shares them. The reserved slots are listed with their exact writers and readers in [interpreter/variables-and-flags](andromeda-wiki/interpreter/variables-and-flags.md). A few behave unlike the spec, so read that page before using one:

- `flag(8)` and `var(15)` are joystick double-click detection and its time window, not sensitivity.
- `var(19)` is the last key drained this cycle, cleared each cycle.
- `var(9)` counts only kept words.
- `flag(11)` is set at startup on any machine other than type 0 and never used.

### Startup

Startup parses the command-line switches, detects the machine and display, and loads the four directories, `WORDS.TOK` and `OBJECT`. It sets up the object table, loads LOGIC 0, and sets `var(20)` (machine), `var(22)`, `var(24)` = 41 (input length), `var(26)` (monitor), `flag(5)` and `flag(9)`. The switches are `-c`, `-r`, `-h`, `-e` and `-v` for the display, and `-p`, `-t` and `-s` for the machine; see [concepts/ega-palette](andromeda-wiki/concepts/ega-palette.md) §"Other displays" and [entities/sound](andromeda-wiki/entities/sound.md) §"Machine types".

### Memory

2.917 runs on a fixed 57,744-byte bump-allocated heap, whatever the machine has. Resources stack up and are released from the top. You don't need to copy that, with one exception: a game can observe a few consequences of the heap's bookkeeping. Stage 4 lists them, and you can decide case by case. If memory runs out, 2.917 prints "No memory" with the two sizes as signed 16-bit numbers and exits.

## Stage 3: the screen buffer and PICTURE

### The buffer

One buffer of 160 × 168 bytes, top row first. Each byte holds the **visual color in its low nibble and the priority in its high nibble**. There aren't two screens: everything, including drawn objects, goes into this one buffer.

- Startup and `toggle.monitor` fill it with `0x40`: color 0, priority 4.
- `draw.pic` fills it with `0x4F`, white at priority 4, then draws. `overlay.pic` draws over what's there.
- Neither touches the display. `show.pic` sends the whole buffer to the display, and from then on object updates reach the display too.

Priority 4–14 are the depth bands, 15 is closest to the viewer, and 0–3 are control values; see stage 6.

### PICTURE bytecode

A byte stream ending at `0xFF`. Opcodes `0xF0`–`0xFA` take arguments until the next byte of `0xF0` or above. Any other byte at the top level, including `0xFB`–`0xFE` and whatever follows them, is skipped. Each picture starts with both layers disabled and pen 0, and no state carries over between pictures.

| Opcode | Does |
|---|---|
| `F0 c`, `F1` | Set the visual color and enable that layer; disable it |
| `F2 p`, `F3` | Set the priority and enable that layer; disable it |
| `F4`, `F5` | Corner lines from a start point, alternating vertical then horizontal (`F4`) or the reverse (`F5`) |
| `F6` | A polyline through absolute points |
| `F7` | A polyline of relative steps, each byte packing sign-magnitude Δx and Δy of up to 7 |
| `F8` | Flood fill from each point |
| `F9 s` | Set the pen: size in bits 0–2, rectangle in bit 4, splatter in bit 5 |
| `FA` | Plot the pen at each point, preceded by a texture byte when splatter is on |

The exact rules are in [entities/picture](andromeda-wiki/entities/picture.md) and [concepts/picture-rendering](andromeda-wiki/concepts/picture-rendering.md). The ones that catch implementations out:

- **Writing a pixel** replaces the nibbles of the enabled layers and keeps the others. There's no priority test while drawing a picture.
- **Coordinates** clamp: x bytes `A0`–`EF` become 159 and y bytes `A8`–`EF` become 167. A relative step left of 0 or above 0 wraps and clamps to the far edge, drawing a line across the picture.
- **Lines** step along the longer axis with integer error terms that start at half the major length. Those terms are 8 bits, so a diagonal whose two lengths sum to more than 255 can miss its endpoint, and the next segment starts from where it really ended. This matches the line rule in `showpic.c` everywhere else.
- **Fill** qualifies pixels by the enable state: visual color 15 when the visual layer is on, otherwise priority 4. White with the visual layer on fills nothing, not even priority. The filled set is the 4-connected region containing the seed, and a plain 4-neighbor fill gives the identical result. The color byte isn't masked, so a fill with `0x1F` never terminates in 2.917; treat it as an error.
- **Pens** are `size + 1` columns by `2·size + 1` rows, not square, with the placement and clamping in [concepts/picture-rendering](andromeda-wiki/concepts/picture-rendering.md) §"Brush plotting". Circles use the masks there. Splatter uses an 8-bit shift register with feedback `B8`, restarted at each plot.

`tools/picture_emu/` runs the interpreter's own PICTURE routine. The rules model in it matches all 73 SQ1 pictures and thousands of synthetic ones pixel for pixel, so use it to check your renderer.

### Getting pixels to the display

On EGA each buffer pixel becomes two identical pixels in mode `0Dh`, using only the low nibble. The play area starts at display row `top × 8`, where `top` is the first `configure.screen` value, 0 until the game sets it. A game that keeps the status line on row 0 sets 1, which puts the picture at row 8. Other adapters map colors differently; [concepts/ega-palette](andromeda-wiki/concepts/ega-palette.md) has each driver, and the runtime pass confirmed all of them against the buffer.

`show.pri.screen` swaps the two nibbles of every byte, does a full update, waits for a key, and swaps back. So it shows priorities as colors, with any drawn objects included.

## Stage 4: LOGIC and the VM

### The resource

After the VOL header: a 2-byte text offset, counted from the first bytecode byte, then the bytecode, then the text section. The text section has a message count, an end pointer and one pointer per message. All of them count from the byte after the count, and message 1 is the first pointer. The text after the pointer table is XORed with `Avis Durgan` as one run starting at key index 0, terminators included.

### Control flow

| Byte | In code | Inside an `if` |
|---|---|---|
| `FF` | Opens a condition | Closes it, followed by a 2-byte offset added to the position after it when false |
| `FE` | `else` or `goto`: add a signed 2-byte offset to the position after it | Error `0x0F` |
| `FD` | Hangs 2.917; treat as an error | `not`, for the next test only |
| `FC` | Hangs 2.917; treat as an error | Opens or closes an `or` group; groups don't nest |
| `00` | `return` | A test that is always false |

**Conditions short-circuit**, and it matters because `said` and `have.key` have side effects. A false test outside a group fails the `if` at once. A true test inside a group skips to the group's end, and a group with no true test fails. An `if` with no tests is true. Skipping uses each test's argument count, except `said`, which reads its own count byte.

`set.scan.start` makes the byte after it the entry point for later runs of that LOGIC, and `reset.scan.start` undoes it. The entry point lives in the LOGIC's loaded record.

### Commands

The opcode table, with argument counts checked against the interpreter's own tables, is [interpreter/commands](andromeda-wiki/interpreter/commands.md). The harness generates `tools/agi_emu/opcodes.py` from it. **Don't take variable-versus-number from the type byte in `AGIDATA.OVL`**: the handlers hard-code it, and the byte is wrong for some commands. Use the signatures on the wiki page. 2.917 accepts action opcodes up to `$AD`, and anything above raises error `0x10`.

Behavior per command is in [interpreter/command-semantics](andromeda-wiki/interpreter/command-semantics.md). Some rules apply throughout:

- **Arithmetic** wraps at 8 bits. Division is unsigned, and dividing by zero isn't caught by 2.917; treat it as fatal.
- **Errors** set `var(17)` to a code and `var(18)` to a detail, then clean up much as `new.room` does, stopping sound, releasing memory and clearing the resource lists, and resume at the start of the cycle's LOGIC 0 run. So an error is survivable but drops the room's loaded resources. The codes are listed on [interpreter/variables-and-flags](andromeda-wiki/interpreter/variables-and-flags.md) and with each command.
- **Messages** past a LOGIC's count give a null pointer. `print` then shows garbage and `set.string` copies bytes from the stack base. Treat the message as empty, or as an error.
- **Loading** something already loaded does nothing. A `call` to a LOGIC that isn't loaded loads it, runs it, and releases it on return.

### Heap behavior a game can see

These come from 2.917's bookkeeping, and the runtime pass confirmed each one. A faithful reimplementation reproduces them, but no well-formed game should depend on them, so most implementations can simply avoid the corruption:

- `discard.view` and `discard.pic` release all memory loaded after the resource, but cut only their own type's list. Records of other types stay listed with stale pointers. A later `load` of one of those does nothing, and drawing it draws garbage.
- A view or picture loaded inside a temporary `call` stays listed after the call returns, with its memory reclaimed.
- `new.room` inside a temporary `call` enters the room but drops the room's LOGIC from the list.

## Stage 5: the cycle and rooms

Each cycle runs in this order:

1. **Wait** until `var(10)` ticks of 20 Hz have passed since the last cycle. Time spent working counts, and 0 means no wait.
2. **Clear** the controller table.
3. **Clear** `flag(2)` and `flag(4)`.
4. **Read the joystick**, if present.
5. **Drain the event queue**, first clearing `var(19)` and `var(9)`. A menu requested earlier runs here.
6. **Sync EGO's direction.** Under program control `var(6)` takes EGO's direction; under player control EGO takes `var(6)`.
7. **Motion pass:** pick new directions for moving objects.
8. **Snapshot** the score and `flag(9)`.
9. **Run LOGIC 0.** If it returns 0 because of `new.room`, a restore or a restart, clear `var(9)`, `var(4)`, `var(5)` and `flag(2)`, and run LOGIC 0 again at once.
10. **Set EGO's direction** from `var(6)`.
11. **Redraw the status line** if the score or `flag(9)` changed.
12. **Clear** `var(4)`, `var(5)`, `flag(5)`, `flag(6)` and `flag(12)`.
13. **Screen pass:** cycle, step and draw objects, unless the text screen is up.

The steps and their exact conditions are in [interpreter/event-loop](andromeda-wiki/interpreter/event-loop.md). Four things the spec gets wrong:

- The spec has the `var(6)` sync running the other way.
- The keyboard isn't read by the cycle: a 20 Hz timer routine polls it into the queue.
- A room change takes effect straight after LOGIC 0, before objects update.
- `var(9)` and `var(19)` clear every cycle.

**Time.** 2.917 runs a 60 Hz timer. Sound steps at 60 Hz. Every third tick drives the 20 Hz routine: the `var(10)` delay counter, the clock (20 ticks to a second), and keyboard and joystick polling. `pause`, `save.game` and `restore.game` stop the clock; menus, `status` and `print` don't.

**`new.room(n)`** takes effect at once: nothing after it in the same LOGIC runs. In order, it:

1. Stops sound.
2. Releases memory down to the resident mark and clears queued input.
3. Resets the script buffer.
4. Resets every object.
5. Clears the resource lists, keeping LOGIC 0.
6. Sets player control, removes the block, and sets the horizon to 36.
7. Sets `var(1)` to `var(0)`, then `var(0)` to `n`. Clears `var(4)` and `var(5)`. Sets `var(16)` to EGO's current view.
8. Loads LOGIC `n` without running it.
9. Moves EGO by the border it touched, from `var(2)`: 1 sets y to 167, 2 sets x to 0, 3 sets y to 37, 4 sets x to 160 minus its width. Then clears `var(2)`.
10. Sets `flag(5)`, clears the controllers, and redraws the status and input lines.

The main loop then reruns LOGIC 0, which calls the room's LOGIC as usual. Room setup sees `flag(5)` set during that rerun.

`new.room` is also where every object gets its step and cycle times of 1. A synthetic test that never changes rooms leaves them at 0.

## Stage 6: objects

### The table

43 bytes per slot, and slot 0 is EGO. The full layout is in [interpreter/view-objects](andromeda-wiki/interpreter/view-objects.md) §"The table". You only need to match it byte for byte if your save files must load into the original interpreter. The fields that matter for behavior:

- Position `x` (left column) and `y` (bottom row). The reference point is the cel's bottom-left pixel.
- View, loop, cel, and their counts.
- Step size, plus a step time and step countdown. Cycle time, plus a cycle countdown.
- Direction (0 stopped, then 1–8 clockwise from north), motion type, and cycle type.
- Priority, a 16-bit flag word, and four shared parameter bytes.

**The shared parameters overlap.** The completion flag of `end.of.loop` and `reverse.loop` sits in the same byte as `move.obj`'s target x. So `end.of.loop(n, f)` followed by `move.obj(n, x, …)` sets `flag(x)` when the loop ends. That's confirmed at runtime and SQ1 contains the pair, so reproduce it.

### Lifecycle

- `animate.obj` sets the flag word to `0x70`, overwriting everything.
- `draw` sets the updating bit, runs the position fixer and adds the object to the screen.
- `erase` clears only the drawn bit.
- `draw` and `erase` accept a number equal to the slot count, one past the table, and then write into whatever follows it. In 2.917 that's LOGIC 0's own bytecode. Treat it as an error.

### Each cycle

**Motion pass** (cycle step 7). For each active object whose step countdown is 1, its motion type picks a direction, then the block box is checked. The motion types:

- **Wander:** a random direction for a random 6 to 50 steps.
- **Follow EGO:** toward EGO, stopping within a distance, with random retreats when stuck.
- **Move to a point:** toward the target, and on arrival restores the step size, sets the flag and, for EGO, returns player control.

A direction comes from classing each axis as below, near, or above, with the step size (or the stop distance) as the threshold. So an object stops within that distance of its target, not exactly on it.

**Screen pass** (cycle step 13):

1. **Loop choice and cycling.** If an object's loop isn't fixed and its step countdown is 1, choose a loop from its direction. This works only for views with 2–3 or exactly 4 loops; with 1 or 5 and more nothing happens. Then count down cycling, and advance the cel at zero by cycle type.
2. **Erase** the updating objects.
3. **Clear** `var(2)`, `var(4)` and `var(5)`.
4. **Step** each object whose countdown is due.
5. **Redraw** in order.
6. **Clear** EGO's on-water and on-land bits.

None of this happens when no object is active.

**A step** adds step size times the direction's offset, then applies limits:

- x is kept between 0 and `160 - width`.
- y is kept between `height - 1` and 167, and below the horizon unless the object ignores it.
- Each limit hit records a border code, and the later one wins.

The new position must then pass the collision test and the control check. If either refuses, the position goes back, the border code is dropped, and the position fixer runs. A surviving border code goes to `var(2)` for EGO, or to `var(4)` and `var(5)` for others, and ends a `move.obj`.

**Step time 0** keeps the countdown at 0. The object steps every cycle, but never gets the motion pass or a loop change, so `move.obj` overshoots its target. That's observable; reproduce it.

**The position fixer** first moves an object at or above the horizon to `horizon + 1`. It then walks an outward square spiral until the position is legal. It has no limit, so a screen with no legal position hangs 2.917. Give yours a limit and report an error.

**Collision.** Two animated, drawn objects collide when neither ignores objects, their x ranges overlap with inclusive bounds, and they have the same `y` or have swapped vertical order since their last positions.

### Priority and control lines

**Automatic priority** comes from `y` through a table:

| `y` | 0–47 | 48–59 | 60–71 | 72–83 | 84–95 | 96–107 | 108–119 | 120–131 | 132–143 | 144–155 | 156–167 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Priority | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |

It's only reassigned when the control check runs, so `get.priority` straight after `position` returns the old value.

**The control check** scans the object's bottom row, left to right, on the priority nibble. It stops at the first black (0) pixel, or blue (1) unless the object ignores blocks. The check fails on a stop, or on an `on.water` or `on.land` mismatch. Green (2) sets `flag(3)`, and an all-cyan (3) row sets `flag(0)`, both for EGO only. An object fixed at priority 15 skips the scan.

**Drawing a cel** compares each non-transparent pixel with the priority on screen:

- **3 to 15:** the pixel draws if the object's priority is at least that value, and the byte takes the object's priority and the cel's color.
- **0 to 2:** search down the column for the first priority of 3 or more, and compare with that. If the pixel draws, only its color changes and the control value stays.

After drawing, EGO sets `flag(1)` if no pixel drew and clears it otherwise.

**Mirroring.** A cel whose byte 2 has bit 7 set and names another loop is flipped when drawn in a different loop. 2.917 flips it in memory and rewrites the stored loop, but drawing it flipped each time gives the same pixels.

**Draw order.** Static objects first, then updating ones. Within each group, sort by `y`, or for a fixed priority by `(priority - 5) × 12 + 48`. Ties go in table order.

### Pictures from views

`add.to.pic` draws a cel into the picture itself through a private object. Priority 0 means automatic. A margin below 4 also draws a hollow priority-only rectangle under the cel. The rectangle's height is limited to the rows that share the bottom row's band. Two quirks were confirmed at runtime:

- The private object is numbered 0, so each call clears `flag(0)`, `flag(1)` and `flag(3)`. A game can see this; reproduce it.
- A cel 1 or 2 pixels wide with a rectangle taller than 1 row overruns. Width 2 zeroes the whole screen's priority. Treat it as an error.

## Stage 7: input and the parser

### Events

Three types go through the queue:

- **Key** (type 1): goes to `var(19)`, and to the input line if input is on. A key bound with `set.key` becomes a controller event instead.
- **Direction** (type 2): sets `var(6)`, or 0 if EGO is already moving that way. Under player control it also stops EGO's motion type.
- **Controller** (type 3): sets that entry in the controller table for this cycle.

Only the eight cursor-pad keys count as directions; digits typed with Num Lock stay keys. Numeric-pad 5 queues a stop. `hold.key` makes releasing a direction key stop EGO. That needs key-release events, which a keyboard abstraction has to provide.

### The input line

- Backspace removes a character.
- Enter on a non-empty line saves it as the previous line, parses it, and clears it.
- Other keys append, up to the smaller of `var(24)` and the space left on the row.

### Parsing

1. **Separators:** space and `, . ? ! ( ) ; : [ ] { }` split words, and ``' ` - "`` are deleted inside words.
2. **Lookup:** each word is looked up case-insensitively with longest match. Entries can span several words, such as SQ1's "cartridge retrieval unit".
3. **Fillers:** group-0 words are dropped. A single "a" or "i" counts as filler unless listed.
4. **Unknown words:** parsing stops at the first one. The word count and `var(9)` become the number of words kept, plus 1, and `flag(2)` is set.
5. **Limit:** at most 10 words are kept.
6. **`flag(2)`:** set if anything was kept, or if a word was unknown.

### `said`

`said` fails at once if `flag(4)` is set, `flag(2)` is clear, or there are no words. Otherwise it walks the pattern against the words:

- `9999` matches the rest, including nothing, and succeeds.
- `1` matches any one word, including an unknown one's slot.
- Any other code must be equal.

It succeeds when both run out together, and success sets `flag(4)`, so later `said` tests that cycle fail. Fillers never reach the word list, so `said` can't see them on either side of a wildcard.

## Stage 8: text, windows, menus and inventory

### Messages

One formatter handles every message. It expands `%v` (with an optional `|` width), `%m`, `%g`, `%s`, `%w` (counted from 1) and `%o` (an item number taken from a variable), and backslash escapes the next character. It wraps at the last space. A message that would reach 20 lines is replaced with "Message too verbose". The full rules, including two wrap quirks, are in [interpreter/command-semantics](andromeda-wiki/interpreter/command-semantics.md) §"Text output and strings".

### `print`

`print` formats at width 30 and centers the window:

- **Row:** `(19 - lines) / 2 + 1`, plus the `configure.screen` offset.
- **Column:** `(40 - width) / 2`.
- **Colors:** black text on white, with a red border.

What happens next depends on `flag(15)` and `var(21)`, in that order:

- **`flag(15)` set:** it returns at once and leaves the window open, then clears the flag.
- **`var(21)` not 0:** it waits that many half-seconds, or for Enter or Esc, then clears it.
- **Neither:** it waits for Enter or Esc.

`quit(0)`, `pause` and `version` share this wait, so `quit(0)` with either set exits without asking.

### The status line

The status line shows `Score:<var 3> of <var 7>` at column 1 and `Sound:on ` or `Sound:off` at column 30. It's redrawn when the score or `flag(9)` changes over a LOGIC 0 run.

### Menus

`menu.input` with `flag(14)` set opens the menu at the next cycle's input step. The chosen item's controller is seen in that cycle only. Menus remember their highlighted item. Menu text is drawn inverted, the highlighted entry normally, and disabled items as the inverted glyph with a checkerboard of pixels turned white. [interpreter/command-semantics](andromeda-wiki/interpreter/command-semantics.md) §"Menus" has the keys and geometry.

### `status`

`status` lists carried items two to a row in text mode. With `flag(13)` set the player can select: Enter sets `var(25)` to the item and Esc sets 255.

## Stage 9: sound

A SOUND is four voice offsets, then 5-byte notes per voice:

- A 16-bit duration in 60 Hz ticks, with `FF FF` ending the voice.
- Two bytes carrying a 10-bit tone divisor: the top 6 bits in the first (mask off bit 6), the low 4 in the second.
- An attenuation byte, whose low nibble is the attenuation.

**Starting.** `sound(n, f)` stops any playing sound, which sets that sound's flag, then clears `flag(f)`.

**Each tick** steps every active voice. A note's duration counts down, and the next note loads at zero. The first note loads on the first tick.

**Envelope.** On voices 1–3, each note runs a 67-step attenuation table, one step per tick:

1. Add the table value to the note's attenuation and clamp to 0–15.
2. Add `var(23)` and cap at 15.
3. On a Tandy only, add 2 more if the result is below 8.

The table itself is in [entities/sound](andromeda-wiki/entities/sound.md) §"Attenuation envelope". When it runs out, the note keeps its last step-1 value, and `var(23)` no longer applies.

**Finishing.** The sound ends when its voices run out, or at once if `flag(9)`, sound on, is clear. Ending sets its flag.

**Output by machine:**

| Machine | Output | Frequency |
|---|---|---|
| PCjr, Tandy | All four voices on the SN76496 | 111,860 Hz / divisor |
| PC, type 8 | Voice 1 on the speaker | The PIT is set to 12 × divisor, so about 99,432 Hz / divisor |

The speaker has no volume, so only attenuation 15 silences it. One quirk was confirmed at runtime: when the envelope ends on a note of base attenuation 2 or more, the speaker turns off for the rest of the note. SQ1 has no note long enough to show it.

## Stage 10: save, restore and restart

### The save file

The file name is the game ID, `sg.`, and a slot number from 1 to 12, so SQ1's first slot is `sqsg.1`. The file is a 31-byte description, then five blocks, each with a 16-bit length word in front:

| Block | Holds | SQ1 size |
|---|---|---|
| 1 | Fixed state from `DS:0002`: game ID, variables, flags, clock, horizon, block, control mode, script count, `set.key` table, strings, text and input settings | 1,505 |
| 2 | The object table | 774 |
| 3 | The decrypted OBJECT entries and names | 328 |
| 4 | The script buffer, at full capacity | 100 |
| 5 | Scan positions: a pseudo-entry, one entry per loaded LOGIC, then a terminator, 4 bytes each | 4 × (loaded LOGICs + 2) |

The game ID is at file offset 33, and the slot list uses it to reject other games' files. Matching this layout matters only if you want to read the original interpreter's saves.

### The script buffer and restore

Restore doesn't save the screen or resources. It replays the script buffer, the room's log of loads, picture draws, `add.to.pic` calls and discards. Recording turns on at each `new.room`, and the buffer is reset there.

The replay rebuilds everything the room did, in order, then reapplies scan positions to the LOGICs it reloaded. LOGIC 0 is never reloaded, so its scan start isn't restored from the file; it keeps whatever it had. The rerun of LOGIC 0 then sees `flag(12)` set.

If a room records more than the buffer holds, error `0x0B` repeats on every recorded command until the next `new.room`. `script.size` sets the buffer size, but 2.917 only allocates the buffer once. A larger second size overwrites memory after the buffer, so allocate the size the game asks for.

### Restart

`restart.game` asks to confirm unless `flag(16)` is set.

- **Resets:** variables, flags, objects and the OBJECT data, the heap and resource lists, the controllers, and the tick count. It also re-enables menu items.
- **Keeps:** strings, `set.key` bindings, the horizon, the screen and text settings, and `flag(9)`.

It then sets `flag(6)` and reruns LOGIC 0, which normally calls `new.room`. [interpreter/save-restore](andromeda-wiki/interpreter/save-restore.md) has the full lists.

## Stage 11: debugging aids

2.917's own debugger is a command trace. Scroll Lock or `trace.on` opens it, and only while `flag(10)` is set. It shows each command as `logic: number(args)`, with test results at the right, and waits for a key after each one. `trace.info` names a LOGIC whose messages give command names.

Everything else that looks like a debugger is game script. In SQ1, ALT-D sets `flag(190)` and loads LOGIC 99, which holds commands such as `tp` and `show priority`. A reimplementation needs nothing special for it.

## Quirks: reproduce or reject

**Reproduce.** A well-formed game can observe these:

| Behavior | Where |
|---|---|
| `end.of.loop`'s flag shared with `move.obj`'s target x | Stage 6 |
| Step time 0 skipping the motion pass and loop choice | Stage 6 |
| `get.priority` lagging `position` until the next check | Stage 6 |
| `add.to.pic` clearing `flag(0)`, `flag(1)` and `flag(3)` | Stage 6 |
| Control values surviving under drawn cels | Stage 6 |
| Fillers invisible to `said` | Stage 7 |
| `quit(0)` not asking with `flag(15)` or `var(21)` set | Stage 8 |
| The menu choice arriving in the next cycle only | Stage 8 |
| LOGIC 0's scan start surviving a restore unchanged | Stage 10 |
| The speaker turning off at the end of the envelope | Stage 9 |
| `var(10)` = 0 meaning no delay | Stage 5 |

**Reject as errors.** These only follow from invalid scripts or data, and 2.917 hangs, corrupts memory or crashes:

| Behavior | 2.917 does |
|---|---|
| `FC` or `FD` outside an `if` | Hangs |
| A fill with an unmasked color byte such as `0x1F` | Hangs |
| A screen with no legal position for an object | Hangs in the position fixer |
| `draw` or `erase` one past the object table | Writes into LOGIC 0's bytecode |
| `set.loop` equal to the loop count | Reads past the loop table, then raises error 8 |
| `add.to.pic` margin rectangle on a 1- or 2-pixel cel | Overruns the buffer |
| `script.size` larger the second time | Overwrites memory after the buffer |
| `shake.screen(0)` | Loops 65,536 times |
| Divide by zero | Leaves it to DOS |
| A message number past the count | Shows garbage |
| A fill deep enough to exhaust the 2,560-byte stack | "Stack blown." and exit |
| `trace.on` while the trace is on | Skips the next byte |

## Using the harness as an oracle

`tools/agi_emu/` boots the real interpreter on the game's files. `session.boot()` takes replacement LOGIC bytecode (built with `logic.py`), PICTURE and VIEW payloads (`resources.py`), and SOUND payloads, and appends them to `VOL.0`. A scenario then runs some ticks and reads the result:

- The screen buffer (`m.screen()`), variables and flags (`m.var`, `m.flag`), and object fields.
- Decoded display memory, for each adapter.
- Port writes with their tick, for sound and display registers.
- Text the interpreter printed, with its row and column.

To check a stage of your own interpreter, give both the same input and compare. A synthetic LOGIC 0 should enter a room on its first cycle, as `scenarios.once()` does. Sample the buffer at the start of a LOGIC 0 run with `at_cycle()`, not mid-update. The README lists what the harness can't show.

## Not covered

- AGI v3 (compressed resources, combined directory). The wiki keeps its v3 pages, marked unaudited.
- Interpreter versions other than 2.917, beyond the argument-count changes in [interpreter/command-evolution](andromeda-wiki/interpreter/command-evolution.md).
- The analog look of each display, such as composite CGA color.
- Disk swapping and DOS error handling, which a reimplementation can treat as fatal.
