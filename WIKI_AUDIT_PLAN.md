# Wiki Audit Plan

Cross-check every claim in `andromeda-wiki/` against the AGI 2.917 interpreter from SQ1, working top-down along what the interpreter executes. The end product is a start-to-finish build document generated from the audited wiki.

## Resume protocol

A fresh agent should:

1. Read this file, `WIKI.md`, and the newest entries in `andromeda-wiki/log.md`. If this file and the log disagree, trust the log.
2. Read `andromeda-wiki/sources/agi-2917-binary.md` for the analysis setup and routine map.
3. Take the first unchecked item under Progress.
4. Compare the listed wiki pages with the binary, then record a verdict per claim using the labels below.
5. Update the pages, `index.md`, and `log.md`, and tick the item.

Do not commit without the user's approval. The user writes all project code; agents write wiki pages and analysis scripts only.

## Verdict labels

- **Confirmed**: the binary does what the wiki says.
- **Refined**: the wiki is right but incomplete or imprecise.
- **Contradicted**: the binary does something else. Keep the spec's claim in a conflict callout.
- **Unread**: the relevant routine has not been read yet. Say so rather than guess.
- **Runtime only**: needs observation of the running interpreter to settle.

## Rules

- Facts apply to 2.917 unless another version is checked. Use ScummVM for cross-version questions.
- Describe behavior in prose. Never paste disassembly or translate routines line by line.
- Pages stay spec-organized for now; the build document gets its own structure later.
- Static reading is not proof. Queue anything load-bearing for the runtime pass. For PICTURE behavior, `tools/picture_emu/` runs the interpreter's own routine, so check new claims there first.
- REA refuses this DOS MZ target on Windows, so analysis uses headless Ghidra. See `andromeda-wiki/sources/agi-2917-binary.md`.
- When agents run in parallel, give each its own git worktree and its own copy of the Ghidra project, because Ghidra locks a project while it's open. Give each agent exclusive pages and have it hand off edits to shared pages, which a coordinator merges. Worktrees don't contain `test_games/`, so point agents at the main checkout's copy.
- Before committing subagent findings, spot-check the riskiest claims against the binary or game data.

## Progress

### Slice 1: command tables and the game cycle

- [x] Set up a permanent analysis project with the command handlers seeded
- [x] `interpreter/commands`: all argument counts and variable positions against `AGIDATA.OVL` and disputed handlers
- [x] `interpreter/event-loop`: main loop order
- [x] `new.room` core and its conflict
- [x] `new.room` unread callees: `516C`, `1485`, `4482`, `6FB5`, `6FA6`, `10D0`, `30D6`, `38D7`, and the `var(2)` reposition cases
- [x] Timer interrupt: the tick rate behind `var(10)` and the clock in `var(11)`–`var(14)`
- [x] Input events: `44F9`, `4566`, key mapping, and joystick routine `612B`

Left for later slices: the direction-key lookup (`46B6`, slice 2 with input), the internals of the resource-list clears under `10D0` and heap release under `1485` (slice 4 with memory), and sound stepping at 60 Hz (`7F55`, slice 4).

### Slice 2: the LOGIC VM

- [x] `entities/logic`: header, entry point, `goto` offset base, message decryption, LOGIC load and discard
- [x] Remaining action handlers, by group. All 174 now have a verdict. See the log entries of 2026-11-01 for each group; what stays Unread or Runtime only is listed under Resume notes
- [x] `interpreter/input-parsing` and `said`
- [ ] `interpreter/variables-and-flags`: every reserved slot

### Slice 3: objects and drawing

- [x] `interpreter/view-objects`: table layout, flag bits, cycling, motion, collision
- [x] `interpreter/control-lines`, `interpreter/priority-bands`
- [x] `entities/view`, `concepts/rle-encoding`
- [x] `entities/picture`, `concepts/picture-rendering`, `concepts/screen-layers`, `concepts/ega-palette`

### Slice 4: sound, data files, and memory

- [x] `entities/sound`, `concepts/pcjr-sound-encoding`: playback timing and voices
- [x] `entities/object`, `entities/words-tok`
- [x] `entities/dir-file`, `entities/vol-file`, `concepts/offset-encoding`
- [x] `interpreter/memory-layout`, resource auto-discard
- [x] `interpreter/debug-modes`, save and restore

### Slice 5: proof and the document

- [ ] Runtime pass: capture traces and screens from the real interpreter for every "Runtime only" item
- [ ] Mark out-of-scope v3 pages as unaudited rather than deleting them
- [ ] Generate the start-to-finish build document from the wiki

## Resume notes

Next item: `interpreter/variables-and-flags`. The handoffs' edits are already on that page, so finish by checking every remaining reserved slot, especially `var(7)`, `var(15)`, `var(19)`, `var(22)`, `flag(8)` and `flag(13)`, and by searching for indirect writes. "Only writer" claims need a raw byte scan as well as `AgiGrep`. Then do the v3 marking, the runtime pass, and the build document, in that order.

The six agents' full handoffs, with per-opcode verdicts and addresses to re-check, are outside the repo in `C:\Users\ebrah\tools\andromeda-re\audit_2026-11-01\handoffs\`. Each log entry from the merge summarizes its unit.

### Runtime pass queue, from slices 2 to 4

- **Objects:** `end.of.loop`'s flag sharing offset `27` with motion parameters (SQ1 LOGICs 53 and 78). `set.loop` accepting a loop equal to the count (LOGIC 71 with VIEW 89). `draw` and `erase` accepting a number equal to the slot count. The placement search's unbounded walk. Step time 0.
- **Drawing:** the control value kept when drawing over priority 0 to 2. `add.to.pic` rewriting `flag(0)`, `flag(1)` and `flag(3)`. The margin rectangle wrapping on narrow cels. `flag(0)` left set after a black first pixel. `get.priority` straight after `position`.
- **Picture and display:** every driver path, since only the PICTURE routine ran in an emulator. Display colors on each monitor type. `show.pri.screen`. Composite CGA. `0xF0` under `-v` on machine type 0. Stack overflow from a fill. Line overflow, pen and splatter behavior in a game that uses them.
- **Misc:** `quit(0)` skipping confirmation. A menu's controller arriving in the cycle it runs. `hold.key`. `shake.screen` effects. Disabled-item dither, menu geometry, `status` selection, the `toggle.monitor` color change.
- **Memory:** heap base and the 16-bit top wrap. Stale records after a mixed discard or a temporary `call`. `new.room` inside a temporary `call`. A larger second `script.size`. `set.menu` over save areas.
- **Save and debug:** a real save file's bytes, with an expected size for SQ1 of 2,748 + 4 × (loaded LOGICs + 1) and the game ID at offset 33. Restore from a file. ALT-D in SQ1. Trace window output. `trace.on` when already on.

### Still unread

`HGC_OBJS.OVL` and the rest of the Hercules driver. Driver entries `9777` (view load hook) and `97D9`. Replay caller `1000:6826`. Joystick routine `635E`. The lookup `46B6`. Restart's sub-clears `396D`, `5004`, `49DC`. Drive checks in `5B15`, `5D39`, `5D76`. A fill with an unmasked color byte such as `0x1F`. Other games' debug phrases.
