# Save, Restore and Restart

Everything here is from static reading of 2.917. No save file has been produced or inspected, so the layout below needs a runtime check against a real file.

## Save file layout

A save file is a 31-byte description followed by five length-prefixed blocks. Each length is a 16-bit little-endian word holding the byte count of the data after it [AGI 2.917 1000:28C6, 1000:26B0]. All file calls use near pointers with `DS` = `SS` = `ES` = `19F5`, and no routine on the save or restore path sets them to anything else [AGI 2.917 1000:00A3, 1000:5C27, 1000:5C4A].

| # | Length word | Source | Bytes | What it holds |
|---|---|---|---|---|
| — | none | `DS:1C62` | 31 | Description. All 31 bytes are written, including whatever follows the terminator [AGI 2.917 1000:27FB] |
| 1 | yes | `DS:0002` | 1,505 (`0x5E1`) | Fixed interpreter state, mapped below [AGI 2.917 1000:2816] |
| 2 | yes | pointer at `DS:0963` | object slots × 43 | The object table [AGI 2.917 1000:282F, 1000:100B] |
| 3 | yes | pointer at `DS:0969` | `OBJECT` file size − 3 | Decrypted `OBJECT` data after its 3-byte header, so room numbers go with it [AGI 2.917 1000:2845, 1000:0FD9] |
| 4 | yes | pointer at `DS:16FD` | 2 × script size | The script buffer at full capacity, not just the used part [AGI 2.917 1000:285B] |
| 5 | yes | `DS:097D` | 4 × (loaded LOGICs + 1) | Scan positions of loaded LOGICs: a word for the number and a word for the scan offset from the first bytecode byte, ended by a number of `0xFFFF` whose second word is stale [AGI 2.917 1000:1364, 1000:2873] |

The file offset of the game ID is 33, which is what the slot list reads to reject other games' files [AGI 2.917 1000:8B3D].

SQ1's sizes work out to 18 object slots (774 bytes), 328 bytes of `OBJECT` data, and a script size of 50 entries (100 bytes), since no SQ1 LOGIC calls `script.size` and `DS:0141` starts at 50 [SQ1 data check]. That gives 2,748 + 4 × (loaded LOGICs + 1) bytes.

Block 1 holds these regions, named from the code that uses them:

| Range | Contents |
|---|---|
| `DS:0002`–`0008` | Game ID |
| `DS:0009`–`0108` | Variables |
| `DS:0109`–`0128` | Flags |
| `DS:0129`–`012C` | 32-bit tick count, so a restore rewinds it |
| `DS:012D` | Horizon [AGI 2.917 1000:7DC4] |
| `DS:0131`–`0137`, `DS:013D` | `block` rectangle and its active flag [AGI 2.917 1000:7A8F] |
| `DS:0139` | Player control flag [AGI 2.917 1000:6F7F] |
| `DS:013B` | Written by `draw.pic` and startup, with no reads found [AGI 2.917 1000:4AD7] |
| `DS:0141`, `DS:0143` | Script size, and entries used [AGI 2.917 1000:70B2, 1000:7037] |
| `DS:0145`–`01E0` | `set.key` table, 39 slots of 4 bytes [AGI 2.917 1000:4C6F] |
| `DS:020D`–`05CC` | The 24 strings |
| `DS:05CD`–`05D1` | Text attribute words [AGI 2.917 1000:7721] |
| `DS:05D3`, `DS:05D5`, `DS:05D7` | Input enabled, input row, cursor character [AGI 2.917 1000:3874, 1000:7872, 1000:38CE] |
| `DS:05D9`, `DS:05DB` | Status line shown, status row [AGI 2.917 1000:354C, 1000:787C] |
| `DS:05DD`, `DS:05DF` | `configure.screen` row offset and second value [AGI 2.917 1000:7838, 1000:783E] |
| `DS:05E1` | Mark set by `$AB` and read by `$AC` [AGI 2.917 1000:70C4, 1000:70D6] |

`DS:012F`, `DS:013F` and `DS:01E1`–`020C` have no direct references in the code, so their purpose is unread. The last range does end the `set.key` scan if all 39 slots fill, since that scan stops at a zero word [AGI 2.917 1000:4573].

Not saved: menus, screen buffers, the sound state, the event queue, the controller table, trace state, the save directory and the `$AA` name.

## File names and slots

