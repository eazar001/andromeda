# Source: AGI 2.917 interpreter binary

Static analysis of the interpreter shipped with the local SQ1 copy. It is the top-ranked source for what 2.917 does and says nothing about other versions [WIKI.md §Source-reliability rules]. Everything here comes from reading code, not from running it.

## Identity

- `AGI`: 39,424 bytes, stored encrypted. `AGIDATA.OVL`: 8,192 bytes, plain, with the string `Version 2.917`. Both sizes match the 2.917 row in [[sources/2-8-interpreter]].
- `SQ.COM` is the loader, with the banner `LOADER v3.0`.
- The highest accepted action opcode is `$AD`, matching that row's command count of 173 [AGI 2.917 1000:02CC]. So "173" counts the highest opcode, and the table has 174 entries including `$00`.

## Setup

- The encryption is the rolling XOR described in [[sources/2-5-interpreter]]. Its rotate-with-OR rule, run from block 2, predicts block 307 with no wrong bits. The key was recovered from zero-padded header blocks rather than from the loader.
- The decoded file is `test_games/sq1/AGI.decoded`, which is gitignored and must not be committed or shared.
- REA 6.8.0 refuses DOS MZ targets on Windows, so analysis uses Ghidra 12.1.4 headless. The scripts and run command are in `tools/ghidra/`, and the project, which contains the decoded interpreter, stays outside the repo in `C:\Users\ebrah\tools\andromeda-re\`.
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
| `1000:1F54`, `1000:1F93` | Message formatter and wrapping |
| `1000:1CE8`, `1000:1D96` | Print a window and wait; build and draw it |
| `1000:1F2B` | Close the window |
| `1000:2390`, `1000:29F6` | Formatted output; output one character |
| `1000:0DA9` | Line editor for `get.string` and `get.num` |
| `1000:770E`, `1000:773C` | Set the text attribute |
| `1000:54C8` | Draw a window box |
| `DS:020D` | String table, 40 bytes per string |
| `DS:0129` | 32-bit tick count at 20 Hz, never paused |
| `1000:00C4`, `1000:40B2` | Command-line switches, machine and monitor detection |
| `1000:0F4E` | Startup loading of directories, `words.tok`, `object`, LOGIC 0 |
| `1000:0FA5` | OBJECT load and object-table setup |
| `1000:3113` | Load a whole file by name |
| `1000:4305` | Load the four directories |
| `1000:434E` | Directory entry check |
| `1000:4371`, `1000:43A5`, `1000:43D9`, `1000:440D` | LOGIC, VIEW, PICTURE, SOUND directory lookup |
| `1000:2E32`, `1000:2E56` | Read a resource from a VOL file, with retries |
| `1000:3080`, `1000:30D6` | Open and close the VOL files |
| `1000:401D` | Disk error prompt |
| `1000:505E` | `load.sound` core |
| `1000:7ECF` | Start a sound |
| `1000:7F55` | 60 Hz sound step |
| `1000:7FFA` | Silence output and finish a sound |
| `1000:802C`, `1000:809B` | Write a tone, write an attenuation |
| `1000:7546`, `1000:759C` | Item number and item variable to entry, with bounds check |
| `1000:3203` | Build the `status` item list |
| `DS:17AE` | Attenuation envelope table |
| `DS:0EFC` | VOL file handles |
| `1000:516C` | Stop sound |
| `1000:3FE8` | Error routine, setting `var(17)` and `var(18)` |
| `1000:8D44` | Command trace display |
| `DS:061D` | Action table, 4 bytes per entry: handler, argument count, mask |
| `DS:08F5` | Test table, same layout |
| `DS:08E9` | `Avis Durgan` key |

## Informs

[[interpreter/commands]], [[interpreter/event-loop]], [[interpreter/command-semantics]], [[interpreter/variables-and-flags]], [[interpreter/view-objects]], [[interpreter/command-evolution]], [[interpreter/input-parsing]], [[entities/logic]], [[entities/sound]], [[entities/object]], [[entities/words-tok]], [[entities/dir-file]], [[entities/vol-file]], [[concepts/agi-data-types]], [[concepts/offset-encoding]], [[concepts/pcjr-sound-encoding]].

## Notes

The project dropped its cleanroom claim when it adopted this source. Pages citing it are identifiable by the `[AGI 2.917 …]` citations.
