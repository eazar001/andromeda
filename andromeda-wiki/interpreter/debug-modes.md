# Debug Modes

In 2.917, the interpreter's only debugging features are a command trace and a few commands such as `show.mem` and `obj.status.v`. The typed debug commands the spec lists are ordinary LOGIC script, written per game [2-1-Interpreter.html §What are the debug modes?]. Facts below apply to 2.917 and to SQ1's scripts, and come from static reading only.

> [!conflict] Spec vs. AGI 2.917: a built-in debugger
> The spec describes a built-in debugger, toggled by ALT-D through `flag(10)`, with phrases and a command vocabulary. In 2.917 the interpreter has no special handling of ALT-D: no code compares a key with its code [AGI 2.917 1000:4566]. Its only use of `flag(10)` is a read that gates the trace [AGI 2.917 1000:8BF3]. In SQ1, ALT-D is a script binding that has nothing to do with `flag(10)`; see below.

## Activation in SQ1

LOGIC 104 binds ALT-D to controller 14 with `set.key(0, 0x20, 14)`. Under a condition that includes that controller, LOGIC 0 sets `flag(190)`, prints a message, runs `version` and loads LOGIC 99, which holds the debug commands [SQ1 data check, LOGIC 0, 99, 104]. The full condition hasn't been decoded.

SQ1's scripts never set `flag(10)` by number. The only route found is LOGIC 99's "set flag" command, which takes the flag number from the player through `set.v` [SQ1 data check]. LOGIC 99 tests `flag(10)` once, before a `call(95)`.

**Per-game magic phrases.** Unread: the spec gives these, and they would be script behavior, but these games aren't available locally:

| Game | Magic phrase |
|---|---|
| Gold Rush | `bird man` |
| King's Quest 3 | `rats ass` |
| Police Quest | `stink bug` |

## Debug command vocabulary

These are `said` tests in a game's scripts, so a reimplementation needs nothing for them beyond running LOGIC. Searching the decoded interpreter for `show`, `gimme`, `tp` and `priority` finds nothing, and `AGIDATA.OVL`'s strings don't include them. The table compares the spec's list with SQ1's LOGIC 99, matched by word group from `WORDS.TOK` [2-1-Interpreter.html §What are the debug modes?; SQ1 data check].

| Command | Spec's action | In SQ1 |
|---|---|---|
| `TP` | Teleport to another room | Present: asks for a room number, then `new.room.v` |
| `GET OBJECT` | Acquire inventory items | Present, but asks for an object number. The spec has it acquiring all items |
| `GIMME GIMME` | Acquire all inventory items | Absent: `gimme` isn't in the vocabulary |
| `SHOW PRIORITY` | Overlay the priority screen | Present |
| `SHOW FLAG` | Display all flags | Present, but asks for one flag number and reports that flag |
| `SHOW VAR` | Display all variables | Present, but asks for one variable number and shows that variable |
| `SET FLAG <n>` | Set `flag(n)` | Present, and asks for the number instead of parsing it |
| `SET VAR <n> <v>` | Set `var(n)` to `v` | Present, and asks for both values |
| `POSITION` | Print ego's `(x, y)` | **Differs**: asks for x and y, then erases EGO, ready to move it. Accepts `pos` too |
| `SHOW POSITION` | Same as `POSITION` | Not present as a separate command |
| `OBJECT NUMBER`, `OBJECT ROOM`, `ROOM` | List items, rooms, current room | Not present as such |
| `SET PRIORITY <n>`, `RELEASE PRIORITY` | Set or release ego's priority | Not present |

SQ1 adds others: `reset flag`, `show mem`, `object` or `sp` (asks for an object number, then `obj.status.v`), `cash`, and some game-specific view swaps. The body of each command beyond its first few instructions hasn't been read in detail, and neither has how the `said` groups combine with `or`.

## Command trace

The trace shows each command as it runs, in a window, and waits for a key after each one [AGI 2.917 1000:8D44].

### Turning it on and off

- **Scroll Lock** reads the BIOS toggle state on every keyboard poll. Any change, on or off, toggles the trace, so the key's light doesn't indicate whether the trace is on. The first poll only records a baseline [AGI 2.917 1000:59C1].
- **`trace.on`** opens it directly [AGI 2.917 1000:8BCA]. SQ1 never uses it [SQ1 data check].
- **`flag(10)`** must be set for either to open the trace. If it's clear, nothing happens [AGI 2.917 1000:8BF3]. Closing doesn't check the flag, and restores the screen under the window [AGI 2.917 1000:8CB2].

