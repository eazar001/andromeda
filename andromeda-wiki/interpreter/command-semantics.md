# Command Semantics

Behavioral semantics for LOGIC opcodes, audited against AGI 2.917 and first drawn from [4-4-Logic.html] (an AGDS-manual chapter translated from Russian by Vassili Bykov, with translator's notes from Bykov and clarifying replies from Lance Ewing). This page surfaces high-value items — edge-case behavior, multi-step procedures, runtime constraints, and mnemonic / argument-count conflicts with [[interpreter/commands]]. The chapter itself documents prose behavior for every opcode; for the full text refer directly to `AGI_Specifications/Specifications/4-4-Logic.html`.

Companion pages:

- [[interpreter/commands]] — opcode dispatch table (signatures, argument types). Source: 4-3.
- [[entities/logic]] — bytecode container format. Source: 4-1.
- [[interpreter/priority-bands]] — y → priority auto-assignment table (`release.priority`).

## Page-level caveats

- There is no LOGIC decoder in `resource/`, so nothing here is checked against project code. Claims cited to `[AGI 2.917 …]` are read from that binary, and nothing here has been run.
- 4-4 is an AGDS manual chapter. AGDS surface syntax (`if_`, `else_`, `not_`, `or_` — keywords with trailing underscores) differs from the AGI Studio syntax in [[sources/4-2-logic]] (`if () { }`, `else { }`, `&&`, `||`, `!`). Both compile to the same `$FC..$FF` bytecode control-flow opcodes; the underscore-suffixed mnemonics are AGDS authoring conventions, not bytecode-level distinctions.

## Arithmetic edge cases

The chapter flags four behaviors as unspecified, marked with translator's-note brackets [VB] (Vassili Bykov) [4-4-Logic.html §ARITHMETIC COMMANDS]. AGI 2.917 settles them [AGI 2.917 1000:728E–1000:73BC]:

1. **`addn` / `addv` overflow** — wraps at 8 bits, so 250 + 10 = 4.
2. **`subn` / `subv` underflow** — wraps at 8 bits, so 1 - 2 = 255.
3. **`mul.n` / `mul.v` overflow** — keeps the low 8 bits of the product.
4. **`div.n` / `div.v` by zero** — the interpreter neither checks for it nor installs a handler for the CPU's divide error, so control passes to DOS [AGI 2.917 1000:7395, 1000:8369]. The result depends on DOS's own divide-error handler, which the runtime harness doesn't model, so it stays open. The interpreter does hook `int 23h` to a bare `IRET` [AGI 2.917 1000:836D, 1000:84F3], which matters if that handler goes through Ctrl-C handling. A reimplementation should treat it as a fatal error. Division is unsigned and keeps the quotient.

`increment` and `decrement` saturate at 255 and 0 [4-4-Logic.html §ARITHMETIC COMMANDS; AGI 2.917 1000:728E, 1000:72A1], so `addn(var, 1)` is not the same as `increment(var)` at the boundary.

The indirect commands read as follows, with no bounds checks since every index is one byte [AGI 2.917 1000:7314, 1000:732D, 1000:733E]:

- `lindirectv(a, b)`: `var(var(a)) = var(b)`
- `lindirectn(a, n)`: `var(var(a)) = n`
- `rindirect(a, b)`: `var(a) = var(var(b))`

## Tests

All comparisons are unsigned 8-bit [AGI 2.917 1000:0823–1000:089A]. `lessn` and `lessv` are strict, as are `greatern` and `greaterv`.

**Flags.** Flag `n` is the bit `0x80 >> (n & 7)` of the byte at `DS:0109 + n / 8`, so the highest bit of each byte comes first [AGI 2.917 1000:744A]. This matters only for anything that reads the flag bytes as a block, such as a saved game.

**Position tests.** `posn`, `obj.in.box`, `center.posn` and `right.posn` all take `(obj, x1, y1, x2, y2)` and test inclusively against the object's baseline `y`. They differ in which x values must be in range [AGI 2.917 1000:08C6–1000:0917]:

| Test | `x >= x1` applies to | `x <= x2` applies to |
|---|---|---|
| `posn` | left edge | left edge |
| `obj.in.box` | left edge | right edge (`x + width - 1`) |
| `center.posn` | center (`x + width / 2`, rounded down) | center |
| `right.posn` | right edge | right edge |

**`has` and `obj.in.room`.** `has(i)` is true when item `i`'s room byte is 255. `obj.in.room(i, v)` is true when it equals `var(v)` [AGI 2.917 1000:08AD, 1000:093B].

**`controller`.** Reads entry `n` of the 50-entry controller table, with no bounds check [AGI 2.917 1000:0931]. See [[interpreter/event-loop]].

**`have.key`.** True at once if `var(19)` is non-zero. Otherwise it empties the event queue until it finds a key, stores that key in `var(19)` and returns true, or returns false once the queue is empty. It doesn't wait, and it discards any direction or controller events it passes [AGI 2.917 1000:09BE, 1000:459E]. Joystick button codes become Enter or Esc on this path [AGI 2.917 1000:4634].

**`compare.strings`.** More forgiving than the spec's "string(s1) = string(s2)" [4-4-Logic.html §TEST COMMANDS]. Both strings are lowercased and stripped of space, tab, and the characters `. , ; : ' ! -` before comparing, so "Hello, World" equals "helloworld" [AGI 2.917 1000:0EAC, 1000:0EF8, DS:0943].

## Resource loading and unloading

### Auto-discard rule

[4-4-Logic.html §COMMANDS TO LOAD AND UNLOAD RESOURCES]:

> "Remember that when a resource is unloaded, all resources loaded after it ARE ALSO AUTOMATICALLY UNLOADED!"

Load order does decide what is reclaimed, because the heap only grows and shrinks at its top. In 2.917 the rule holds fully for memory but only partly for bookkeeping: a discard reclaims all later memory, yet cuts only its own type's list, so resources of other types can stay listed with stale pointers. See the callout in [[interpreter/memory-layout]] §"Releasing memory" [AGI 2.917 1000:3F0D, 1000:4BCE]. Confirmed at runtime there.

### Load and discard handlers

Read from AGI 2.917. Heap details are in [[interpreter/memory-layout]].

- **`load.pic`, `load.view`, `load.view.v`.** If the resource is already loaded, nothing happens and no script entry is written. Otherwise object save areas are released, a script entry is written, a 5-byte record and the data are allocated, and the save areas are rebuilt [AGI 2.917 1000:4A3B, 1000:39F7]. A missing directory entry or too little memory ends the game [AGI 2.917 1000:4441, 1000:13ED]. After reading a view, some machine types call a further driver routine, which is unread [AGI 2.917 1000:5857].
- **`discard.pic`, `discard.view`, `discard.view.v`.** An unloaded resource raises error `0x15` for a picture or `1` for a view, which returns to the main loop. Otherwise a script entry is written, the type's list is cut at the record, and the heap's next-free offset moves back to the record [AGI 2.917 1000:4BCE, 1000:3F0D].
- **`show.mem`** shows a `print` window with five values, labeled by the interpreter's own string: `heapsize` (top − base), `now` (next-free − base), `max` (highest next-free − base), `rm.0, etc.` (resident mark − base), and `max script` (most script entries used). The first four are bytes [AGI 2.917 1000:14BD, DS:0A11].
- **`script.size(n)`** sets the script buffer's size to `n` entries of 2 bytes each and empties the log. Its byte argument limits `n` to 255 [AGI 2.917 1000:70A3, 1000:6FB5].

> [!conflict] Spec silent vs. AGI 2.917: resizing the script buffer
> 4-4 presents `script.size` as setting the buffer's size. In 2.917 the buffer is allocated only once, by the first `script.size` or `new.room`, with a default of 50 entries. A later call changes the limit but not the buffer, so a larger size lets entries overflow into the heap above it. Any call also discards the current room's log. `script.size(0)` makes the next recorded command raise error `0x0B` [AGI 2.917 1000:6FC1, 1000:7004]. **Confirmed at runtime:** after `script.size(10)` before any room, then `script.size(100)` and 23 recorded loads, the entries ran past the 20-byte buffer and overwrote the VIEW records above it, leaving the view list reading `1, 255, 0, 14, …` where views 2 to 13 had been. `script.size(0)` then one load gave `var(17)` = `0x0B` [2.917 runtime: script_size_resize_and_zero]. SQ1 doesn't use this command [SQ1 data check, memory unit, log 2026-11-01].

### Missing command variants

4-4 includes Bykov / Ewing exchanges confirming the AGI command set has asymmetric coverage [4-4-Logic.html §COMMANDS TO LOAD AND UNLOAD RESOURCES]:

| Operation | Literal form | Variable form | Note |
|---|---|---|---|
| Load LOGIC | `$14 load.logics` | `$15 load.logics.v` | Symmetric. |
| Load PICTURE | — | `$18 load.pic` | **Asymmetric.** `load.pic(n)` takes an argument that the chapter describes as "Var(n)" — i.e. the literal-form name is in use but the semantics are the indirect form. Lance Ewing confirms: "load_pic_v may be a more appropriate name for it, but the name above is what they gave it. There is no equivalent command that takes a number rather than a variable." |
| Load VIEW | `$1E load.view` | `$1F load.view.v` | Symmetric. |
| Load SOUND | `$62 load.sound` | — | **No `load.sound.v`.** Lance Ewing confirms: "There really is no way of loading a sound with indirection. The command doesn't exist." |
| Discard PICTURE | — | `$1B discard.pic` | Same asymmetry as `load.pic` — takes an argument that the chapter describes as indirect. |
| Discard VIEW | `$20 discard.view` | `$99 discard.view.v` | Symmetric. |
| Discard LOGIC | — | — | **No discard.logic.** Lance Ewing: "There must be some other way that those commands are removed from memory, because the commands you mention above don't exist." In 2.917, LOGICs are released by `new.room`, the error routine, and the end of a temporary `call`. LOGIC 0 is never released [AGI 2.917 1000:10F7, 1000:12AE]. |
| Discard SOUND | — | — | **No discard.sound.** In 2.917, sounds are released by `new.room` and the error routine [AGI 2.917 1000:4FF5, 1000:10D0]. |

### PICTURE composition ordering

[4-4-Logic.html §PICTURE RESOURCE MANAGEMENT COMMANDS]:

> "Please use the following sequence of commands when loading PICTURE resources:
>  `load.pic(n); draw.pic(n); discard.pic(n); ...; show.pic;`
>  Any other order may crash the interpreter without any diagnostic messages."

The discard between `draw.pic` and `show.pic` works because `show.pic` doesn't use the resource [AGI 2.917 1000:4B82]. The spec calls any other order a crash hazard, but 2.917 enforces no order, and keeping a picture loaded is harmless in itself. The hazards found by reading are `draw.pic` on a picture that isn't loaded, which raises error `0x12` rather than crashing [AGI 2.917 1000:4AE8], and the stale records described in [[interpreter/memory-layout]], which do decode garbage at runtime there. No crash came from order alone.

### PICTURE commands

All four are read from 2.917, with the PICTURE routine they call also run in an emulator; see [[entities/picture]] for the bytecode and [[concepts/screen-layers]] for the buffer. None of them touches the display except as stated.

**`$19 draw.pic(var)`** [AGI 2.917 1000:4AAA, 1000:4ACF]. The argument is a variable holding the picture number. In order:

1. Records the number at `DS:013B`. It lies in the block a save writes, and no reader was found.
2. Finds the picture in the loaded list. If absent, raises error `0x12` with the picture number, so `var(17)` is `0x12` and `var(18)` the number.
3. Adds event 4 with the number to the script log, unless `flag(7)` is set [AGI 2.917 1000:6FEA].
4. Takes the screen objects out of the buffer, fills the buffer with color 15 and priority 4, runs the bytecode, and puts the objects back [AGI 2.917 1000:698D, 1000:637E, 1000:69C7].
5. Clears `DS:120E`, which stops object updates reaching the display until `show.pic` [AGI 2.917 1000:56A2].

So the old picture stays on screen until `show.pic`.

**`$1C overlay.pic(var)`** [AGI 2.917 1000:4B17, 1000:4B3B]. The same as `draw.pic`, with these differences: it doesn't fill the buffer first, so new drawing lands on the existing contents; it logs event 8; it doesn't write `DS:013B`; and before clearing `DS:120E` it sends the objects' rectangles to the display, if `DS:120E` was set [AGI 2.917 1000:6379, 1000:69E4]. As with `draw.pic`, all PICTURE state starts fresh, with both layers disabled, so the overlay must set its own colors.

**`$1A show.pic`** [AGI 2.917 1000:4B82]. Clears `flag(15)`, closes any open window, sends the whole buffer to the display, and sets `DS:120E`. It has no argument and doesn't check that a picture was drawn.

**`$1D show.pri.screen`** [AGI 2.917 1000:7254].

- It sets a flag so the full update swaps each byte's two nibbles, then sends the buffer to the display. The priority values now appear as colors. Objects in the buffer appear too.
- It discards queued input, then waits for **Enter or Esc** only; other keys are ignored [AGI 2.917 1000:4618, 1000:45F0].
- It repeats the swap and update, which restores both the buffer and the screen, and clears the flag [AGI 2.917 1000:5486–1000:54BE].

The game cycle doesn't run while it waits.

## `new.room` — the eleven-step room transition

[4-4-Logic.html §PROGRAM CONTROL COMMANDS] documents `new.room(n)` and `new.room.v(n)` as the most powerful interpreter command. Each call performs an ordered sequence:

1. Issue `stop_update` and `unanimate` to all objects.
2. Discard all resources except Logic(0).
3. Issue `player_control`.
4. Issue `unblock`.
5. Issue `set_horizon 36`.
6. Var(1) ← Var(0); Var(0) ← n (or Var(n) for `new.room.v`); Var(4) ← 0; Var(5) ← 0; Var(16) ← VIEW resource ID associated with EGO.
7. Load Logic(Var(0)) and execute.
8. Reposition EGO based on Var(2) (border-touch code from the previous room): bottom edge → place on horizon; top edge → place at bottom; right edge → place at left, and vice versa.
9. Var(2) ← 0.
10. Flag(5) ← 1 (signals the first cycle of the new room; reset by the interpreter at the end of that cycle).
11. Clear keyboard input buffer and return to the main interpreter loop.

The reserved variables Var(0), Var(1), Var(2), Var(4), Var(5), Var(16) and Flag(5) — all documented in [[interpreter/variables-and-flags]] — are coordinated state at step 6 / step 10. Flag(5) is the signal LOGIC scripts use to detect they are running in a freshly-entered room and should perform first-cycle initialization (the chapter emphasizes this in all-caps: "THIS IS VERY IMPORTANT!"). The spec cross-references the "Thunderstorm" educational program for a concrete example.

> [!conflict] 4-4 procedure vs. AGI 2.917
> Read from the `new.room` core [AGI 2.917 1000:1792]. `new.room.v` differs only in reading the room number through a variable [AGI 2.917 1000:1773].
>
> - **Confirmed:** resets every object's state, discards resources, player control, unblock, horizon 36, `var(1)` ← `var(0)`, `var(0)` ← n, clears `var(4)` and `var(5)`, loads the new LOGIC, repositions EGO from `var(2)`, clears `var(2)`, sets `flag(5)`, clears queued input.
> - **Contradicted, step 6:** `var(16)` comes from EGO's object entry (offset 7), the view it has now. It is not looked up from a file.
> - **Contradicted, step 7:** the core only loads the LOGIC. It does not execute it. It returns 0, and the main loop reruns LOGIC 0, which then calls the room's LOGIC as usual.
> - **Refined, step 8:** the positions are fixed values [AGI 2.917 1000:1843]. `var(2)` = 1 (top) sets y to 167; 2 (right) sets x to 0; 3 (bottom) sets y to 37; 4 (left) sets x to 160 minus EGO's width. "On the horizon" is therefore only true of the default horizon, and the other axis is unchanged.
> - **Refined, step 11:** queued input is cleared first, not last. The core also clears the controller table and redraws the status line and input line. `var(9)` and `flag(2)` are cleared by the main loop, not here.
> - **Not in 4-4:** a playing sound stops first, which sets its completion flag [AGI 2.917 1000:516C]. The script buffer is reset [AGI 2.917 1000:6FB5]. Cached file handles close [AGI 2.917 1000:30D6]. The new room is recorded in the script buffer [AGI 2.917 1000:117D].
>
> The actual order is: stop sound; release heap memory and clear queued input; reset the script buffer; reset all objects; clear the resource lists; set the control state and horizon; update the variables; close files; load the LOGIC; reposition EGO; set `flag(5)`; clear controllers; redraw. The error routine runs a similar cleanup [AGI 2.917 1000:3FE8].

## `release.loop` — direction → loop auto-selection

When `release.loop(n)` is in effect on object `n`, the loop index is set automatically from the object's direction (Var assigned by `set.dir` or motion commands). Direction encoding [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS, with the chapter's compass diagram]:

```
       1
   8   |   2          0 = stationary
     \ | /
   7---+---3
     / | \
   6   |   4
       5
```

Two tables apply, depending on the VIEW's loop count [4-4-Logic.html]:

| Direction | 0 still | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| VIEW with **2 or 3 loops** | * | * | 0 | 0 | 0 | * | 1 | 1 | 1 |
| VIEW with **exactly 4 loops** | * | 3 | 0 | 0 | 0 | 2 | 1 | 1 | 1 |

`*` means "current loop retained" — the auto-selector does not change loop for stationary objects (direction 0) or for directions that have no canonical loop mapping in the 2-/3-loop variant.

The two tables differ only for directions 1 and 5: 4 loops uses dedicated up (loop 3) and down (loop 2) animations; 2-/3-loop VIEWs retain whatever loop is currently displayed.

> [!conflict] 4-4 vs. AGI 2.917, loop counts
> 4-4 headlines its second table "for objects with more than 4 loops", and an earlier version of this page said "4+". In 2.917 the second table applies to **exactly 4** loops. With 5 or more, or with 1, no automatic choice happens [AGI 2.917 1000:059A, DS:08D5, DS:08DF]. The table values themselves are confirmed. SQ1 has no VIEW with more than 4 loops (180 with 1, 27 with 2, 8 with 3, 23 with 4), so its data can't separate the readings [SQ1 data check, log 2026-11-01].

**When the choice runs.** The screen pass makes it for an active object without a fixed loop, and only when the object's step countdown is 1 [AGI 2.917 1000:0593, 1000:05C7]. So with a longer step time, the loop only changes on cycles when a step is due. It never changes with a step time of 0. `release.loop` itself computes nothing. See [[interpreter/view-objects]] §"What happens each cycle".

## Base-point semantics

> [!conflict]
> **The chapter contradicts itself on cel base-point location.** [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS] line 363 (`get.posn`) states: "Coordinates of the object are coordinates of the base point (bottom **left** corner) of cels of the VIEW resource". [4-4-Logic.html §OTHER COMMANDS] line 854 (`upper.left`) states: "Usually the crossing by an object of various areas and lines is tracked by the base point (bottom **right** corner) of its cel." Same chapter, same author, opposite descriptions. The `upper.left` command's name and its description ("After this command, top left corner is used as such a point") imply the default is some *bottom* corner, but the chapter is internally inconsistent about which one.
>
> **Resolved for 2.917: bottom left.** The object's `x` is the cel's left column and its `y` is the bottom row, and the control check scans the baseline rightward from `x` [AGI 2.917 1000:8FF7, 1000:55F0].

## Objects

Behavior of opcodes `$21`..`$5B`, `$83`, `$84`, `$93` and `$94` in 2.917, read from each handler. Table offsets and flag bits are in [[interpreter/view-objects]]. Most handlers do **no bounds check** on the object number, so an out-of-range number writes past the table. Exceptions are below. Errors go through the error routine, with the code in `var(17)` [AGI 2.917 1000:3FE8].

### Setting up

- **`animate.obj`**: error `0x0D` if the number is out of range. See [[interpreter/view-objects]] §"Lifecycle" [AGI 2.917 1000:04F5].
- **`unanimate.all`**: erases both draw lists, then clears the animated and drawn bits on every object. It adds nothing about motion or position [AGI 2.917 1000:053D].
- **`draw`**: error `0x13` if out of range, error `0x14` if no view is set. It does nothing if already drawn. Otherwise it sets the updating bit, runs the position fixer, takes the current cel and position as "previous", adds the object to the screen and clears the skip-cel bit [AGI 2.917 1000:0A06]. This makes `draw` imply `start.update`.
- **`erase`**: error `0x0C` if out of range. It does nothing if not drawn. It clears only the drawn bit, so the object stays animated [AGI 2.917 1000:0AAB].

> [!conflict] Bound checks that let one extra number through
> `draw` and `erase` accept an object number equal to the slot count, because they compare with "end of table >= entry", unlike `animate.obj`'s strict check [AGI 2.917 1000:0A21, 1000:0AC9, 1000:0510]. The entry they then use lies past the table. **Confirmed at runtime:** in 2.917's heap order, the bytes after the table are LOGIC 0's list record and bytecode. With 18 slots, `draw(18)` did nothing, because the byte at the flags offset happened to have the drawn bit set. `erase(18)` cleared that bit and copied the cel pointer into the previous-cel field, which rewrote two commands of LOGIC 0's own bytecode, after which LOGIC 0 no longer counted cycles. `animate.obj(18)` raised error `0x0D` as expected [2.917 runtime: draw_and_erase_one_past_table].

### Position

- **`position`**, **`position.v`**: write `x` and `y` and the previous-position fields. No checks, no flags, no fixer. They don't touch the screen until the next update [AGI 2.917 1000:7B53, 1000:7B90].
- **`get.posn`**: stores the low byte of each coordinate [AGI 2.917 1000:7BDD].
- **`reposition`**: adds two variables, each read as a **signed** byte, so 128–255 are negative. A negative delta larger than the coordinate gives 0, and it doesn't wrap. It then sets the repositioned bit and runs the position fixer [AGI 2.917 1000:7C20]. 4-4 gives only "x + Var(dx)", with no mention of the sign.
- **`reposition.to`**, **`reposition.to.v`**: set `x` and `y`, set the repositioned bit, run the fixer. They leave the previous-position fields alone [AGI 2.917 1000:7CB0, 1000:7CF3].

### View, loop, cel

- **`set.view`**, **`set.view.v`**: error 3 if the VIEW isn't loaded. They store the view number, pointer and loop count, then keep the current loop if it's below the new count and otherwise use loop 0 [AGI 2.917 1000:3AE7].
- **`set.loop`**, **`set.loop.v`**: error 6 if no view is set, error 5 if out of range. The current cel is kept if below the new loop's cel count and otherwise becomes 0. Then the position correction for a changed cel applies [AGI 2.917 1000:3BB7, 1000:3C1B].
- **`set.cel`**, **`set.cel.v`**: error `0x0A` if no view is set, error 8 if the cel isn't below the count. The position correction applies, and the skip-cel bit clears [AGI 2.917 1000:3C55, 1000:3CCB].
- **`last.cel`**: reads the count byte from the loop data and subtracts 1. With no view set, it reads from address 0 [AGI 2.917 1000:3D9F]. **`current.cel`**, **`current.loop`**, **`current.view`**, **`number.of.loops`**: read the table fields [AGI 2.917 1000:3DED–1000:3E95].
- **`fix.loop`**, **`release.loop`**: set and clear bit 13 only [AGI 2.917 1000:497B, 1000:49A3].

> [!conflict] `set.loop` bound
> The check rejects a loop only if it's **greater than** the count, so a loop equal to the count passes, unlike the cel check, which is strict [AGI 2.917 1000:3BEF, 1000:3D03]. That loop reads its offset from past the VIEW's loop table. This isn't hypothetical: LOGIC 71 has `set.view(11, 89)` directly followed by `set.loop(11, 3)`, and VIEW 89 has 3 loops. There, the offset read is 4873, past the end of the 1,529-byte resource [SQ1 data check, log 2026-11-01]. The scan is linear, so reaching that code isn't shown. **Confirmed at runtime:** `set.view(1, 89)` then `set.loop(1, 3)` stored loop 3, read a cel count of 0 from the heap after the view, and the next cel operation raised error 8 with `var(18)` = 1. The game ran on [2.917 runtime: set_loop_equal_to_count].

### Priority and updates

- **`set.priority`**, **`set.priority.v`**: set the fixed bit and the value [AGI 2.917 1000:79B9, 1000:7A41]. **`release.priority`**: clears the bit only. **`get.priority`**: reads the stored value, which may be stale. See [[interpreter/view-objects]] §"Priority".
- **`stop.update`**, **`start.update`**: if the bit would change, erase both lists, change it, and redraw both lists [AGI 2.917 1000:6A7D, 1000:6A9B]. A stopped object doesn't cycle or move, which 4-4 doesn't mention.
- **`force.update`**: 4-4 says object n is redrawn. In 2.917 the argument is skipped and ignored: **all** objects are erased, redrawn and copied to the screen [AGI 2.917 1000:6A51, 1000:69E4].

### Limits on movement

- **`set.horizon`**: stores the value in the word at `DS:012D` and moves nothing [AGI 2.917 1000:7DB5].
- **`ignore.horizon`**, **`observe.horizon`**, **`ignore.blocks`**, **`observe.blocks`**, **`ignore.objs`**, **`observe.objs`**: set or clear one flag bit each.
- **`object.on.water`**, **`object.on.land`**: each sets its own bit, without clearing the other. **`object.on.anything`** clears both [AGI 2.917 1000:7D46, 1000:7D6B, 1000:7D90]. On EGO, both bits clear after each screen pass.

> [!conflict] 4-4 vs. AGI 2.917, `object.on.land`
> 4-4 says an object on land "is not allowed to touch pixels of water surface". In 2.917 it's refused only when its **entire** baseline is water, so partial contact is allowed. `object.on.water` matches 4-4: the whole baseline must be water [AGI 2.917 1000:564C–1000:5660].

- **`block`**: stores four bytes as words at `DS:0131`–`DS:0137` and marks the box active at `DS:013D`. **`unblock`** clears the mark only [AGI 2.917 1000:7A87, 1000:7AC3]. See [[interpreter/view-objects]] §"The block box".

### `distance`

If either object isn't drawn, the variable gets 255. Otherwise it gets `|y1 - y2|` plus the difference of the x **centers** (`x + width / 2`), capped at 254 [AGI 2.917 1000:47EF].

> [!conflict] 4-4 vs. AGI 2.917, `distance`
> 4-4 gives `ABS(x(n) - x(m)) + ABS(y(n) - y(m))`, using plain `x`, with no cap. 2.917 uses centers. Objects of equal width get the same result either way, except for the cap. "On the screen" means the drawn bit, so an object can be off-list and still count.

### Cycling

- **`start.cycling`**, **`stop.cycling`**: set and clear the cycling bit [AGI 2.917 1000:6BF5, 1000:6BD0].
- **`normal.cycle`**, **`reverse.cycle`**: set the type and the cycling bit [AGI 2.917 1000:6ABB, 1000:6B24].
- **`end.of.loop`**, **`reverse.loop`**: set the type, the cycling, updating and skip-cel bits, store the flag and clear that flag now [AGI 2.917 1000:6AE7, 1000:6B50]. Because of the skip bit, the first cycle-countdown expiry changes nothing. The flag slot is shared; see [[interpreter/view-objects]] §"Shared parameters". 4-4 doesn't mention that finishing also stops motion by clearing the direction.
- **`cycle.time`**: copies a variable to both cycle bytes, restarting the countdown. A value of 0 stops cycling [AGI 2.917 1000:6B8D, 1000:05EF].

### Motion

- **`stop.motion`**: direction 0 and motion 0. On EGO, also `var(6)` 0 and program control [AGI 2.917 1000:6E01].
- **`start.motion`**: motion 0. On EGO, also `var(6)` 0 and player control. It doesn't restore a direction, so a stopped non-EGO object stays stopped until `set.dir` [AGI 2.917 1000:6E3E]. That refines 4-4's "motion is started".
- **`step.size`**: variable to offset `1E`. **`step.time`**: variable to both step bytes [AGI 2.917 1000:6E77, 1000:6EB5]. 4-4 says `Var(n)` in both, a slip: the variable is the second argument, and the first is the object.
- **`move.obj`**, **`move.obj.v`**: store motion 3, target and flag. They save the step size, and replace it with the argument unless that's 0 [AGI 2.917 1000:6C1D, 1000:6C9A]. They set the updating bit and clear the flag. On EGO they set program control. The direction is computed at once, so a target already in range finishes before the command returns [AGI 2.917 1000:1672]. Touching a border also finishes it. Finishing returns EGO to player control.
- **`follow.ego`**: motion 2. The second argument is a **stop distance**, not a step. The stored value is the larger of it and the step size [AGI 2.917 1000:6D3B]. It clears the flag and sets the updating bit. It doesn't change program or player control.
- **`wander`**: motion 1, updating bit. On EGO, program control [AGI 2.917 1000:6DA1].
- **`normal.motion`**: motion 0 only, so the direction stays, as 4-4 says [AGI 2.917 1000:6DDA].
- **`set.dir`**, **`get.dir`**: variable to and from offset `21` [AGI 2.917 1000:6EF7, 1000:6F35]. `var(6)` isn't touched, but on EGO the main loop overwrites the direction from `var(6)` after LOGIC 0. So `set.dir(0, ...)` has no lasting effect [AGI 2.917 1000:01EA].
- **`program.control`**: sets `DS:0139` to 0. **`player.control`**: sets it to 1 and EGO's motion to 0 [AGI 2.917 1000:6F68, 1000:6F7A]. EGO's direction and `var(6)` aren't cleared.

> [!conflict] 4-4 vs. AGI 2.917, `follow.ego`
> 4-4 says the object chases EGO "by s pixels every step", and sets the flag when "EGO's and the object's coordinates become equal". In 2.917 `s` is the stop distance, the step size is unchanged, and the flag sets when both axis differences are under that distance. The comparison uses x centers and `y` [AGI 2.917 1000:0B36, 1000:16ED]. SQ1 uses `s` = 10 in 15 of 17 literal calls, which fits a distance better than a speed [SQ1 data check, log 2026-11-01].

## `set.upper.left` argument-count conflict

> [!conflict]
> **4-3 and 4-4 disagree on `$9B`'s arity.** [4-3-Logic.html §Action commands] lists opcode `$9B set.upper.left` with **2 arguments** (both `???` type). [4-4-Logic.html §OTHER COMMANDS] calls the command `upper.left` (no `set.` prefix) and describes it as a **0-arg state toggle** that switches the collision-detection base-point reference. The descriptions cannot both be right.
>
> **Resolved for 2.917: 4-3's count is right, and 4-4's behavior does not exist there.** The table gives 2 arguments, and the handler does nothing except skip those 2 bytes [AGI 2.917 DS:061D entry $9B; 1000:4C15]. There is no base-point toggle in this version. An earlier provisional reading on this page favored 4-4 and was wrong. Other versions are unchecked.

## Mnemonic variants across chapters

4-4's prose uses slightly different opcode mnemonics than 4-3's table. None of these are bytecode-level distinctions — both chapters describe the same opcode bytes — but a future decoder must pick one form:

| Opcode | 4-3 mnemonic | 4-4 mnemonic |
|---|---|---|
| `$03` | `assignn` | `assign` |
| `$14` | `load.logics` | `load.logic` |
| `$15` | `load.logics.v` | `load.logic.v` |
| `$12` | `right.posn` | `right.position` (test command) |
| `$11` | `center.posn` | `center.position` (test command) |
| `$9B` | `set.upper.left` | `upper.left` |

The wiki uses the **4-3 forms** as canonical (they match AGI Studio and ScummVM conventions). 4-4's variants are recorded here for cross-reference.

## `add.to.pic` — VIEW-to-PICTURE composition

[4-4-Logic.html §PICTURE RESOURCE MANAGEMENT COMMANDS]. `$7A add.to.pic` and `$7B add.to.pic.v` composite a VIEW cel onto the background PICTURE buffer. Parameters (per the literal form):

| Pos | Param | Meaning |
|---|---|---|
| a | `num` | VIEW resource number |
| b | `num` | loop index within the VIEW |
| c | `num` | cel index within the loop |
| d | `num` | x coordinate on the PICTURE |
| e | `num` | y coordinate on the PICTURE |
| f | `num` | priority value |
| g | `num` | margin (see below) |

The variable-form `add.to.pic.v` takes 7 `var` arguments (verified against [4-3-Logic.html]). **Confirmed** for 2.917, with this argument order [AGI 2.917 1000:2C7A, 1000:2CCA].

**Margin rule** [4-4-Logic.html line 509]: "If margin is 0, 1, 2, or 3, the base of the cel is surrounded with a rectangle of the corresponding priority. If margin > 4, this extra margin is not shown."

**Resolved:** a margin of 4 draws no rectangle, the same as any larger value. The priority and margin are packed into one byte, with the margin in the high nibble, and the rectangle is drawn only if that byte is `0x3F` or less [AGI 2.917 1000:2CB7–1000:2CBD, 1000:5732]. SQ1 uses margin 4 in 29 of its 46 literal `add.to.pic` calls, along with 0 (11 calls), 1 (3), 12 (1) and 15 (2) [SQ1 data check, audit draw].

The packing has two side effects. Only the low 4 bits of the margin survive, so a margin of 16 acts like 0. A priority argument above 15 ORs its high bits into the margin.

### What it does in 2.917

1. Unless `flag(7)` is set or recording is off, it records the arguments in the script buffer as four 2-byte entries: code 5, then the values with priority and margin sharing a byte. This happens before anything is validated [AGI 2.917 1000:2D57–1000:2D94, 1000:6FEF].
2. It sets up a private object at `DS:0EAC`. The view must already be loaded, or error 3 is raised. The loop and cel checks are the same as for object commands [AGI 2.917 1000:3B08, 1000:2DA4–1000:2DC4].
3. It finds a place for the cel with the placement search, using priority 15, fixed priority, ignore horizon and ignore objects. So the only check that can move the cel is the screen bounds. It stays on screen by moving, and it can end up somewhere other than the requested position [AGI 2.917 1000:2DE6–1000:2DF5].
4. It restores the backgrounds of all objects, so the cel goes under them [AGI 2.917 1000:2E14].
5. It draws the cel into the buffer using the normal comparison, so existing higher-priority scenery hides it, and control lines survive [AGI 2.917 1000:5729].
6. It draws the margin rectangle, then redraws all objects and sends the cel's rectangle to the display [AGI 2.917 1000:2E21, 1000:2E28].

**Priority 0 means automatic.** A low nibble of 0 is replaced with the band for the final `y` [AGI 2.917 1000:5720–1000:5725]. SQ1 doesn't use this in its literal calls.

**The rectangle** is hollow and changes only the priority nibble, never the color [AGI 2.917 1000:5771–1000:57AB]. It has the cel's width. Its bottom is the cel's bottom row, and its height is the smaller of the cel's height and the number of rows from `y` upward that share `y`'s band [AGI 2.917 1000:573E–1000:5769].

Two quirks read from the code, both confirmed at runtime:

- With a rectangle height above 1, a cel 2 pixels wide makes the rectangle's top-row counter start at zero, so it wraps and writes the priority nibble across the whole 64K segment. A cel 1 pixel wide writes 255 bytes. No literal SQ1 call combines a margin below 4 with such a narrow cel [AGI 2.917 1000:579F–1000:57AB; SQ1 data check, audit draw]. At runtime, margin 0 with a 4-row cel at `y` 59: a 3-pixel cel drew a normal hollow rectangle, a 1-pixel cel wrote a 255-byte run along one row, and a 2-pixel cel set the priority of 26,237 of the buffer's 26,880 bytes to 0, the rest already being 0, turning the whole screen into a barrier. With a rectangle height of 1, at `y` 120, a 2-pixel cel was harmless [2.917 runtime: narrow_cel_margin_rectangle].
- The private object's number stays 0, because nothing writes `DS:0EAE`, and object 0 is EGO to the routines that set EGO's flags. So each call clears `flag(0)` and `flag(3)` in the baseline test and rewrites `flag(1)` when drawing. `show.obj` guards against this by using object number `0xFF`, and `add.to.pic` doesn't [AGI 2.917 1000:5663, 1000:9E2C, 1000:5EAA]. At runtime, with all three flags set beforehand, an `add.to.pic` left all three clear, on plain ground and over an all-cyan baseline alike, while a run without it kept them set [2.917 runtime: add_to_pic_rewrites_ego_flags].

PICTURE bytecode has no VIEW-composition opcodes ([[entities/picture]]), so `add.to.pic` is purely a LOGIC-side operation.

## `show.obj` — inventory close-up

`$81 show.obj` takes a view number, and `$A2 show.obj.v` takes it from a variable. Both then run the same routine [AGI 2.917 1000:5DD3, 1000:5DF7, 1000:5E13]. Recording to the script buffer is off throughout, so nothing it does is replayed [AGI 2.917 1000:5E1B, 1000:5F5C].

1. It loads the view if needed. If loading fails, it prints `Not now.` and does nothing else. It sets `DS:0F10` during the load, which makes a view too big for free memory fail instead of going to the allocator's error path. Other ways to fail weren't traced [AGI 2.917 1000:5E3A–1000:5E5D, 1000:2F8E, DS:1505].
2. It uses a private object on the stack, with object number `0xFF`, loop 0, cel 0 and fixed priority 15. The cel's bottom row is at `y = 167` and it's centered with `x = (159 - width) / 2` [AGI 2.917 1000:5E69–1000:5EAA].
3. If free memory exceeds the cel's save area plus 16 bytes, it saves the background, draws the cel and sends it to the display. Otherwise it skips the cel and still shows the text [AGI 2.917 1000:5ECC–1000:5F0E].
4. It prints the view's description in the normal message window and waits. There is no check for a missing description. See [[entities/view]] §"Description (optional)" [AGI 2.917 1000:5F1C–1000:5F25].
5. If it drew the cel, it restores the background and updates the display [AGI 2.917 1000:5F2B–1000:5F47].
6. If it loaded the view itself, it discards it again. A view that was already loaded stays [AGI 2.917 1000:5E23–1000:5E37, 1000:5F4D–1000:5F56].

It doesn't touch the object table, or erase or redraw animated objects. The cel simply goes over them, at priority 15.

## `set.game.id` — interpreter identification

[4-4-Logic.html §INITIALIZATION COMMANDS]: `set.game.id(n)` reads message `n` and compares it with the interpreter binary's internal identifier. On mismatch the interpreter exits. **Confirmed** for 2.917: it copies up to 6 characters to `DS:0002`, compares them with the terminator against a value in the code, case-sensitively, and exits on the first difference [AGI 2.917 1000:0E7E, 1000:5A81, 1000:02AE]. In the SQ1 binary that value is `SQ`, at `1000:5AA4`. The chapter notes "For AGDS interpreter the identifier is 'TQ'" — i.e. the *AGDS* fork carries its own identifier distinct from Sierra's. A reimplementation that runs many games shouldn't enforce a single value.

The runtime / loader-side counterpart is covered in [[sources/2-5-interpreter]] (the chapter on interpreter-binary loading and game IDs). 4-4 supplies only the LOGIC-side call form.

## Text output and strings

Everything here comes from AGI 2.917 [AGI 2.917 1000:0C44–1000:0E7D, 1000:1C06–1000:2315, 1000:7603–1000:7884]. Rows and columns are text cells on a 40x25 grid, and the first coordinate is always the row, whatever the spec calls it.

### Formatting a message

`print`, `display`, `get.string`, `get.num` and the input line's prompt all pass text through one formatter [AGI 2.917 1000:1F54, 1000:1F93]. It copies text to a buffer, expands codes, and wraps to a given width.

| Code | Inserts | Notes |
|---|---|---|
| `%v<n>` | Decimal value of `var(n)` | `%v<n>\|<w>` pads with leading zeros to width `w`. The `\|` must follow the digits directly, as in SQ1's `%v12\|2`. |
| `%m<n>` | Message `n` of the current LOGIC | Skipped if `n` is above the message count. |
| `%g<n>` | Message `n` of LOGIC 0 | Nested `%m` codes also resolve in LOGIC 0. |
| `%s<n>` | String `n` | No bounds check. |
| `%w<n>` | Word `n` of the player's input | Numbered from 1. Skipped if `n` is 0 or above the word count. |
| `%o<n>` | Name of the inventory item whose number is in `var(n)` | |

Inserted text is expanded in turn, including text the player typed. Numbers are plain digits; with none, `n` is 0. Any other character after `%` is dropped along with the `%`, and digits after it print as text. A backslash makes the next character literal and is itself dropped, so `\%` gives a percent sign, as in SQ1 LOGIC 71.

The finished buffer then goes to a printf-style output routine, which treats `%s`, `%d`, `%u`, `%x` and `%c` as codes with no arguments behind them. A literal `%` followed by one of those letters therefore prints garbage, and a reimplementation should print it as text [AGI 2.917 1000:2390].

> [!conflict] Format codes in the spec
> [4-4-Logic.html §TEXT MANAGEMENT COMMANDS] differs from 2.917 as follows.
>
> - **Contradicted:** the spec's `%0` is the letter `o`. `%0` is dropped as an unknown code. SQ1 uses neither.
> - **Contradicted:** the spec says the code takes "the item with the given number". 2.917 reads the item number from `var(n)`.
> - **Refined:** the spec shows spaces, as in `%m <number>` and `%v34 | 2`. 2.917 accepts none, so `%m 8` means `%m0` followed by " 8".

### Wrapping

Width is counted per line, and a newline byte (`0x0A`) starts a new one. When a line reaches the width, it breaks at the last space, dropping that space and any after it, and the rest of the word moves down. With no space to break at, it breaks mid-word [AGI 2.917 1000:2191].

The remembered space is only cleared by a wrap, not by a newline. A line that follows a newline and overflows before its own first space therefore breaks at a space from an earlier line, which corrupts the width count. This is a quirk a valid message shouldn't reach.

Formatting stops once 20 lines are finished. A `print` that reaches 20 lines or more gets a replacement message instead: `Message too verbose:`, the first 20 bytes of the raw message, and `Press ESC to continue.` [AGI 2.917 1000:1E0C, DS:0CCB, DS:0D09]. So the longest normal window has 19 lines. One display-specific path sets the limit to 24 and the line height to 7 pixels [AGI 2.917 1000:42CD]; its condition is unread.

### `print` windows

`print` and `print.v` first close any open window, then save the text attribute and format at a width of 30 [AGI 2.917 1000:1D96]. The window is sized to its text, with `lines` lines and `width` columns in the widest line:

- **Row:** `(19 - lines) / 2 + 1`, plus the first `configure.screen` value.
- **Column:** `(40 - width) / 2`.
- **Box:** `width * 4 + 10` units wide and `lines * 8 + 10` pixels high, with its left edge at `column * 4 - 5`.
- **Colors:** color 15 fill with a color 4 border inset from the edge, and text in black on white [AGI 2.917 1000:1EF0, 1000:54C8].

`print.at(n, row, col, width)` and `print.at.v` set the row, column and width for one call. A width of 0 means 30. Nothing checks that the window fits on screen [AGI 2.917 1000:1C96].

What happens next depends on `flag(15)` and `var(21)`, checked in that order [AGI 2.917 1000:1CE8]:

| State | Behavior | Afterward |
|---|---|---|
| `flag(15)` set | Returns at once and leaves the window open until the next `print` or `close.window` | Clears `flag(15)` |
| `var(21)` non-zero | Waits `var(21) * 10` ticks of 20 Hz, or until Enter or Esc | Closes the window and clears `var(21)` |
| Neither | Clears queued input, then waits for Enter or Esc | Closes the window |

The game clock keeps running during the wait, since the paused state isn't set. Other keys and events are discarded. See [[interpreter/event-loop]] §"Timer".

`close.window` removes an open window and does nothing otherwise [AGI 2.917 1000:1F2B].

### `display`

`display(row, col, n)` moves the cursor, formats at a width of 40, prints with the current attribute, then restores the cursor. A newline returns to column 0, not to the starting column. `display.v` takes all three from variables [AGI 2.917 1000:2250, 1000:22A7]. Display rows are absolute, so the first `configure.screen` value doesn't shift them.

Output never scrolls: on row 24, a newline stays on that row. Past column 39 it moves to the next row [AGI 2.917 1000:29F6].

### Attributes and clearing

`set.text.attribute(fg, bg)` behaves differently by mode [AGI 2.917 1000:770E, 1000:773C]:

- **Text mode:** both colors apply.
- **Graphics mode:** `bg` is only zero or non-zero. Non-zero draws inverted text and ignores `fg`, which is how the status line gets black on white. Outside type 8, the interpreter copies the character's glyph from the ROM font at `F000:FA6E`, XORs every row with `FF`, and prints it as character `0x80` with the user-font vector pointed at the copy [AGI 2.917 1000:2A7A, 1000:2C37, 1000:2C55, 1000:2AB6]. On type 8 it uses a BIOS attribute instead. Seen at runtime on EGA [2.917 runtime: menu_delivery_and_look].

`clear.lines(first, last, color)` and `clear.text.rect(row1, col1, row2, col2, color)` also don't use a real color. In graphics mode a non-zero value fills with `0xFF`, which should appear white, and 0 fills black. In text mode they always fill black [AGI 2.917 1000:764D, 1000:768C, 1000:77E6].

> [!conflict] Colors and coordinates in the spec
> **Contradicted:** [4-4-Logic.html §TEXT MANAGEMENT COMMANDS] says these commands use the given colors, and it labels `clear.text.rect`'s and `print.at`'s coordinates `x` then `y`. In 2.917, graphics mode reduces the colors as above, and the first coordinate is the row.

### Screen and status line

- **`text.screen`** sets the text-mode state that also stops object updates, and clears all 25 rows with the current attribute [AGI 2.917 1000:7603].
- **`graphics`** leaves that state, restores the screen, and redraws the status and input lines [AGI 2.917 1000:7804]. The mode switch and restore are in driver entries `9743` and `9746`; see [[concepts/screen-layers]] §"The driver overlay".
- **`configure.screen(top, input, status)`** sets the play area's top row, the input row and the status row [AGI 2.917 1000:7829]. `top` also shifts the picture by `top * 8` pixels. It redraws nothing itself. The spec's "a = 1" is only the usual value.
- **`status.line.on`** fills the status row and prints `Score:<var 3> of <var 7>` at column 1 and `Sound:on ` or `Sound:off` at column 30, using `flag(9)` [AGI 2.917 1000:34BD, DS:0F77]. **`status.line.off`** clears the row to black [AGI 2.917 1000:355C].
- **`prevent.input`** disables input and clears the input row. **`accept.input`** enables it and redraws the row [AGI 2.917 1000:386F, 1000:3898].
- **`set.cursor.char(n)`** stores the first byte of message `n` as the cursor character at `DS:05D7`. A value of 0 means no cursor [AGI 2.917 1000:38B4, 1000:37F7].

### Strings

Strings live in a table at `DS:020D`, 40 bytes each. The next variable starts at `DS:05CD`, which leaves room for exactly 24.

| Command | Behavior |
|---|---|
| `set.string(s, m)` | Copies message `m`, up to 39 characters plus the terminator [AGI 2.917 1000:0D37]. |
| `word.to.string(s, w)` | Copies input word `w`, **numbered from 0**, with the same limit. There's no check against the word count. Parsing clears the word codes but not these text pointers, so a slot past the current line's words keeps its pointer from an earlier line [AGI 2.917 1000:0D70, 1000:18C8]. A slot never used is null, which copies from `DS:0000`; see [[entities/logic]] §"Text section". At runtime it copied `80 1E 53 51`, the stack base and then the game ID `SQ` [2.917 runtime: null_message_reads]. |
| `get.string(s, m, row, col, len)` | Empties the string, prints the formatted prompt, and reads up to `len` characters, at most 39 [AGI 2.917 1000:0C44]. A row of 25 or more keeps the current cursor position. |
| `get.num(m, v)` | Prints the prompt on the input row at column 0 and reads up to 3 characters. Leading spaces are skipped, digits are read up to the first non-digit, and the low byte goes in `var(v)`, so 300 becomes 44 [AGI 2.917 1000:7126, 1000:4DC6]. |
| `parse(s)` | Ignores strings 12 and up. See [[interpreter/input-parsing]]. |

**Bounds.** Only `parse` checks a string number. `set.string`, `word.to.string`, `get.string`, `compare.strings` and `%s` accept any value, so 12 to 23 work and 24 and up overwrite later data. A reimplementation should provide 24 and treat higher numbers as errors.

**Line editing.** `get.string` and `get.num` share an editor [AGI 2.917 1000:0DA9]. Backspace removes one character. Ctrl-C and Ctrl-X clear the field. Enter accepts it. Esc abandons it, which leaves `get.string` with an empty string and `get.num` with 0, so a script can't tell Esc from empty input. It blocks the game cycle while it waits.

**Prompt.** There is no prompt command beyond string 0, which the input line formats at each redraw, so a prompt can contain format codes [AGI 2.917 1000:38D7].

**Word numbering.** `%w` counts from 1 and `word.to.string` from 0, so `%w1` and `word.to.string(s, 0)` give the same word.

**Hercules.** `get.string` and `get.num` take a separate prompt path on Hercules [AGI 2.917 1000:0CF3, 1000:718F]. It opens the centered prompt window that the Hercules input line uses, 36 columns wide and headed by the formatted prompt message, runs the normal line editor inside it, then closes it [HGC_GRAF.OVL +0x452, +0x593]. See [[interpreter/event-loop]] §"Input events".

## `said` test command — algorithm

The spec's algorithm is at [4-4-Logic.html §LOGICAL COMMANDS §TEST COMMANDS, `said(n, W(i))`], which repeats [2-6-Interpreter.html]; both are AGDS-manual chapters translated by Vassili Bykov. It is wrong in places for 2.917. See [[interpreter/input-parsing]], which holds the checked procedure.



The bytecode-level encoding of the parameter list is documented in [[entities/logic]] §"The `said` test command" (count-prefixed array of 2-byte little-endian vocabulary codes). The runtime hooks (Var(9), Flag(2), Flag(4)) are reflected in [[interpreter/variables-and-flags]].

## Save, restore and restart

See [[interpreter/save-restore]] for `save.game`, `restore.game`, `restart.game`, the save-file layout and `$AA`.

## `obj.status.v`

It shows a window, then waits, with the object number from the variable followed by x, x size, y, y size, priority and step size from object offsets `0x03`, `0x1A`, `0x05`, `0x1C`, `0x24` and `0x1E`, and continues at the next command [AGI 2.917 1000:71EE, DS:1709]. There's no bounds check on the object number. Field meanings belong to [[interpreter/view-objects]].

## Inventory commands

See [[entities/object]] for the table these commands change. `get`, `get.v`, `drop`, `put`, `put.v` and `get.room.v` match the spec except for one point.

> [!conflict] `put`
> **Contradicted:** [4-4-Logic.html §INVENTORY ITEM MANAGEMENT COMMANDS] says `put(n, m)` stores the value `m`. In 2.917 it stores `var(m)` [AGI 2.917 1000:74C5]. The command table's type byte marks neither argument as a variable, so that byte can't be used to decode this command [AGI 2.917 DS:061D entry $5F]. SQ1 never uses `put`, `put.v` or `get.room.v`, so game data can't test this [SQ1 data check, log 2026-11-01].

### `status`

The screen goes to text mode with black text on white, then shows `You are carrying:` at row 0, column 11 [AGI 2.917 1000:31D8, 1000:3346, DS:0F1E]. Items follow from row 2, two to a row. The left item starts at column 1, and the right item at column `39 - length`, so it ends at column 38 [AGI 2.917 1000:3203]. With no items, `nothing` appears at row 2, column 16.

Behavior then depends on `flag(13)`:

| | `flag(13)` set | `flag(13)` clear |
|---|---|---|
| **Row 24** | `Press ENTER to select, ESC to cancel` at column 2 | `Press a key to return to the game` at column 4 |
| **Highlight** | White on black, starting on the item whose number equals `var(25)`, otherwise the first entry | None |
| **Ends on** | Enter, which sets `var(25)` to the highlighted item; Esc, which sets it to 255 | Any key or direction event |
| **`var(25)`** | Written | Untouched |

Confirmed at runtime for the `flag(13)` case: the title, item columns and row 24 prompt appeared where stated, Enter returned the item `var(25)` started on, and Esc returned 255 [2.917 runtime: status_selection].

Up and down move two entries, and left and right move one, so right from a row's second item reaches the next row. Diagonals do nothing. A move past either end of the list is ignored, with no wrap-around [AGI 2.917 1000:33FC]. Joystick buttons count as Enter and Esc [AGI 2.917 1000:4634].

- On the `nothing` screen, Enter sets `var(25)` to 0, not 255, because the placeholder entry has number 0 [AGI 2.917 1000:32AB].
- The screen returns to graphics mode even if the game was in text mode before [AGI 2.917 1000:7804].
- The clock and sound keep running, since the paused state isn't set.
- The list has room for 50 entries and isn't bounds-checked, and entry 44 would land on row 24 [AGI 2.917 1000:3208]. SQ1 has 25 items.

## Menus

Everything here comes from AGI 2.917 [AGI 2.917 1000:9056–1000:9636]. [4-4-Logic.html §MENU MANAGEMENT COMMANDS] describes the commands only briefly and is right as far as it goes, apart from the refinements noted below.

### Building a menu

Menus and items are circular doubly linked lists, allocated from the heap with no limit on their number [AGI 2.917 1000:907C, 1000:9136]. Each node holds a pointer to its message text, not a copy.

- **`set.menu(m)`** adds a heading on row 0. The first heading is at column 1, and each later one is `length + 1` columns further on. Nothing checks that headings fit on the row.
- **`set.menu.item(m, c)`** adds an item bound to controller `c`. Rows count up from 2. The first item fixes the column for the whole menu: the heading's column, or `39 - length` if the item would reach column 39 [AGI 2.917 1000:9185].
- **`submit.menu`** ends the build and sets the first menu and its first item as current. It also raises the heap floor to the current top, so `new.room` can't release the menu or anything allocated before it, which includes a LOGIC that supplied its text [AGI 2.917 1000:91F3, 1000:1476, 1000:1485].

After `submit.menu`, `set.menu` and `set.menu.item` still consume their arguments but do nothing. Nothing clears that state, so a game builds its menu once per run, and `restart.game` keeps it [AGI 2.917 1000:9072, 1000:912C].

A menu with no items is disabled when the next `set.menu` or `submit.menu` runs [AGI 2.917 1000:909F, 1000:91FC]. Only the first item's length sets the column and the box width, so a game must pad its items to one length [AGI 2.917 1000:95CF]. SQ1 does, with one exception: its alternate `Controller` item is a character longer than the first item in that menu [SQ1 data check, log 2026-11-01].

None of these commands check that a menu exists. Calling `set.menu.item` or `submit.menu` first writes through a null pointer into low memory, corrupting low-numbered variables [AGI 2.917 1000:914B, 1000:91F8]. A reimplementation should treat that as an error.

### Enabling items

`enable.item(c)` and `disable.item(c)` change every item bound to `c`, in every enabled menu [AGI 2.917 1000:9298]. They work before `submit.menu`. They take a literal code.

`disable.item` affects only the menu. A key bound to the same code with `set.key` still fires, so a script has to guard the action itself.

`restart.game` and `restore.game` re-enable every item in every enabled menu, so a script must disable items again afterward [AGI 2.917 1000:24F8, 1000:2693, 1000:9247]. SQ1 does this: LOGIC 0 calls `disable.item(20)` when `flag(6)` is set [SQ1 data check, log 2026-11-01].

### Running the menu

`menu.input` tests `flag(14)` once. If it's set, the command sets a request flag at `DS:1D18` and returns, and nothing else happens in that cycle [AGI 2.917 1000:92EA]. If it's clear, the command does nothing. Clearing `flag(14)` afterward doesn't cancel a pending request.

The menu runs at the input step of the next cycle, after `var(19)` and `var(9)` are cleared and before queued events are drained [AGI 2.917 1000:358B]. It blocks the cycle until the player finishes. Objects stop updating, but the clock, the `var(10)` counter and sound keep going, because the paused state isn't set.

The menu reads raw events, so `set.key` bindings don't apply inside it, and any events already queued go straight to it [AGI 2.917 1000:934F, 1000:4529].

| Event | Effect |
|---|---|
| Enter on an enabled item | Queues a controller event for `c` and closes |
| Enter on a disabled item | Nothing |
| Esc | Closes with no event |
| Direction 1, 5 | Previous or next item, wrapping, and landing on disabled items is allowed |
| Direction 2, 4 | First or last item of the menu |
| Direction 3, 7 | Next or previous menu, wrapping and skipping disabled menus |
| Direction 8, 6 | First or last menu, without skipping disabled menus |
| Anything else | Nothing |

[AGI 2.917 1000:93B5, 1000:945F]. Joystick buttons count as Enter and Esc, and on a Tandy the second key table applies [AGI 2.917 1000:4634, 1000:46E8].

**Delivery.** The pump drains the queue right after the menu closes, so the chosen controller is set before LOGIC 0 runs in the same cycle. A script therefore sees the choice in the cycle after its `menu.input` call, and only in that cycle, as observed at runtime [2.917 runtime: menu_delivery_and_look], since the table is cleared at the start of each one. The controller code isn't bounds-checked anywhere, and the spec's range of 0 to 255 overruns the 50-entry table [AGI 2.917 1000:362B]. SQ1's codes go up to 28.

Each menu remembers its highlighted item, and the interpreter remembers the current menu, so the menu reopens where the player left it [AGI 2.917 1000:94ED, 1000:947F].

### Drawing

Row 0 is always the menu bar, whatever row `configure.screen` gives the status line [AGI 2.917 1000:9326]. It's filled white, with headings in black on white. The current heading and item are white on black [AGI 2.917 1000:9509, 1000:955E].

The item box is `length * 4 + 8` units wide and `(items + 2) * 8` pixels high, using the first item's length. It covers screen rows 1 to `items + 2`, with its left edge one column before the items. It uses the `print` window's box routine with fill color 15 [AGI 2.917 1000:95C4, 1000:54C8].

Disabled text is dithered in graphics modes other than Hercules and monitor type 4, where it looks the same as enabled text [AGI 2.917 1000:953E, 1000:2A85, 1000:2C46]. At runtime, with a solid font in ROM, the glyph buffer showed the mechanism: menu text is the glyph inverted, black on white; the highlighted entry is printed normally; and a disabled item is the inverted glyph ORed with alternating `55` and `AA` rows. So half of each disabled glyph's black pixels, in a checkerboard, turn white, and the text looks grey [AGI 2.917 1000:2C37, 1000:2C46; 2.917 runtime: menu_delivery_and_look].

On closing, the box area is restored from the picture and the cursor and text attribute are put back. If the status line is on it's redrawn at its own row, otherwise row 0 is cleared to black [AGI 2.917 1000:94E2, 1000:9396]. So with the status line on another row, the menu bar stays on row 0 until something overwrites it.

## Miscellaneous commands

All of these block the game cycle until they return. The commands that show a message use `print`'s wait [AGI 2.917 1000:1CE8], so they inherit its `flag(15)` and `var(21)` rules. See §"`print` windows".

### `random`

`random(min, max, v)` stores a value from `min` to `max` inclusive in `var(v)` [AGI 2.917 1000:4F42].

- **Generator.** A 16-bit linear congruential generator: `state = state * 0x7C4D + 1`, keeping the low 16 bits. The output is the state's two bytes XORed together, so it's 0 to 255 [AGI 2.917 1000:70F9, DS:1707].
- **Seed.** The state starts at 0, and whenever it's 0 at the start of a call, it's loaded from the low word of the BIOS tick count. The generator has a full period of 65,536, so this also happens once per period.
- **Range.** The output is reduced with an unsigned remainder by `max - min + 1`, computed in 16 bits, and `min` is added. The result is stored as a byte.
- **Bad ranges.** With `max` = `min - 1` the divisor is 0, so this is a divide error like `div.n` by zero. With `max` further below `min`, the divisor wraps to a large value, so the result is the raw output plus `min`, wrapping at 8 bits. SQ1 has no reversed literal range [SQ1 data check, log 2026-11-01].

Three other routines draw from the same generator [AGI 2.917 1000:0C0B, 1000:3F8E, 1000:3FA8], so the sequence isn't owned by LOGIC. A saved game doesn't store the state, since `DS:1707` is outside the blocks a save writes [AGI 2.917 1000:2816].

### `quit`, `pause`, `version`

**`quit(n)`** stops the sound first, even if the player then keeps playing. With `n` = 1 it exits at once. **Any other value asks**, not just the spec's 0, showing `Press ENTER to quit.` / `Press ESC to keep playing.` [AGI 2.917 1000:027F, DS:05E3]. The exit closes the log, restores the machine state and returns code 0 to DOS [AGI 2.917 1000:02AE, 1000:81AE].

The prompt's wait returns 1 for Enter and 0 for Esc. But with `flag(15)` set or `var(21)` non-zero it always returns 1, so `quit(0)` then exits with no confirmation, and Esc can't cancel it [AGI 2.917 1000:1D16, 1000:1D7D, 1000:4618]. Confirmed at runtime: with neither set it waited at the prompt, and with either it exited with code 0 [2.917 runtime: quit_zero_confirmation].

**`pause`** sets the paused state, which stops the clock and `var(10)` counter. It clears queued input, stops the sound, shows `Game paused.` / `Press Enter to continue.`, and clears the paused state [AGI 2.917 1000:0257, DS:0C05].

> [!conflict] `pause`
> **Contradicted:** [4-4-Logic.html §OTHER COMMANDS] says it waits for any key. 2.917 waits for Enter or Esc only, and with `flag(15)` or `var(21)` set it follows those rules instead. **Not in the spec:** the sound stops and doesn't resume, which sets its completion flag.

**`version`** shows `Adventure Game Interpreter` / `Version 2.917` as an ordinary `print` window [AGI 2.917 1000:7275, DS:0AA3].

### `shake.screen`

`shake.screen(n)` repeats an effect `n` times and blocks while it runs. The effect depends on the monitor type [AGI 2.917 1000:7939]:

| Monitor | Effect | Each `n` lasts |
|---|---|---|
| 0, 1 (CGA) and other | Moves the picture through four small offsets and back by writing CRTC registers 2 and 7. The vertical base value is `0x70` on machine type 0 and `0x38` otherwise | 5 timer ticks of 20 Hz |
| 2 (Hercules) | Copies the screen to the second page with an offset, then flips pages | 8 flips, each 4 vertical retraces |
| 3 (EGA) | Copies the screen to page 1 with an offset, then flips pages | 8 flips, each 4 vertical retraces |
| 4 | Inverts 16 VGA color registers and back, so the screen flashes rather than moves | 20 inversions, one 20 Hz tick each |

The last three are in the display overlays, at `9B23` in `HGC_GRAF.OVL`, `98F8` in `EGA_GRAF.OVL` and `9856` in `VG_GRAF.OVL`, with those files loaded at `9740`. The spec's "shakes n times" holds only loosely. At runtime, `shake.screen(1)` on CGA wrote CRTC registers 2 and 7 in five pairs around vertical base 112 over 13 ticks at 60 Hz, and on a Tandy around base 56 over 15 ticks; EGA made 8 BIOS page selects, alternating pages 1 and 0; Hercules wrote its mode port 8 times; and VGA made 21 BIOS palette calls over 58 ticks [2.917 runtime: shake_screen_by_monitor]. How each looks on a monitor isn't something the harness can show.

With `n` = 0, the count is used as a 16-bit loop counter that starts by wrapping, so it repeats 65,536 times, which in effect hangs the game [AGI 2.917 1000:79AE]. SQ1 only uses 1 and 2 [SQ1 data check, log 2026-11-01]. A reimplementation should do nothing for 0.

### `echo.line`, `cancel.line`

**`echo.line`** does nothing if input is disabled. Otherwise it appends the part of the previous line beyond the current line's length, so what's already typed stays [AGI 2.917 1000:3753, 1000:37A5]. It isn't a plain redisplay as the spec says. If the current line is as long as the previous one or longer, it changes nothing.

**`cancel.line`** sends backspaces to the input line until it's empty [AGI 2.917 1000:3726]. It doesn't check whether input is enabled.

On Hercules, while `DS:0D07` is clear, `cancel.line` does nothing and `echo.line` opens the `ENTER COMMAND` prompt window with the previous line appended, then edits it there like a typed line [AGI 2.917 1000:3775, 1000:37A5; HGC_GRAF.OVL +0x452, +0x52B].

### `open.dialogue`, `close.dialogue`

These set and clear `DS:0D07`, and nothing else [AGI 2.917 1000:3939, 1000:394B].

> [!conflict] Dialogue commands
> **Contradicted:** [4-4-Logic.html §OTHER COMMANDS] says these enable and disable `get.string` and `get.num` when `prevent.input` is in force. In 2.917 neither command reads the input-enabled state; only the event pump, `echo.line` and the input line redraw do [AGI 2.917 1000:35B3, 1000:3758, 1000:38E0]. The commands work either way.

What `DS:0D07` actually changes:

- **Hercules only:** `get.string`, `get.num`, `echo.line`, `cancel.line` and the cursor use the normal on-screen path when it's set, and otherwise the separate Hercules prompt [AGI 2.917 1000:0CB9, 1000:7136, 1000:37F7, 1000:382E].
- **All displays:** the input line's limit is 36 when it's set, instead of 40 minus the prompt's length [AGI 2.917 1000:365A].

`print` shares this flag: it sets it when the window opens, and closing any window clears it, so a `print` inside an `open.dialogue` pair ends the state early [AGI 2.917 1000:1F1F, 1000:1F47]. SQ1 uses the pair around `get.string` in LOGICs 1 and 69 [SQ1 data check, log 2026-11-01]. A reimplementation with no Hercules mode only needs the input limit.

### `init.joy`

This also runs once at startup, so it isn't only a script command [AGI 2.917 1000:0F69, 1000:4473]. It reads the joystick axes. If either reads 0 the joystick counts as absent, with no message. Otherwise it shows a centering prompt and waits for Enter, which enables the joystick, or Esc, which disables it. This wait ignores `flag(15)` and `var(21)` [AGI 2.917 1000:6075, DS:153F].

On Enter it reads the center position again and sets each axis's thresholds at the center plus or minus half of it. It then repeats a button check until two button states clear, which looks like waiting for release, though `635E` wasn't read in detail. Last, it clears queued input [AGI 2.917 1000:60D5, 1000:6110, 1000:6121].

### `toggle.monitor`

The spec's "switch RGB monitor into the graphics mode" is imprecise. It flips the monitor type between 0 and 1, which select different color tables and palette setup in the CGA driver [AGI 2.917 1000:7885, `CGA_GRAF.OVL` at `9764`, `9785`, `9821`]. It does nothing unless the machine type is 0, the room isn't 0, and the monitor type isn't 2 or 3. It then reinitializes the screen and rebuilds it through the routine `restore.game` also uses, which stops any sound [AGI 2.917 1000:5460, 1000:6755, 1000:267A].

It doesn't update `var(26)`, which is only written at startup and on restore [AGI 2.917 1000:1089, 1000:265A]. A monitor type of 4, reachable with `-v`, would flip to 5, which nothing tests for. A reimplementation with one display can ignore this command.

### `log`

`log(m)` appends to a file named `logfile`, creating it if needed. If that fails, it silently does nothing [AGI 2.917 1000:81C8, 1000:8278, DS:181B]. Each call writes two newlines, `Room <var 0>`, `Input line: <text>` and then message `m`, formatted with its codes expanded and wrapped at 78 columns [DS:17FF].

- **Refined:** the spec's "current input line" is the previous line entered, at `DS:0FC6`, not what's being typed.
- **Refined:** the spec's "followed by the message number n" is the message's text.

The handle stays open and is flushed after each call. It closes on exit and whenever the interpreter closes its files, which includes `new.room` [AGI 2.917 1000:82C5, 1000:310C]. SQ1 never calls it [SQ1 data check, log 2026-11-01].

### Former unknowns

The spec leaves these four unnamed. The names are ScummVM's [`engines/agi/opcodes.cpp`] and the behavior is from 2.917. SQ1 uses none of them, so nothing has been seen in play.

- **`$AA set.simple(s)`** copies string `s`, at most 30 characters plus the terminator, to a save-name buffer at `DS:0E6A` [AGI 2.917 1000:2726, 1000:4D21]. `save.game` and `restore.game` both test that buffer, and a non-empty value changes how they ask for a name and slot [AGI 2.917 1000:2548, 1000:2782, 1000:887D]. See [[interpreter/save-restore]] §"Named saves with `$AA`".
- **`$AB push.script`** saves the script buffer's entry count in one slot at `DS:05E1`, with no nesting [AGI 2.917 1000:70C4].
- **`$AC pop.script`** restores that count and moves the write position to match, which drops every entry added since [AGI 2.917 1000:70D6].
- **`$AD hold.key`** increments `DS:1526`, and no code ever decrements it, so the mode can't be turned off [AGI 2.917 1000:5F67, 1000:601E]. In this mode the keyboard interrupt queues a stop (a type 2 event with value 0) when a held direction key is released, so `var(6)` becomes 0 and EGO moves only while the key is held. This applies to eight keys, scan codes `47h` to `51h` except `4Ah`, `4Ch` and `4Eh` [AGI 2.917 1000:5FF8, DS:150F]. Confirmed at runtime: releasing Down set `var(6)` to 0 within a tick with `hold.key` on, and left it at 5 without [2.917 runtime: hold_key_release_stops_ego].

## What this page does not cover

4-4 contains short prose descriptions for nearly every opcode (`animate.obj`, `draw`, `erase`, `position`, `cycle.time`, etc. — most of the 182 commands). These descriptions are mostly straightforward restatements of the opcode name (`stop.cycling(n)` disables cel animation for object `n`). Re-transcribing them in the wiki would duplicate the chapter without adding value. The page above captures only items that are *non-obvious* from the opcode name in [[interpreter/commands]]: edge cases, multi-step procedures, cross-chapter conflicts, AGDS-specific authoring conventions, and the few semantics with hidden runtime requirements (PICTURE composition order, resource auto-discard, `new.room` state coordination).

For everything else, read [4-4-Logic.html] directly when implementing a particular opcode.
