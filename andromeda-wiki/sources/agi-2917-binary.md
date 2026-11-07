# Source: AGI 2.917 interpreter binary

Static analysis of the interpreter shipped with the local SQ1 copy. It is the top-ranked source for what 2.917 does and says nothing about other versions [WIKI.md §Source-reliability rules]. Everything here comes from reading code, not from running it, except the PICTURE routine, which was also run alone in an x86 emulator with `tools/picture_emu/`; see [[concepts/picture-rendering]]. The whole interpreter has since been run too; see [[sources/agi-2917-runtime]].

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
- The overlays aren't in the Ghidra project, which ends before them at `1000:9800`, so read them with a 16-bit disassembler at their load base. The loader's table at `1964:0004` has 16-byte entries giving segment, name and size in paragraphs: `CGA_GRAF`, `JR_GRAF`, `EGA_GRAF`, `HGC_GRAF` and `VG_GRAF` load at `1000:9740`, `IBM_OBJS` and `HGC_OBJS` at `1000:9CF0`, then `AGIDATA` [AGI 2.917 1000:66FC, 1000:8155]. See [[concepts/ega-palette]] §"Other displays" for the Hercules overlays.
- `AgiGrep` can miss direct memory moves, so confirm "only writer" claims with a raw byte scan. The file offset is `1000:xxxx` + `0x200`.

## Addresses

