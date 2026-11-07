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
- Static reading is not proof. Check anything load-bearing on the running interpreter with `tools/agi_emu/`, which runs all of 2.917 under emulation; add a scenario and cite it as `[2.917 runtime: scenario]`. For PICTURE behavior alone, `tools/picture_emu/` runs just the routine.
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
- [x] `interpreter/variables-and-flags`: every reserved slot

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

- [x] Runtime pass: capture traces and screens from the real interpreter for every "Runtime only" item
- [x] Mark out-of-scope v3 pages as unaudited rather than deleting them
- [x] Generate the start-to-finish build document from the wiki: `BUILD_GUIDE.md` at the repo root

## Resume notes

The audit is complete. What remains is under "Open" below. When the wiki changes, keep `BUILD_GUIDE.md` in step: it summarizes the wiki and links to it, and doesn't add claims of its own.

Raw scans use `C:\Users\ebrah\tools\andromeda-re\scan\agiscan.py` (`mem`, `calls`, `dis`) and `ovl.py` for the overlays, run with `uv run --with capstone python -I`. The six agents' 2026-11-01 handoffs are in `C:\Users\ebrah\tools\andromeda-re\audit_2026-11-01\handoffs\`.

### Runtime pass

Done on 2026-11-07 with `tools/agi_emu/`, one scenario per claim, each named in that claim's citation. See `andromeda-wiki/sources/agi-2917-runtime.md` and the log entry of that date. It also corrected one static claim, the size of save block 5.

### Open

These can't be settled with what's local:

- **Analog display output.** Composite CGA artifact colors, and how any monitor shows a palette. The registers and memory each driver writes are recorded.
- **DOS's own behavior.** The result of a divide by zero, which DOS's handler decides, and whether a heap filled exactly to its 16-bit top writes the file's last 16 bytes over `DS:0000`, which depends on how DOS reads across a 64K offset boundary.
- **Menu box geometry in pixels.** Text positions are confirmed; the box itself goes through the driver's fill and wasn't compared pixel by pixel.
- **Other games' debug phrases**, which need games that aren't local.