There are 12 slots. The file name is the directory, a separator if needed, the game ID, `sg.` and the slot number, all lowercased: SQ1's first slot is `sqsg.1` [AGI 2.917 1000:5AAB, DS:1322]. The directory defaults to the current one and persists between saves [AGI 2.917 1000:863E].

The slot list opens each file and reads its description and stored game ID. A missing file or a different game ID counts as an empty slot [AGI 2.917 1000:8AD8]. Saving lists all 12. Restoring lists only the valid ones, and says there are none if the list is empty. The pointer starts on the file with the newest DOS date and time [AGI 2.917 1000:874D, 1000:5DAB].

The description is at most 31 bytes including the terminator. Saving prompts for it, pre-filled from the chosen slot, after the slot is picked [AGI 2.917 1000:85A5, 1000:8A1F, 1000:86CD].

## Named saves with `$AA`

The undocumented `$AA` takes a string number and copies at most 30 characters of that string to `DS:0E6A` [AGI 2.917 1000:2726, 1000:4D21]. A non-empty name changes the dialogs: no directory prompt, confirmation or description prompt [AGI 2.917 1000:8658, 1000:2782, 1000:2548, 1000:859E]. ScummVM calls it `set.simple` [`engines/agi/opcodes.cpp`]; its behavior there wasn't compared. SQ1 doesn't use it [SQ1 data check].

- **Slot choice.** The slot whose description equals the name is used directly. Otherwise a save takes the first empty slot, and a restore silently cancels [AGI 2.917 1000:8887, 1000:88E7, 1000:8923].
- **No empty slot on a save.** The list appears with a "disk is full" message, and the player picks a slot to overwrite [AGI 2.917 1000:892C, DS:187A].
- **The first use.** `DS:190A` starts at 1, so the first save or restore with a name shows the list instead, with a prompt to pick "your name", and clears that word. A restore picked this way copies the chosen description into the name [AGI 2.917 1000:8887, 1000:8933, 1000:8992, 1000:8A24].

## Common behavior of `save.game` and `restore.game`

Both set the paused state, so the clock stops. Both also stop any playing sound, even if the player then cancels [AGI 2.917 1000:275C, 1000:251B, 1000:8535]. While they run, the message formatter's escape character at `DS:0D0D` changes from `\` to `@`, so a backslash in a path prints literally [AGI 2.917 1000:2769, 1000:252F, 1000:1FCB].

## `save.game`

After the dialog and a confirmation showing the description and file name, the handler creates the file, truncating any old one, and writes the description and blocks in order. If a write comes up short, it closes and deletes the file and reports a full disk. If the create fails, it reports that the directory is full or write-protected [AGI 2.917 1000:27C3, 1000:2889, 1000:27DD]. Every outcome continues at the next command, and no flag reports the result [AGI 2.917 1000:28BD].

Block 5 is built just before it's written, and the same table builder runs before `toggle.monitor` rebuilds the screen [AGI 2.917 1000:1364, 1000:78A6].

## `restore.game`

The handler opens the file read-only and seeks past the description. It reads each block using the file's own length word, with no check against the size of the destination [AGI 2.917 1000:25C4, 1000:26B0]. A read failure is fatal: it shows "Error in restoring game. Press ENTER to quit." and exits, whichever key is pressed, because state may already be overwritten [AGI 2.917 1000:2630]. A cancel or a file that won't open just continues at the next command.

The game ID stored in block 1 is only compared by the slot list. The handler itself doesn't check it.

After reading, it does the following in order:

1. Replaces `var(20)`, `var(22)` and `var(26)` with the current machine's values, and sets `flag(11)` on machines other than type 0 [AGI 2.917 1000:2651].
2. Rebuilds resources and the screen, as described below [AGI 2.917 1000:6755].
3. Clears the controller table, sets `flag(12)`, closes the VOL files, and re-enables all menu items in enabled menus [AGI 2.917 1000:267D, 1000:2680, 1000:9247].
4. Returns 0, which ends every running LOGIC. The cycle then reruns LOGIC 0 at once, with `flag(12)` set for that run [AGI 2.917 1000:268D, 1000:02FF, 1000:01BD].

## The rebuild after a restore

The rebuild replays the script buffer, and `toggle.monitor` uses it too [AGI 2.917 1000:6755, 1000:78B8]. It turns off script recording so the replay isn't recorded again, stops sound, and cuts the loaded lists down. The LOGIC list keeps only its first entry, LOGIC 0 [AGI 2.917 1000:10D0, 1000:10F7, 1000:6F97].