Code is `1000:xxxx` and data is `DS:xxxx`, where `DS` is segment `19F5`, filled from the first 7,792 bytes of `AGIDATA.OVL` at startup [AGI 2.917 1000:66FC, 1000:672A]. `SS` equals `DS` after `1000:00A3`, so `BP`-based accesses reach data. `var(n)` lives at `DS:0009 + n`.

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
| `1000:00A3` | Moves the stack into `DS`, so `SS` equals `DS` from here on |
| `1000:0078` | Startup after entry; allocates the stack |
| `1000:66FC` | Load an overlay from the table at `1964:0004` |
| `1000:8155` | Choose and load the display overlays |
| `1000:9740`–`1000:9752` | Graphics driver entries; see [[concepts/screen-layers]] |
| `1000:9CF0`, `1000:9CF3`, `1000:9CF6` | Object overlay entries: save background, restore background, draw cel |
| `1000:9CF9`, `1000:9D38` | Save and restore a rectangle of the screen buffer |
| `1000:9D75`, `1000:9E06` | Draw a cel: mirror check, RLE, priority test, `flag(1)`; its search-downwards step |
| `1000:04F5`, `1000:0A06`, `1000:0AAB` | `animate.obj`, `draw` and `erase` cores |
| `1000:067A`, `1000:06D9` | One object's motion dispatch; block box crossing check |
| `1000:0B36`, `1000:1672`, `1000:16B9` | `follow.ego` step; `move.obj` step and finish |
| `1000:3F5A`, `1000:3FA3` | `wander` step, random direction |
| `1000:150A` | Step all active objects, set border variables |
| `1000:16ED`, `1000:172D` | Direction from two points with a threshold |
| `1000:3AE7`, `1000:3BB7`, `1000:3C1B`, `1000:3CCB`, `1000:3D6A` | Set view; set loop and its pointers; set cel and its pointers |
| `1000:4719` | Collision with other objects |
| `1000:48B3` | Cel change by cycle type |
| `1000:55F0` | Baseline control test, automatic priority, `flag(0)`, `flag(3)` |
| `1000:559E`, `1000:555C` | Buffer offset of a pixel; display offset of a pixel |
| `1000:55DA` | Build the y-to-priority table at `DS:1270` |
| `1000:5872`, `1000:594C` | Placement search with a square spiral; bounds and horizon test |
| `1000:57B5` | Mirror a cel in place |
| `1000:7B1F` | Point in block box |
| `1000:0358`, `1000:042F` | Build a sorted draw list; add a node |
| `1000:0307`, `1000:032D` | Restore and free a draw list; free only |
| `1000:045E`, `1000:0488` | Save and draw a list; send a list to the display |
| `1000:691D`, `1000:693E`, `1000:695F`, `1000:6976` | List filters; build the updating and static lists |
| `1000:698D`, `1000:69AA`, `1000:69C7`, `1000:69E4` | Release save areas; drop them without restoring; rebuild them; show both lists |
| `1000:4CBB` | Priority to sort key |
| `1000:569A` | Send an object's old and new rectangle to the display, gated by `DS:120E` |
| `1000:8FD0`, `1000:9043` | Allocate a 16-byte draw record and save area; free one |
| `1000:2D52`, `1000:5707` | `add.to.pic` core; draw a cel into the picture, with margin rectangle |
| `1000:5E13` | `show.obj` core |
| `1000:4AAA`, `1000:4ACF` | `draw.pic` handler and core |
| `1000:4B17`, `1000:4B3B` | `overlay.pic` handler and core |
| `1000:4B82`, `1000:7254` | `show.pic`; `show.pri.screen` |
| `1000:637E`, `1000:6379`, `1000:63AE` | Draw a PICTURE, with and without clearing the buffer; its opcode loop |
| `1000:63CD`–`1000:6597` | PICTURE opcode routines `F0`–`F7`, `F9`, `FA` |
| `1000:65E4`, `1000:5273` | `F8` and flood fill |
| `1000:65F1`, `1000:65FA`, `1000:660D` | Read a PICTURE coordinate pair, x, y |
| `1000:661A`, `1000:51A7`, `1000:51E3` | Line, horizontal, vertical |
| `1000:5231`, `1000:6463`, `1000:518F` | Write a pixel; plot a pen; fill the buffer |
| `1000:5460`, `1000:547E` | Display setup; full update, with the nibble swap for `show.pri.screen` |
| `1000:55BD` | Map a PICTURE color for the display |
| `1000:84A2`, `1000:84C1` | Stack guard check and "Stack blown." |
| `1000:41C6` | Heap and screen buffer setup through DOS |
| `1000:13D6`, `1000:14A0` | Allocate from the heap, fatal if it doesn't fit; free bytes, updating `var(8)` |
| `1000:1430`, `1000:143C` | Read and set next-free |
| `1000:1476`, `1000:1485` | Set the resident mark; release the heap to it |
| `1000:10D0` | Clear the resource lists, keeping LOGIC 0 |
| `1000:110F`, `1000:3979`, `1000:49E8`, `1000:5010` | LOGIC, VIEW, PICTURE, SOUND list search |
| `1000:39F7`, `1000:4A3B` | `load.view` and `load.pic` core |
| `1000:3F0D`, `1000:4BCE` | `discard.view` and `discard.pic` core |
| `1000:6FB5`, `1000:6FEA` | Reset the script buffer, allocating it the first time; write an entry, skipped if `flag(7)` |
| `1000:6F97`, `1000:6FA6` | Script recording off and on |
| `1000:7068`, `1000:7085` | Start script replay; next entry |
| `1000:6755` | Rebuild resources and screen by replaying the script buffer, dispatch table at `1000:684E` |
| `1000:7E19`, `1000:7E28` | Save and jump to a return point (`DS:0617`) |
| `1000:2472`, `1000:2512`, `1000:2753` | `restart.game`, `restore.game`, `save.game` |
| `1000:26B0`, `1000:28C6` | Read and write one length-prefixed save block |
| `1000:851E`, `1000:874D`, `1000:8AD8` | Save and restore dialog; slot selection; read one slot's description, game ID and time |
| `1000:5AAB` | Build a save file name |
| `1000:5BE5`–`1000:5CA3`, `1000:5DAB` | DOS file wrappers; file date and time |
| `1000:1364`, `1000:13A5` | Build the LOGIC scan-offset table; apply one entry |
| `1000:2726` | `$AA`: set the save name |
| `1000:59C1` | BIOS keyboard read, with Scroll Lock detection |
| `1000:8BCA`, `1000:8BE7`, `1000:8CB2`, `1000:8C76` | `trace.on`, open the trace, close it, `trace.info` |
| `1000:8CDC`, `1000:8D02` | Trace entry for an action, for a test |
| `1000:8E62`, `1000:8F70` | Print a traced command's arguments; fetch one |
| `1000:71EE` | `obj.status.v` |
| `1000:930A`, `1000:9247`, `1000:9298` | Run the menu; re-enable all items; enable or disable items by code |
| `1000:9490`, `1000:94E2`, `1000:9509`, `1000:955E`, `1000:95C4` | Menu box open and close; entry highlighted and normal; box position and size |
| `1000:3346`, `1000:33FC`, `1000:3464` | `status`: draw list, move selection, redraw highlight |
| `1000:70F9` | Random generator |
| `1000:4618`, `1000:45F0`, `1000:4529` | Wait for Enter or Esc; poll for them; block for any raw event |
| `1000:5F6E` | Keyboard interrupt handler, installed at `1000:8373` |
| `1000:3726`, `1000:3753`, `1000:37A5` | `cancel.line`, `echo.line`, append previous line |
| `1000:8278`, `1000:82C5` | Open and close `logfile` |
| `1000:7885`, `1000:7939` | `toggle.monitor`; `shake.screen` |
| `1000:62F7` | Read joystick axes |
| `DS:0000` | Stack base, read by the guard check |
| `DS:0002` | Game ID, 7 bytes, start of the saved block |
| `DS:012D`, `DS:0131`–`DS:0137`, `DS:013D` | Horizon; block box; block active |
| `DS:0139` | Control mode: 1 player, 0 program |
| `DS:0141`, `DS:0143`, `DS:16FD`, `DS:16FF`, `DS:1701`, `DS:1703`, `DS:1705` | Script size, count, buffer, write position, replay position, enabled, high-water |
| `DS:0963`, `DS:0965` | Object table start and end |
| `DS:096F`, `DS:0FF2`, `DS:1206`, `DS:1250` | LOGIC, VIEW, PICTURE, SOUND list heads |
| `DS:097D` | LOGIC scan-offset table |
| `DS:0A4D`, `DS:0A4F`, `DS:0A51`, `DS:0A53`, `DS:0A57` | Heap next-free, base, resident mark, top, high-water |
| `DS:0A59`, `DS:0A6B`, `DS:0A7D` | Step x and y by direction; direction by axis classes |
| `DS:08D5`, `DS:08DF` | Loop by direction for 2–3 and for 4 loops |
| `DS:0D07`, `DS:0D0D` | Dialogue flag, set by `open.dialogue` and `print`; format escape character |
| `DS:0E6A`, `DS:05E1`, `DS:1526`, `DS:1707` | `$AA` save name; `push.script` slot; `hold.key` mode; random state |
| `DS:0EAC` | `add.to.pic`'s private object |
| `DS:0FC6`, `DS:0F9C`, `DS:0FF0` | Previous input line, current line, current length |
| `DS:1126`, `DS:1128` | Machine and monitor words behind `var(20)` and `var(26)` |
| `DS:120E` | Set when the picture is on screen; gates object updates |
| `DS:1270` | y-to-priority table, 168 bytes, built at runtime |
| `DS:135F`, `DS:1363`, `DS:1364` | PICTURE enable mask; write values for odd and even rows |
| `DS:1365`, `DS:1367` | Screen buffer segment; display segment |
| `DS:136D`, `DS:136F`, `DS:1371` | PICTURE pointer; display row offset; display-row table |
| `DS:1501`, `DS:1503` | Current draw position, y then x; the target |
| `DS:15CC`, `DS:15EF`, `DS:160F`, `DS:15E4`, `DS:15EE` | PICTURE opcode table; pen and circle masks; pen style; splatter texture |
| `DS:16F5`, `DS:16F9` | Updating and static draw lists |
| `DS:174B` | Nibble-swap request for the full update |
| `DS:1819` | `logfile` handle |
| `DS:1958`, `DS:1C62`, `DS:1C82` | Save directory, description, file name |
| `DS:1D06`, `DS:1D08`, `DS:1CFE`, `DS:1D00` | Trace state: 0 off, 1 stepping, 2 skipping to the next LOGIC; `trace.info` values |
| `DS:1D18`, `DS:1D20`, `DS:1D22`, `DS:1D24`, `DS:1D26` | Menu request, submitted, first menu, current menu, current item |
| `DS:1D2C`, `DS:1D9E` | CGA color table; Hercules dither patterns |

## Informs

[[interpreter/commands]], [[interpreter/event-loop]], [[interpreter/command-semantics]], [[interpreter/variables-and-flags]], [[interpreter/view-objects]], [[interpreter/command-evolution]], [[interpreter/input-parsing]], [[entities/logic]], [[entities/sound]], [[entities/object]], [[entities/words-tok]], [[entities/dir-file]], [[entities/vol-file]], [[concepts/agi-data-types]], [[concepts/offset-encoding]], [[concepts/pcjr-sound-encoding]], [[entities/view]], [[entities/picture]], [[concepts/rle-encoding]], [[concepts/picture-rendering]], [[concepts/screen-layers]], [[concepts/ega-palette]], [[interpreter/control-lines]], [[interpreter/priority-bands]], [[interpreter/memory-layout]], [[interpreter/debug-modes]], [[interpreter/save-restore]].

## Notes

The project dropped its cleanroom claim when it adopted this source. Pages citing it are identifiable by the `[AGI 2.917 …]` citations.
