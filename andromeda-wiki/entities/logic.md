# LOGIC Resource Format

A LOGIC resource holds the bytecode program for a single room. Each room has one associated LOGIC file (numbered 0–255); LOGIC.0 is special and runs continuously, while other LOGICs are invoked from it directly or transitively. The on-disk LOGIC resource has three regions: the universal [[entities/vol-file]] resource header, a 2-byte text-offset prefix, the bytecode section, and the encrypted text-message section.

This page documents the on-disk format. Execution semantics (opcode behavior, VM cycle integration) live under [[interpreter/overview]] and its detail pages.

The Python prototype in `resource/` has no LOGIC decoder, so these claims are unverified against project code. A throwaway walker did decode all 101 SQ1 LOGICs with no desyncs or bad branch targets, which confirms the control-flow bytes, argument counts, and text-section layout on that game [SQ1 data check, log 2026-11-01]. Execution semantics are on the interpreter pages, audited against 2.917.

## Format overview

```
+-----------------------------+
| VOL resource header (5 B)   |  See [[entities/vol-file]]: signature 0x1234, VOL number, length
+-----------------------------+
| Text offset (2 B, LE)       |  Distance from the first bytecode byte to the text section
+-----------------------------+
| Bytecode section            |  Commands, control-flow opcodes, condition codes
+-----------------------------+
| Text section (encrypted)    |  Message count + offset table + Avis-Durgan-XOR'd message bodies
+-----------------------------+
```

[4-1-Logic.html §THE HEADER, §THE TEXT SECTION]

The spec describes this as "a seven-byte header" — the first 5 bytes are the universal VOL resource header documented in [[entities/vol-file]]; only the trailing 2-byte text offset is LOGIC-specific. For brevity below, "the header" refers to the full 7-byte prefix.

**Versioning:** 4-1-Logic specifies v2 only. The chapter notes "the header of each logic script is seven bytes in length for games before 1988. After this date compression seems to have been introduced and the header was subsequently altered" — implying v3 LOGIC headers differ. v3 LOGIC layout is unspecified in this chapter [4-1-Logic.html §THE HEADER].

## Header

| Offset | Size | Field | Format | Source |
|--------|------|-------|--------|--------|
| 0 | 5 | VOL resource header | Universal — see [[entities/vol-file]] | [[entities/vol-file]], [3-2-Files.html §VOL File Format] |
| 5 | 2 | Text offset | Little-endian, unsigned | [4-1-Logic.html §THE HEADER] |

**Text offset** — distance in bytes from the first bytecode byte (byte 7 of the resource) to the text section, so the section starts at byte `7 + offset` [AGI 2.917 1000:11E8]. Bytecode occupies the `offset` bytes after the header.

> [!conflict] Text offset base
> **Contradicted:** this page used to measure the offset from byte 0 of the VOL header. The spec gives no base, only "Offset of logic code end and text begin" [4-1-Logic.html §THE HEADER]. Measuring from the first bytecode byte puts the end pointer exactly at the end of the resource on all 101 SQ1 LOGICs, and measuring from the VOL header does so on none [SQ1 data check, log 2026-11-01].

**Example** [4-1-Logic.html §THE HEADER]: KQ1 Room 2 header is `12 34 01 5F 06 BA 02` — signature `0x1234`, VOL `01`, payload length `0x065F` (1631 bytes including the 2-byte text-offset field and everything after it), text offset `0x02BA` (714 bytes of bytecode, so the text section starts at resource byte 721).

## Bytecode section

Begins immediately after the header (byte 7 of the resource) and runs until the text offset. Three byte ranges are dispatched differently [4-1-Logic.html §THE LOGIC CODES]:

| Range | Meaning |
|-------|---------|
| `$00 .. $B5` | AGI commands (e.g. `animate.obj`, `load.pic`, `printf`). `$00` is `return`, handled before the command table is used. In 2.917 the valid range is `$01..$AD`; `$AE..$FB` raises error `0x10` with the opcode in `var(18)` [AGI 2.917 1000:02C4]. The upper bound varies by version; Manhunter 2 reaches `$B5` [4-1-Logic.html §THE LOGIC CODES, §NEW INFORMATION ON LOGIC INTERPRETATION]. |
| `$00 .. $12` | Test condition codes (e.g. `isset`, `equaln`, `posn`, `said`). Only read inside an `if`, between the opening and closing `$FF` [4-1-Logic.html §TEST CONDITIONS]. `$00` is a test here, one that is always false [AGI 2.917 1000:09D8]. |
| `$FC .. $FF` | Control-flow opcodes (see below). |