If the trace is already on, `trace.on` returns one byte further on in the bytecode, which skips the byte after the command [AGI 2.917 1000:8BD9]. It looks like a bug; a script that calls it twice with the trace on would desynchronize.

### `trace.info(names, top, height)`

It stores three bytes without side effects [AGI 2.917 1000:8C76]:

- **`names`** is the number of a LOGIC whose messages hold command names. Zero means none.
- **`top`** positions the window: its top text row is the `configure.screen` row offset plus `top` plus 1.
- **`height`** is the number of rows, and a value below 2 becomes 2.

The window spans text columns 2 to 37 [AGI 2.917 1000:8C01]. The values aren't in the save file. They persist across a restart and a restore. SQ1 calls `trace.info(95, 3, 10)` in LOGIC 104 [SQ1 data check].

The names LOGIC is loaded by `new.room` and `restart.game` [AGI 2.917 1000:182B, 1000:24E7], and these loads aren't recorded in the script buffer. So after a restore it's gone until the next room change, unless a script loaded it.

### What it shows

Commands are traced at the dispatchers: an action before it runs, and a test after it runs [AGI 2.917 1000:02DA, 1000:07FB]. `if`, `goto` and `return` go through neither path and are never shown [AGI 2.917 1000:02C4, 1000:293C].

> [!conflict] Spec vs. AGI 2.917: what the trace covers
> The spec says the trace displays on every `if` evaluation, showing the test command [2-1-Interpreter.html §What are the debug modes?]. In 2.917 it shows every action as well as every test, and it never shows the `if` itself.

For each command, the window scrolls up one line, using the BIOS scroll service, and prints on the bottom row [AGI 2.917 1000:8FAD, 1000:2C07]:

1. A line of 26 `=` signs first, if LOGIC 0 has been entered since the last traced command [AGI 2.917 1000:12F9, 1000:8D6C].
2. The running LOGIC's number, a colon, and the command's name. An action's name is message *n* of the names LOGIC, and a test's is message *n* + 220 [AGI 2.917 1000:8CF8, 1000:8D2A, 1000:8DC1]. With no names LOGIC, it prints the number instead. A test numbered 0 prints `return`, which is the only way that text can appear.
3. The arguments in parentheses, as raw values. `said` takes its count from the bytecode and prints 16-bit word codes [AGI 2.917 1000:8D17, 1000:8E62, 1000:8F70].
4. If the command has variable arguments, a second line in parentheses with those replaced by their current values, using the table's type mask from bit `0x80` down [AGI 2.917 1000:8EEF, 1000:8F26].
5. For a test, ` :T` or ` :F` at the right edge of the bottom row [AGI 2.917 1000:8DF4].

SQ1's LOGIC 95 fits this numbering: message 1 is `increment` and message 135 is `show.mem`. Its header counts 238 messages, which is 220 plus the 18 tests, and its last non-empty messages are test names ending in `right.posn` [SQ1 data check].

If a names LOGIC is set but isn't loaded, the lookup returns zero, and the number printed comes from `DS:0002`, the first character of the game ID, rather than from a LOGIC [AGI 2.917 1000:8DA4].

### Stepping

After each command the trace waits for a key event. Other events are consumed and ignored. Pressing `+` suppresses the display until the next LOGIC starts running, at which point stepping resumes. Any other key steps once [AGI 2.917 1000:8E24, 1000:8E50, 1000:12E6]. If the trace closes during the wait, the wait ends [AGI 2.917 1000:8E24].

The trace saves and restores the cursor and text attribute around its output, and swaps the current LOGIC while it reads a name [AGI 2.917 1000:8D56, 1000:8D97, 1000:8E56].

## See also

- [[interpreter/variables-and-flags]] — `flag(10)` semantics.
- [[interpreter/commands]] — `$85 obj.status.v`, `$95 trace.on`, `$96 trace.info`.
- [[interpreter/command-semantics]] — `obj.status.v`.
- [[sources/2-1-interpreter]] — source chapter.
- [[sources/agi-2917-binary]] — routine map.
