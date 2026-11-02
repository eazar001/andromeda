# Source: AGI 2.917 interpreter binary

Static analysis of the interpreter shipped with the local SQ1 copy. It is the top-ranked source for what 2.917 does and says nothing about other versions [WIKI.md §Source-reliability rules]. Everything here comes from reading code, not from running it.

## Identity

- `AGI`: 39,424 bytes, stored encrypted. `AGIDATA.OVL`: 8,192 bytes, plain, with the string `Version 2.917`. Both sizes match the 2.917 row in [[sources/2-8-interpreter]].
- `SQ.COM` is the loader, with the banner `LOADER v3.0`.
- The highest accepted action opcode is `$AD`, matching that row's command count of 173 [AGI 2.917 1000:02CC]. So "173" counts the highest opcode, and the table has 174 entries including `$00`.

## Setup

- The encryption is the rolling XOR described in [[sources/2-5-interpreter]]. Its rotate-with-OR rule, run from block 2, predicts block 307 with no wrong bits. The key was recovered from zero-padded header blocks rather than from the loader.
- The decoded file is `test_games/sq1/AGI.decoded`, which is gitignored and must not be committed or shared.
- REA 6.8.0 refuses DOS MZ targets on Windows, so analysis uses Ghidra 12.1.4 headless with the project and scripts in `C:\Users\ebrah\tools\andromeda-re\`.
- Ghidra cannot see handlers reached only through `AGIDATA.OVL`, so `AgiSeed.java` loads the overlay and seeds them. That raised disassembled bytes from 16,241 to 33,985.
- Ghidra's instruction text prints moves into segment registers with the operands swapped. Trust the raw bytes for those.

## Addresses

Code is `1000:xxxx` and data is `DS:xxxx`, where `DS` is segment `19F5`, filled from `AGIDATA.OVL` at startup [AGI 2.917 1000:66FC]. `var(n)` lives at `DS:0009 + n`.

| Address | Role |
|---|---|
| `1000:66B0` | Program entry |
| `1000:0150` | Main loop |
| `1000:12AE` | Run a LOGIC, loading it if needed |
| `1000:293C` | Bytecode loop, with `if` and `goto` |
| `1000:02C4` | Action dispatcher |
| `1000:07E3` | Test dispatcher |
| `1000:1792` | `new.room` core |
| `1000:357C` | Input event pump |
| `1000:0644` | Per-object motion update |
| `1000:0563` | Per-object screen update |
| `1000:845A` | 60 Hz timer interrupt |
| `1000:7E35` | 20 Hz routine: clock, delay counter, input polling |
| `1000:44A9`, `1000:44F9` | Input queue add and remove |
| `1000:4566` | Applies the `set.key` table to a queued key |
| `1000:3652` | Input line editor |
| `1000:119A` | LOGIC load, including message decryption |
| `1000:21F0` | Message number to text pointer |
| `1000:18AC` | Parse a string into word codes |
| `1000:199D` | Input preprocessing |
| `1000:1A6B` | Vocabulary lookup for one word |
| `1000:095C` | `said` test |
| `1000:744A` | Flag byte and bit mask |
| `1000:516C` | Stop sound |
| `1000:3FE8` | Error routine, setting `var(17)` and `var(18)` |
| `1000:8D44` | Command trace display |
| `DS:061D` | Action table, 4 bytes per entry: handler, argument count, mask |
| `DS:08F5` | Test table, same layout |
| `DS:08E9` | `Avis Durgan` key |

## Informs

[[interpreter/commands]], [[interpreter/event-loop]], [[interpreter/command-semantics]], [[interpreter/variables-and-flags]], [[interpreter/view-objects]], [[interpreter/command-evolution]], [[interpreter/input-parsing]], [[entities/logic]], [[concepts/agi-data-types]].

## Notes

The project dropped its cleanroom claim when it adopted this source. Pages citing it are identifiable by the `[AGI 2.917 …]` citations.