### Control-flow opcodes

| Code | Mnemonic | Effect |
|------|----------|--------|
| `$FF` | `if` open/close | Opens condition evaluation. The closing `$FF` is followed by a 2-byte little-endian offset, added to the position after those bytes if the condition is false [AGI 2.917 1000:29F0]. |
| `$FE` | `else` / `goto` | Reads a 2-byte little-endian offset and adds it to the position after those bytes, wrapping at 16 bits, so negative offsets branch back [AGI 2.917 1000:2957]. `else` and `goto` are the same byte; the interpreter does not distinguish them. |
| `$FD` | `not` | Toggles inversion of the next test only, so two in a row cancel. It stays pending across an `$FC`, and it does not invert a whole bracket [AGI 2.917 1000:298A, 1000:2996]. |
| `$FC` | `or` bracket | Used in pairs; tests between them are ORed. Outside a bracket, tests are ANDed [4-1-Logic.html §TEST CONDITIONS]. Brackets cannot nest, since an `$FC` inside a bracket always closes it [AGI 2.917 1000:2973]. |

### Condition evaluation

Conditions short-circuit in 2.917, which matters because `said` and `have.key` have side effects [AGI 2.917 1000:296C]:

- **A false test outside a bracket** fails the whole `if` at once. The interpreter skips to the closing `$FF` without running the remaining tests.
- **A true test inside a bracket** skips to the closing `$FC` without running the rest of the bracket.
- **Reaching a closing `$FC` with no true test** fails the whole `if`. An empty `$FC $FC` is therefore false.
- **An `if` with no tests** (`$FF $FF`) is true.

Skipping uses each test's argument count from the table, except that `said` reads its own count byte. Bytes from `$FC` up are skipped singly, apart from the `$FC` or `$FF` that ends the skip [AGI 2.917 1000:29A6, 1000:29CC].

An `$FC` or `$FD` outside an `if` hangs 2.917: the dispatcher returns without consuming it, and the bytecode loop calls it again forever [AGI 2.917 1000:02C4, 1000:295C]. A valid game can't rely on this, so a reimplementation should report an error. An `$FE` inside a condition reaches the test dispatcher and raises error `0x0F` [AGI 2.917 1000:0812].

### Control-flow examples

`if (isset(5)) { ... }` [4-1-Logic.html §THE LOGIC CODES, Example 3 KQ1 Room 2]:

```
FF 07 05 FF      ; if (isset(flag 5))
84 00            ; bracket distance 0x0084 — skip 132 bytes if false
... body ...
```

`if (cond) { ... } else { ... }` — when an `else` follows the `if`, the spec notes the `if`'s closing bracket distance is **inflated by 3 bytes** so it jumps past the `$FE` opcode and its 2-byte offset, landing on the start of the `else` body [4-1-Logic.html §THE ELSE COMMAND AND MORE ON BRACKETS]:

```
FF ... FF        ; if (cond), with closing bracket distance N+3
... if body ...
FE off_lo off_hi ; else: unconditional branch (skip the else body)
... else body ...
```

Multiple conditions [4-1-Logic.html §TEST CONDITIONS]:

```
FF 07 05 07 06 FF              ; if (isset(5) && isset(6))        — sequential = AND
FF FC 07 05 07 06 FC FF        ; if (isset(5) || isset(6))        — wrapped in $FC pair
FF FC 07 06 07 06 FC FD 07 08 FF   ; if ((isset(6) || isset(6)) && !isset(8))
```

### Inner loops

AGI has no `while` / `for` / `do..while` opcodes. Loops are encoded as `if` blocks whose body ends with an `$FE` `goto` carrying a negative offset that branches back into the test [4-1-Logic.html §INNER LOOPS]. SQ2 example:

```
FF FD 0D FF 03 00 FE F7 FF     ; do { ... } while (!havekey)
                               ; 0xFFF7 = -9 (two's complement) — branches back to the if
```

### Entry-point control

