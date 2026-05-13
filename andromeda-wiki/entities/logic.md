# LOGIC Resource Format

A LOGIC resource holds the bytecode program for a single room. Each room has one associated LOGIC file (numbered 0–255); LOGIC.0 is special and runs continuously, while other LOGICs are invoked from it directly or transitively. The on-disk LOGIC resource has three regions: the universal [[entities/vol-file]] resource header, a 2-byte text-offset prefix, the bytecode section, and the encrypted text-message section.

This page documents the on-disk format. Execution semantics (opcode behavior, VM cycle integration) live under [[interpreter/overview]] and its detail pages.

The Python prototype in `resource/` has no LOGIC decoder, so every bytecode-level claim on this page is `(agidev, unverified)` against working code.

## Format overview

```
+-----------------------------+
| VOL resource header (5 B)   |  See [[entities/vol-file]]: signature 0x1234, VOL number, length
+-----------------------------+
| Text offset (2 B, LE)       |  Byte offset within the LOGIC resource where the text section begins
+-----------------------------+
| Bytecode section            |  Commands, control-flow opcodes, condition codes
+-----------------------------+
| Text section (encrypted)    |  Message count + offset table + Avis-Durgan-XOR'd message bodies
+-----------------------------+
```

[4-1-Logic.html §THE HEADER, §THE TEXT SECTION]

The spec describes this as "a seven-byte header" — the first 5 bytes are the universal VOL resource header documented in [[entities/vol-file]]; only the trailing 2-byte text offset is LOGIC-specific. For brevity below, "the header" refers to the full 7-byte prefix.

**Versioning:** 4-1-Logic specifies v2 only. The chapter notes "the header of each logic script is seven bytes in length for games before 1988. After this date compression seems to have been introduced and the header was subsequently altered" — implying v3 LOGIC headers differ. v3 LOGIC layout is unspecified in this chapter and deferred to later Logic chapters [4-1-Logic.html §THE HEADER].

## Header

| Offset | Size | Field | Format | Source |
|--------|------|-------|--------|--------|
| 0 | 5 | VOL resource header | Universal — see [[entities/vol-file]] | [[entities/vol-file]], [3-2-Files.html §VOL File Format] |
| 5 | 2 | Text offset | Little-endian, unsigned | [4-1-Logic.html §THE HEADER] |

**Text offset** — byte offset from the start of the LOGIC resource (byte 0 of the VOL resource header) at which the text section begins; also marks the end of the bytecode section. Bytecode therefore occupies bytes `7 .. text_offset - 1` and the text section occupies bytes `text_offset .. (5 + payload_length - 1)`.

**Example** [4-1-Logic.html §THE HEADER]: KQ1 Room 2 header is `12 34 01 5F 06 BA 02` — signature `0x1234`, VOL `01`, payload length `0x065F` (1631 bytes including the 2-byte text-offset field and everything after it), text offset `0x02BA` (text section begins 714 bytes into the resource).

## Bytecode section

Begins immediately after the header (byte 7 of the resource) and runs until the text offset. Three byte ranges are dispatched differently [4-1-Logic.html §THE LOGIC CODES]:

| Range | Meaning |
|-------|---------|
| `$00 .. $B5` | AGI commands (e.g. `animate.obj`, `load.pic`, `printf`). `$00` also acts as `return`, terminating the LOGIC and returning to the caller. The upper bound `$B5` (181) is game-dependent — Sierra added commands over time; Manhunter 2 reaches `$B5` [4-1-Logic.html §THE LOGIC CODES, §NEW INFORMATION ON LOGIC INTERPRETATION]. |
| `$00 .. $12` | Test condition codes (e.g. `isset`, `equaln`, `posn`, `said`). Only valid inside an `if` block — between `$FF` opening and `$FF` closing [4-1-Logic.html §TEST CONDITIONS]. |
| `$FC .. $FF` | Control-flow opcodes (see below). |

### Control-flow opcodes

| Code | Mnemonic | Effect |
|------|----------|--------|
| `$FF` | `if` open/close | Switches interpreter mode. Opening `$FF` begins condition evaluation; closing `$FF` is followed by a 2-byte little-endian signed bracket distance — the byte count to skip if the condition is false [4-1-Logic.html §THE LOGIC CODES]. |
| `$FE` | `else` / `goto` | Unconditional 2-byte little-endian signed branch added to the execution pointer. Acts as `else` when it immediately follows the body of an `if`; acts as `goto` when standalone (negative offsets implement loops) [4-1-Logic.html §THE ELSE COMMAND AND MORE ON BRACKETS]. |
| `$FD` | `not` | Inverts the boolean result of the next condition code [4-1-Logic.html §TEST CONDITIONS]. |
| `$FC` | `or` bracket | Used in pairs; conditions between an `$FC ... $FC` pair are ORed. Absence of `$FC` defaults to AND across sequential conditions [4-1-Logic.html §TEST CONDITIONS]. |

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

