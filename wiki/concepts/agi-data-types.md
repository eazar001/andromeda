# AGI Data Types

AGI command parameters and variable semantics are built on eight fundamental data types, each with distinct memory layout, scope, and purpose. 2-3-Interpreter enumerates seven (variable, flag, string, word, inventory item, object, message) [2-3-Interpreter.html §Variable Types Used]; 4-2-Logic adds Controller as an eighth source-level argument type [4-2-Logic.html §Argument types]. 4-2 also lists "Number" (no prefix) as a ninth source-syntax argument category, but Number is an immediate-literal addressing mode — every type-prefixed argument can also appear as a literal byte — and is therefore not given its own section here.

## Variable

A **variable** is an 8-bit unsigned integer (0–255) used to store numeric game state. There are 256 variables: `var(0)` through `var(255)`. All variables are initialized to 0 on interpreter startup [2-3-Interpreter.html §(1) Variable].

Variables are the most commonly used parameter type. They appear in arithmetic commands (addition, multiplication, etc.), and many AGI commands offer both a constant-parameter form and a variable-parameter form [2-3-Interpreter.html §(1) Variable].

See [[interpreter/variables-and-flags]] for the reserved-variable assignment table and shared-namespace scoping rules.

## Flag

A **flag** is a 1-bit boolean: either 0 (false) or 1 (true). There are 256 flags: `flag(0)` through `flag(255)`. All flags are initialized to 0 on interpreter startup [2-3-Interpreter.html §(2) Flag].

Flags signal when certain events or conditions have taken place [2-3-Interpreter.html §(2) Flag]. They share a global namespace across all loaded LOGIC resources.

See [[interpreter/variables-and-flags]] for the reserved-flag assignment table (`flag(0)`–`flag(15)`) and their interpreter-managed semantics.

## String

A **string** is a 40-character buffer, including the zero terminator. String 0 is conventionally the input prompt (e.g., `">"` or `"]"`) [2-3-Interpreter.html §(3) String].

The number of strings available varies by interpreter version, and the spec itself flags uncertainty about whether the larger allocations are actually usable [2-3-Interpreter.html §(3) String]:

| Interpreter version | Strings available |
|---|---|
| 2.089, 2.411 | 12 |
| (intermediate versions) | 24 |
| 3.002.107, 3.002.149 | 12 |

The spec notes both that another source claims only 12 strings are available and that the majority of AGI games have enough room for exactly 24; whether the 24-string versions actually support all 24 is unknown (agidev, unverified) [2-3-Interpreter.html §(3) String]. See [[sources/2-7-interpreter]] for the empirical enumeration of "intermediate" interpreter versions (the row covering the 24-string allocation): {2.272, 2.425, 2.426, 2.435, 2.439, 2.440, 2.915, 2.917, 2.936, 3.002.086, 3.002.098, 3.002.102}.

## Word

A **word** is a single token from the player's parsed input sentence [2-3-Interpreter.html §(4) Word]. The interpreter decomposes input into words, discards filler/punctuation, then assigns the surviving significant words to `word(1)`, `word(2)`, etc., indexed by their position in the filtered sentence.

For example, the input "look at the tree" reduces (after filtering) to `word(1) = "look"`, `word(2) = "tree"` [2-3-Interpreter.html §(4) Word]. Words can be converted to strings for display or comparison [2-3-Interpreter.html §(4) Word].

See [[interpreter/input-parsing]] for the input-preprocessing pipeline and the `said` test pattern-matching semantics. Other input-handling commands (`read`, `get_string`) are LOGIC opcodes covered by Group 3 — Logic (not yet ingested).

## Inventory Item

An **inventory item** is a reference to an entry in the OBJECT inventory table. Inventory-item parameters appear in commands like `get()` and `drop()`. In the original LOGIC source text the programmer writes named references (e.g., `get(dagger)`), but the compiled LOGIC encodes inventory items only as indices into the OBJECT table [2-3-Interpreter.html §(5) Inventory Item].

See [[entities/object]] for the OBJECT resource format (to be ingested with Group 7 — Other).

## Object

An **object**, in the interpreter's runtime, is an entry in the on-screen view-object table — one *instance* of a VIEW resource currently being managed by the interpreter [2-3-Interpreter.html §(6) Object].

**Nomenclature distinction:** The OBJECT file (covered under [[entities/object]] / inventory) has almost nothing to do with the interpreter's runtime "objects". The interpreter's objects are VIEW *instances* — many on-screen objects can reuse the same VIEW resource (e.g., multiple crocodiles drawn from one VIEW in the moats of KQ1 and Black Cauldron) [2-3-Interpreter.html §(6) Object].

When a command takes an object parameter, the value is an index into the runtime object table; the interpreter uses that index to find the VIEW instance to operate on. Many AGI commands take object parameters: `move.obj`, `animate.obj`, `set.view`, `set.cel`, `set.loop`, `draw`, and so on [2-3-Interpreter.html §(6) Object].

See [[interpreter/view-objects]] for the screen-object model and animation state management (to be added when later Group-2 chapters detail it).

## Message

A **message** is a text string stored in the message section appended to the end of a LOGIC resource file. Every LOGIC has a message section, possibly empty [2-3-Interpreter.html §(7) Message].

Messages in LOGIC 0 are global and can be referenced from any LOGIC via the format code `%g<n>`, where `<n>` is the message number in LOGIC 0. Messages in non-zero LOGICs are local to that LOGIC and only addressable from within it [2-3-Interpreter.html §(7) Message].

Example: `print("Message 34 in LOGIC.0 is %g34.")` references message 34 of LOGIC 0 from any LOGIC [2-3-Interpreter.html §(7) Message].

Messages are consumed by `$65 print`, `$67 display`, `$76 get.num`, `$8F set.game.id`, `$90 log`, `$9C set.menu`, `$9D set.menu.item`, and the `print.at` / `print.at.v` family — see [[interpreter/commands]] for the full opcode catalogue.

## Controller

A **controller** is a binding between an input event (menu item selection or key press) and a numeric identifier that LOGIC scripts can test [4-2-Logic.html §Argument types]. 4-2 documents only the source-syntax form: a controller argument uses the `c` prefix followed by a number 0–255 (e.g., `c4`). The chapter states only "Controllers are menu items and keys" without specifying the runtime mechanism or the binding opcodes (presumably `set.controller`, `set.menu`, `submit.menu`, and similar — deferred to later Group 3 chapters).

Programmer-facing intent: a single LOGIC test can detect either a function-key press or a pull-down-menu selection through the same controller value, so input-handling code is written once and the binding (`Save Game` → F5, or `Save Game` → menu item, or both) is configured separately [4-2-Logic.html §Argument types]. The bytecode-level encoding is a single byte (the controller number) wherever opcodes consume a controller parameter — confirmed by [4-3-Logic.html §Action commands] inline argument types. Test opcode `$0C controller` checks the latched event; action opcodes that bind and gate controllers include `$79 set.key`, `$9D set.menu.item`, `$9F enable.item`, and `$A0 disable.item` — see [[interpreter/commands]].

## See also

- [[interpreter/variables-and-flags]] — variables and flags as part of the reserved-slot interpreter model
- [[entities/object]] — OBJECT resource format (inventory table)
- [[interpreter/view-objects]] — on-screen object model and VIEW-instance animation
- [[interpreter/input-parsing]] — word parsing and the `said` test command
- [[sources/4-2-logic]] — source-syntax argument-type catalogue (the nine source-level prefixes), including Number / Controller