`set.scan.start()` makes the byte after it the entry point for later runs of this LOGIC, and `reset.scan.start()` restores the start of the bytecode section [AGI 2.917 1000:1335, 1000:134A; 4-1-Logic.html §NEW INFORMATION ON LOGIC INTERPRETATION]. The entry point lives in the LOGIC's in-memory record, so it's lost when that record is discarded.

## Argument dispatch

Each AGI command and condition code has a fixed argument count (≤ 7) and a per-argument type signature, both stored in a lookup table compiled into the interpreter binary (file `AGIDATA.OVL` on the PC version) rather than in any LOGIC resource [4-1-Logic.html §ARGUMENTS].

The argument-type byte encodes which arguments are variable references vs. literal numbers: bits 7..1 correspond to arguments 1..7 (bit set ⇒ variable, bit clear ⇒ number); bit 0 is unspecified `(agidev, unverified)`. Examples:

- `0x80` — argument 1 is a variable, the rest are numbers.
- `0x60` — arguments 2 and 3 are variables, the rest are numbers.

> [!conflict] What the type byte does in AGI 2.917
> **Contradicted:** the type byte does not control execution. Every handler hard-codes which arguments it dereferences. The only reader found is the trace display, which uses the byte to show variable arguments' current values [AGI 2.917 1000:8CDC, 1000:8EEF, 1000:8F26], so as far as the code read shows, it exists for debugger output.
>
> **The byte is also wrong for some commands.** `$5F put` (`0x00`) and `$60 put.v` (`0x40`) understate their variable arguments, and `$A2 show.obj.v` has `0x01` where `0x80` would be expected [AGI 2.917 1000:74C5, 1000:74F0, 1000:5DD3]. A decoder can use the table's argument count, but should not trust this byte for execution.
>
> **Confirmed:** the argument count is live. The `if` scanner uses it to skip failed tests [AGI 2.917 1000:29C0].