`set.scan.start()` records the current execution pointer as the entry point for the next invocation of this LOGIC; `reset.scan.start()` reverts the entry point to the start of the bytecode section [4-1-Logic.html §NEW INFORMATION ON LOGIC INTERPRETATION].

## Argument dispatch

Each AGI command and condition code has a fixed argument count (≤ 7) and a per-argument type signature, both stored in a lookup table compiled into the interpreter binary (file `AGIDATA.OVL` on the PC version) rather than in any LOGIC resource [4-1-Logic.html §ARGUMENTS].

The argument-type byte encodes which arguments are variable references vs. literal numbers: bits 7..1 correspond to arguments 1..7 (bit set ⇒ variable, bit clear ⇒ number); bit 0 is unspecified `(agidev, unverified)`. Examples:

- `0x80` — argument 1 is a variable, the rest are numbers.
- `0x60` — arguments 2 and 3 are variables, the rest are numbers.

This is also where the version-conditional argument-count changes documented in [[interpreter/command-evolution]] live (`quit`, `print.at`, `print.at.v`, unknown command #176).

## Text section

The text section is always present (possibly with zero messages). Layout [4-1-Logic.html §THE TEXT SECTION]:

| Offset (relative to text section start) | Size | Content |
|---|---|---|
| 0 | 1 | Number of messages (0–255) |
| 1 | 2 | Little-endian offset (relative to text section start) to the end of the message data |
| 3 | 2 × num_messages | Offset table: one little-endian offset per message, each pointing to that message's start |
| ... | varies | Encrypted message bytes; each message is null-terminated (`0x00`) |

**Encryption.** Every byte of every message body is XOR'd with the repeating 11-byte key `"Avis Durgan"` [4-1-Logic.html §THE TEXT SECTION]. The spec states this directly and shows worked examples of decrypted message bytes. The implication of [2-8-Interpreter.html §AGI VERSION THREE] ("v3 LOGIC files do not encrypt the text messages with 'Avis Durgan' since there is no need to do this because it is compressed anyway") is consistent: v2 encrypts, v3 does not. Note that the key is the same as the OBJECT-file XOR key already used in [resource/objects.py] — the same key, different consumer.

Whether the message-count byte, the end-pointer, and the offset table are also encrypted vs. stored in the clear is not stated explicitly `(agidev, unverified)`. No LOGIC decoder in `resource/` to test against.

**Message access via LOGIC.** The `print` command (and similar) takes a 1-byte message index referring into this table — e.g. `65 08` is `print(message #8)` [4-1-Logic.html §THE TEXT SECTION].

## The `said` test command

`said` (condition code `$0E`) has a variable argument count [4-1-Logic.html §THE 'SAID' TEST COMMAND]:

```
FF 0E 01 1E 01 FF                  ; if (said("marble"))      — 1 word: vocab code 0x011E
FF 0E 02 37 02 73 00 FF            ; if (said("open", "door")) — 2 words: 0x0237, 0x0073
```

The byte immediately following `$0E` is the count of 2-byte little-endian word codes that follow. Word codes are looked up against [[entities/words-tok]] (Group 7). For the preprocessing pipeline that produces the parsed-word vector against which `said` matches, see [[interpreter/input-parsing]] (the AGDS chapter, 2-6, references `4-3-Logic.html` for the matching algorithm — that ingest will likely supersede or extend this summary).

## How the interpreter decodes LOGIC

4-1 includes annotated x86 ASM from Manhunter: San Francisco showing the original interpreter's decode loop [4-1-Logic.html §HOW THE INTERPRETER HANDLES LOGIC CODE]. The high-level state machine:

1. **Normal mode** — read one byte. If `< 0xFC`, dispatch as AGI command via the AGIDATA.OVL table; loop.
2. **`$FF` (if open)** — switch to condition mode. Evaluate condition codes, tracking `not` (`$FD`) and `or` (`$FC`) state, until the closing `$FF`. Read the 2-byte bracket distance; if the conjunction is false, advance the pointer by that distance; otherwise fall through into the if body.
3. **`$FE` (else / goto)** — read 2-byte signed offset and add to the execution pointer unconditionally.
4. **`$00` (return)** — exit this LOGIC, returning to the caller (LOGIC.0 for top-level invocations).

The bracket-distance-inflated-by-3 rule for `if/else` is a consequence of step 2 reading the bracket distance and stepping past it before checking whether the next byte is `$FE`; making the distance 3 longer ensures the false-branch fall-through lands inside the else body, not on the `$FE` byte itself [4-1-Logic.html §THE ELSE COMMAND AND MORE ON BRACKETS].

## Implementation gap

`resource/` contains no LOGIC decoder. Validating the claims on this page requires implementing — at minimum — a header parser, a control-flow walker that respects the `$FF/$FE/$FD/$FC` opcodes, the AGIDATA.OVL-equivalent argument dispatch table, and the text-section XOR. The Avis Durgan XOR primitive is already in `util/crypto.py` and reused by [resource/objects.py:Objects.extract_inventory_objects]; the same primitive will decrypt LOGIC text messages once a parser exists.