Replay then releases the heap and walks the buffer up to the saved entry count. Entries are 2 bytes, a code and an argument, recorded by these commands [AGI 2.917 1000:6FEA, 1000:7085, 1000:6845]:

| Code | Command replayed | Recorded at |
|---|---|---|
| 0 | Load a LOGIC, then restore its scan offset from block 5 | `1000:1190` |
| 1 | Load a VIEW | `1000:3A1E` |
| 2 | Load a PICTURE | `1000:4A58` |
| 3 | Load a SOUND | `1000:50A4` |
| 4 | Draw a PICTURE | `1000:4AF8` |
| 5 | `add.to.pic`: three more entries hold its six stored bytes from `DS:0EA6` | `1000:2D5E` |
| 6 | Discard a PICTURE | `1000:4BF3` |
| 7 | Discard a VIEW | `1000:3F35` |
| 8 | Overlay a PICTURE | `1000:4B60` |

Block 5 is applied only to LOGICs named in the script buffer. LOGIC 0's entry is written but never applied, so its scan position isn't restored unless a script recorded a load of it [AGI 2.917 1000:67C7, 1000:13A5]. A code above 8 is skipped.

The object flags need protecting during replay, so before it the code stores each object's flags word in the position field and its x position in the object-number byte. Objects with bit `0x40` also get bit `0x01` cleared and bit `0x10` set. After replay it reverses this: x returns with a zero high byte, the object number is rewritten from its table position, and the original flags return last [AGI 2.917 1000:677B, 1000:687E, 1000:68F5]. Between those steps, each object whose view is loaded gets its view data reattached. Each that had bit `0x40` is drawn again if it also had bit `0x01`, and has its motion byte at offset `0x29` set to `0xFF` if its motion type is 2 [AGI 2.917 1000:68A4, 1000:68BB]. What those bits mean belongs to [[interpreter/view-objects]].

Recording turns back on once replay ends. Last of all, it cancels the input line and redraws the status and input lines [AGI 2.917 1000:6860, 1000:6904, 1000:6910].

## `restart.game`

The handler stops sound first. Unless `flag(16)` is set, it asks for Enter or Esc. Esc continues at the next command [AGI 2.917 1000:247A, 1000:2480, 1000:2495]. `flag(16)` is above the spec's reserved range, so a game that uses it for its own purposes skips the prompt.

If it goes ahead:

**Reset:**

- All variables and flags, then `var(20)`, `var(22)`, `var(24)` (41), `var(26)`, `flag(5)`, and `flag(11)` on machines other than type 0 [AGI 2.917 1000:106E, 1000:7463, 1000:1080].
- The object table, zeroed with object numbers rewritten [AGI 2.917 1000:102B, 1000:105E].
- `OBJECT` data, reloaded from disk into the same buffer and decrypted again [AGI 2.917 1000:0FB4].
- The heap, down to its mark, and the loaded lists, leaving only LOGIC 0 [AGI 2.917 1000:1485, 1000:10D0].
- The controller table [AGI 2.917 1000:1077].
- Player control turned on, and `block` turned off [AGI 2.917 1000:109B, 1000:10A7].
- The 32-bit tick count, cleared to 0 [AGI 2.917 1000:24DB].
- VOL files closed [AGI 2.917 1000:24BE].
- All menu items in enabled menus re-enabled [AGI 2.917 1000:24F8].

**Kept:**

- `flag(9)`, saved around the reset and set again if it was on [AGI 2.917 1000:24AB, 1000:24CB].
- The strings, the `set.key` table, the horizon, text attributes, screen settings, input and status state, the script size and game ID, none of which the reset touches.
- The trace's names LOGIC, which is reloaded [AGI 2.917 1000:24E7].

Then it sets `flag(6)` and returns 0, which ends every running LOGIC, and LOGIC 0 reruns at once [AGI 2.917 1000:24C1, 1000:2504]. The handler doesn't clear the screen or reset the script buffer's count, leaving that to whatever `new.room` LOGIC 0 runs; `new.room` is what resets the buffer [AGI 2.917 1000:17A0, 1000:6FB5].

## See also

- [[interpreter/memory-layout]] — the script buffer that a restore replays
- [[interpreter/debug-modes]] — the trace, which restore and restart interact with
- [[interpreter/command-semantics]] — other command behavior
- [[sources/agi-2917-binary]] — the binary source and routine map