This is also where the version-conditional argument-count changes documented in [[interpreter/command-evolution]] live (`quit`, `print.at`, `print.at.v`, unknown command #176).

## Text section

The text section is always present (possibly with zero messages). Layout [4-1-Logic.html §THE TEXT SECTION]:

| Offset (relative to text section start) | Size | Content |
|---|---|---|
| 0 | 1 | Number of messages (0–255) |
| 1 | 2 | Little-endian offset to the end of the message data, relative to **byte 1** of the section |
| 3 | 2 × num_messages | Offset table: one little-endian offset per message, each relative to **byte 1** of the section |
| ... | varies | Encrypted message bytes; each message is null-terminated (`0x00`) |

**Encryption.** Every byte of every message body is XOR'd with the repeating 11-byte key `"Avis Durgan"` [4-1-Logic.html §THE TEXT SECTION]. The spec states this directly and shows worked examples of decrypted message bytes. The implication of [2-8-Interpreter.html §AGI VERSION THREE] ("v3 LOGIC files do not encrypt the text messages with 'Avis Durgan' since there is no need to do this because it is compressed anyway") is consistent: v2 encrypts, v3 does not. Note that the key is the same as the OBJECT-file XOR key already used in [resource/objects.py] — the same key, different consumer.

**Pointer base.** Message and end pointers count from the byte after the message count, not from the section start. Reading them from the section start lands each pointer on the previous message's terminator, so nearly every message decodes as empty. On all 101 SQ1 LOGICs, section length minus the end pointer is exactly 1 [SQ1 data check, log 2026-11-01].

**What is encrypted.** The count, end pointer, and offset table are stored in the clear. The XOR covers the single range from the first byte after the offset table to the end pointer, starting at key index 0. The key doesn't restart per message, and terminators are XORed like any other byte [AGI 2.917 1000:1229, 1000:07AB; SQ1 data check, log 2026-11-01]; see also [Code/logic.c:loadMessages].

**Message access via LOGIC.** The `print` command (and similar) takes a 1-byte message number — e.g. `65 08` is `print(message #8)` [4-1-Logic.html §THE TEXT SECTION]. Numbers start at 1, because slot 0 of the pointer table is the end pointer [AGI 2.917 1000:21F0]. So message `n` uses the pointer at section byte `1 + 2n`.

In 2.917, a number above the message count produces a null text pointer. `print` then draws a minimal empty box at row 10, column 20 and prints whatever its uninitialized buffer holds, then waits as usual; `display`, `get.string` and `get.num` print the same kind of garbage [AGI 2.917 1000:1F54]. `set.string` and `set.cursor.char` read from `DS:0000` instead, which holds the stack base after startup rather than zeros [AGI 2.917 1000:008C, 1000:0D37, 1000:38B4]. So `set.cursor.char` takes that base's low byte, and `set.string` copies its two bytes and then the game ID. If the base is `DS:1E80`, as [[interpreter/memory-layout]] predicts, neither gives an empty result. Runtime only. `%m` and `%g` skip such a message. A reimplementation should treat it as an error or as empty text. A slot holding 0 raises error `0x0E` with the number in `var(18)` [AGI 2.917 1000:21F0]. Message 0 resolves to the end of the text section.

## Loading and running

Each loaded LOGIC has a 10-byte record on a linked list: next record, LOGIC number, message count, start of bytecode, current entry point, and start of the text section after its count byte [AGI 2.917 1000:119A]. Loading sets the entry point to the start of the bytecode and decrypts the messages in place. The list head is `DS:096F`.

`load.logics` loads a LOGIC if it is absent and does nothing to the record otherwise, so it doesn't reset the entry point [AGI 2.917 1000:117D, 1000:119A].

`call` works as follows [AGI 2.917 1000:12AE]:

- **Already loaded:** the LOGIC runs from its entry point and stays loaded.
- **Not loaded:** it is loaded, run, then cut from the list, and the heap top is reset to its record. Everything allocated after that record goes with it. A resource loaded during the call stays on its own list with a stale pointer, because only the LOGIC list is cut, by reading only; see [[interpreter/memory-layout]] [AGI 2.917 1000:12AE].
- **Current LOGIC:** the previous value is restored on return, so calls nest. The only limit found is the stack guard in [[interpreter/event-loop]] §"Timer".

Variables and flags are not touched by `call`. If the called LOGIC changed rooms, the zero return stops every caller. See [[interpreter/event-loop]] §"When `new.room` takes effect".

## The `said` test command

`said` (condition code `$0E`) has a variable argument count [4-1-Logic.html §THE 'SAID' TEST COMMAND]:

```
FF 0E 01 1E 01 FF                  ; if (said("marble"))      — 1 word: vocab code 0x011E
FF 0E 02 37 02 73 00 FF            ; if (said("open", "door")) — 2 words: 0x0237, 0x0073
```

The byte immediately following `$0E` is the count of 2-byte little-endian word codes that follow. Word codes are looked up against [[entities/words-tok]]. For the preprocessing pipeline that produces the parsed-word vector against which `said` matches, see [[interpreter/input-parsing]].

## How the interpreter decodes LOGIC

4-1 includes annotated x86 ASM from Manhunter: San Francisco showing the original interpreter's decode loop [4-1-Logic.html §HOW THE INTERPRETER HANDLES LOGIC CODE]. The high-level state machine:

1. **Normal mode** — read one byte. `$00`, `$FE` and `$FF` are handled by the loop; anything else goes to the action dispatcher, which runs commands until it meets a byte it can't dispatch.
2. **`$FF` (if open)** — evaluate tests as described in "Condition evaluation". When true, step past the closing `$FF` and its 2 offset bytes into the body. When false, add the offset.
3. **`$FE` (else / goto)** — read 2-byte signed offset and add to the execution pointer unconditionally.
4. **`$00` (return)** — exit this LOGIC and return to the caller [AGI 2.917 1000:294B].

The interpreter never looks for an `else`. The distance inflated by 3 is purely the compiler's doing: it makes a false condition land past the `$FE` and its offset, and a true condition runs into the `$FE` and jumps over the else body [AGI 2.917 1000:29F0, 1000:2957; 4-1-Logic.html §THE ELSE COMMAND AND MORE ON BRACKETS].

> [!conflict] Why `else` adds 3
> **Contradicted:** this page previously said the interpreter checks whether the next byte is `$FE` after reading the distance. 2.917 has no such check.

## Implementation gap

`resource/` contains no LOGIC decoder. Validating these claims in project code requires implementing — at minimum — a header parser, a control-flow walker that respects the `$FF/$FE/$FD/$FC` opcodes, the AGIDATA.OVL-equivalent argument dispatch table, and the text-section XOR. The Avis Durgan XOR primitive is already in `util/crypto.py` and reused by [resource/objects.py:Objects.extract_inventory_objects]; the same primitive will decrypt LOGIC text messages once a parser exists.
