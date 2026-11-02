# Command Semantics

Selected behavioral semantics for LOGIC opcodes, sourced from [4-4-Logic.html] (an AGDS-manual chapter translated from Russian by Vassili Bykov, with translator's notes from Bykov and clarifying replies from Lance Ewing). This page surfaces high-value items — edge-case behavior, multi-step procedures, runtime constraints, and mnemonic / argument-count conflicts with [[interpreter/commands]]. The chapter itself documents prose behavior for every opcode; for the full text refer directly to `AGI_Specifications/Specifications/4-4-Logic.html`.

Companion pages:

- [[interpreter/commands]] — opcode dispatch table (signatures, argument types). Source: 4-3.
- [[entities/logic]] — bytecode container format. Source: 4-1.
- [[interpreter/priority-bands]] — y → priority auto-assignment table (`release.priority`).

## Page-level caveats

- No LOGIC decoder in `resource/`; every behavioral claim is `(agidev, unverified)` against working code. SQ1 confirms argument counts only, not behavior (see [[interpreter/commands]]).
- 4-4 is an AGDS manual chapter. AGDS surface syntax (`if_`, `else_`, `not_`, `or_` — keywords with trailing underscores) differs from the AGI Studio syntax in [[sources/4-2-logic]] (`if () { }`, `else { }`, `&&`, `||`, `!`). Both compile to the same `$FC..$FF` bytecode control-flow opcodes; the underscore-suffixed mnemonics are AGDS authoring conventions, not bytecode-level distinctions.

## Arithmetic edge cases

The chapter flags four behaviors as unspecified, marked with translator's-note brackets [VB] (Vassili Bykov) [4-4-Logic.html §ARITHMETIC COMMANDS]. AGI 2.917 settles them [AGI 2.917 1000:728E–1000:73BC]:

1. **`addn` / `addv` overflow** — wraps at 8 bits, so 250 + 10 = 4.
2. **`subn` / `subv` underflow** — wraps at 8 bits, so 1 - 2 = 255.
3. **`mul.n` / `mul.v` overflow** — keeps the low 8 bits of the product.
4. **`div.n` / `div.v` by zero** — the interpreter neither checks for it nor installs a handler for the CPU's divide error, so control passes to DOS [AGI 2.917 1000:7395, 1000:8369]. The result on real hardware is Runtime only. A reimplementation should treat it as a fatal error. Division is unsigned and keeps the quotient.

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

This is a hard runtime constraint: load order determines unload order. The mechanism by which the interpreter tracks load order is not specified in 4-4 and is not visible in [[interpreter/memory-layout]] (which is sourced from 2-4 and is unverifiable without DOS-era memory instrumentation). `(agidev, unverified)`.

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
| Discard LOGIC | — | — | **No discard.logic.** Lance Ewing: "There must be some other way that those commands are removed from memory, because the commands you mention above don't exist." Probable explanation: LOGICs are unloaded by the auto-discard rule on `new.room`. |
| Discard SOUND | — | — | **No discard.sound.** Same probable explanation as LOGIC. |

### PICTURE composition ordering

[4-4-Logic.html §PICTURE RESOURCE MANAGEMENT COMMANDS]:

> "Please use the following sequence of commands when loading PICTURE resources:
>  `load.pic(n); draw.pic(n); discard.pic(n); ...; show.pic;`
>  Any other order may crash the interpreter without any diagnostic messages."

The discard between `draw.pic` and `show.pic` is intentional — the picture is rendered into a back buffer by `draw.pic`, the PICTURE resource memory is no longer needed, and `show.pic` blits the buffer. Skipping the discard or reordering the calls is documented as a hard crash hazard.

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
| VIEW with **4+ loops** | * | 3 | 0 | 0 | 0 | 2 | 1 | 1 | 1 |

`*` means "current loop retained" — the auto-selector does not change loop for stationary objects (direction 0) or for directions that have no canonical loop mapping in the 2-/3-loop variant.

The two tables differ only for directions 1 and 5: 4+ loops uses dedicated up (loop 3) and down (loop 2) animations; 2-/3-loop VIEWs retain whatever loop is currently displayed.

## Base-point semantics

> [!conflict]
> **The chapter contradicts itself on cel base-point location.** [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS] line 363 (`get.posn`) states: "Coordinates of the object are coordinates of the base point (bottom **left** corner) of cels of the VIEW resource". [4-4-Logic.html §OTHER COMMANDS] line 854 (`upper.left`) states: "Usually the crossing by an object of various areas and lines is tracked by the base point (bottom **right** corner) of its cel." Same chapter, same author, opposite descriptions. The `upper.left` command's name and its description ("After this command, top left corner is used as such a point") imply the default is some *bottom* corner, but the chapter is internally inconsistent about which one.
>
> Provisional reading: the spec is wrong in one of the two places; `(agidev, unverified)` until ScummVM or VIEW-renderer behavior validates. The bottom-left form is the more commonly cited value in AGI lore.

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

The variable-form `add.to.pic.v` takes 7 `var` arguments (verified against [4-3-Logic.html]).

**Margin rule** [4-4-Logic.html line 509]: "If margin is 0, 1, 2, or 3, the base of the cel is surrounded with a rectangle of the corresponding priority. If margin > 4, this extra margin is not shown."

> [!conflict]
> **Margin = 4 behavior is unspecified.** The spec covers `margin ∈ {0, 1, 2, 3}` (priority-margin rectangle drawn) and `margin > 4` (no margin), but not `margin == 4`. Plausibly a typo for "margin ≥ 4" or "margin > 3"; conclusive resolution requires implementation cross-check. `(agidev, unverified)`.

PICTURE bytecode has no VIEW-composition opcodes ([[entities/picture]]), so `add.to.pic` is purely a LOGIC-side operation.

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
- **Graphics mode:** `bg` is only zero or non-zero. Non-zero draws inverted text and ignores `fg`, which is how the status line gets black on white. How inverted glyphs reach the screen varies by display and is unread.

`clear.lines(first, last, color)` and `clear.text.rect(row1, col1, row2, col2, color)` also don't use a real color. In graphics mode a non-zero value fills with `0xFF`, which should appear white, and 0 fills black. In text mode they always fill black [AGI 2.917 1000:764D, 1000:768C, 1000:77E6].

> [!conflict] Colors and coordinates in the spec
> **Contradicted:** [4-4-Logic.html §TEXT MANAGEMENT COMMANDS] says these commands use the given colors, and it labels `clear.text.rect`'s and `print.at`'s coordinates `x` then `y`. In 2.917, graphics mode reduces the colors as above, and the first coordinate is the row.

### Screen and status line

- **`text.screen`** sets the text-mode state that also stops object updates, and clears all 25 rows with the current attribute [AGI 2.917 1000:7603].
- **`graphics`** leaves that state, restores the screen, and redraws the status and input lines [AGI 2.917 1000:7804]. The mode switch and restore are in driver entries `9743` and `9746`, which are unread.
- **`configure.screen(top, input, status)`** sets the play area's top row, the input row and the status row [AGI 2.917 1000:7829]. `top` also shifts the picture by `top * 8` pixels. It redraws nothing itself. The spec's "a = 1" is only the usual value.
- **`status.line.on`** fills the status row and prints `Score:<var 3> of <var 7>` at column 1 and `Sound:on ` or `Sound:off` at column 30, using `flag(9)` [AGI 2.917 1000:34BD, DS:0F77]. **`status.line.off`** clears the row to black [AGI 2.917 1000:355C].
- **`prevent.input`** disables input and clears the input row. **`accept.input`** enables it and redraws the row [AGI 2.917 1000:386F, 1000:3898].
- **`set.cursor.char(n)`** stores the first byte of message `n` as the cursor character at `DS:05D7`. A value of 0 means no cursor [AGI 2.917 1000:38B4, 1000:37F7].

### Strings

Strings live in a table at `DS:020D`, 40 bytes each. The next variable starts at `DS:05CD`, which leaves room for exactly 24.

| Command | Behavior |
|---|---|
| `set.string(s, m)` | Copies message `m`, up to 39 characters plus the terminator [AGI 2.917 1000:0D37]. |
| `word.to.string(s, w)` | Copies input word `w`, **numbered from 0**, with the same limit. An empty slot gives an empty string, because it reads the zero bytes at `DS:0000` [AGI 2.917 1000:0D70, 1000:18C8]. |
| `get.string(s, m, row, col, len)` | Empties the string, prints the formatted prompt, and reads up to `len` characters, at most 39 [AGI 2.917 1000:0C44]. A row of 25 or more keeps the current cursor position. |
| `get.num(m, v)` | Prints the prompt on the input row at column 0 and reads up to 3 characters. Leading spaces are skipped, digits are read up to the first non-digit, and the low byte goes in `var(v)`, so 300 becomes 44 [AGI 2.917 1000:7126, 1000:4DC6]. |
| `parse(s)` | Ignores strings 12 and up. See [[interpreter/input-parsing]]. |

**Bounds.** Only `parse` checks a string number. `set.string`, `word.to.string`, `get.string`, `compare.strings` and `%s` accept any value, so 12 to 23 work and 24 and up overwrite later data. A reimplementation should provide 24 and treat higher numbers as errors.

**Line editing.** `get.string` and `get.num` share an editor [AGI 2.917 1000:0DA9]. Backspace removes one character. Ctrl-C and Ctrl-X clear the field. Enter accepts it. Esc abandons it, which leaves `get.string` with an empty string and `get.num` with 0, so a script can't tell Esc from empty input. It blocks the game cycle while it waits.

**Prompt.** There is no prompt command beyond string 0, which the input line formats at each redraw, so a prompt can contain format codes [AGI 2.917 1000:38D7].

**Word numbering.** `%w` counts from 1 and `word.to.string` from 0, so `%w1` and `word.to.string(s, 0)` give the same word.

**Hercules.** `get.string` and `get.num` take a separate prompt path on Hercules [AGI 2.917 1000:0CF3, 1000:718F], which is unread.

## `said` test command — algorithm

The spec's algorithm is at [4-4-Logic.html §LOGICAL COMMANDS §TEST COMMANDS, `said(n, W(i))`], which repeats [2-6-Interpreter.html]; both are AGDS-manual chapters translated by Vassili Bykov. It is wrong in places for 2.917. See [[interpreter/input-parsing]], which holds the checked procedure.



The bytecode-level encoding of the parameter list is documented in [[entities/logic]] §"The `said` test command" (count-prefixed array of 2-byte little-endian vocabulary codes). The runtime hooks (Var(9), Flag(2), Flag(4)) are reflected in [[interpreter/variables-and-flags]].

## Menu input mechanism

[4-4-Logic.html §MENU MANAGEMENT COMMANDS]. Menu items bind to controller codes via `$9D set.menu.item(message, cntrl)`. Activation is via `$A1 menu.input` (conditional on Flag(14) = 1). After the player picks an item, the bound controller code becomes the latched event tested by `$0C controller(c)` in subsequent cycles. The same controller test fires for `$79 set.key` keyboard bindings, so menu and key handlers share the same dispatch path — already documented in [[concepts/agi-data-types]] §"Controller".

## What this page does not cover

4-4 contains short prose descriptions for nearly every opcode (`animate.obj`, `draw`, `erase`, `position`, `cycle.time`, etc. — most of the 182 commands). These descriptions are mostly straightforward restatements of the opcode name (`stop.cycling(n)` disables cel animation for object `n`). Re-transcribing them in the wiki would duplicate the chapter without adding value. The page above captures only items that are *non-obvious* from the opcode name in [[interpreter/commands]]: edge cases, multi-step procedures, cross-chapter conflicts, AGDS-specific authoring conventions, and the few semantics with hidden runtime requirements (PICTURE composition order, resource auto-discard, `new.room` state coordination).

For everything else, read [4-4-Logic.html] directly when implementing a particular opcode.
