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
- Static reading is not proof. Queue anything load-bearing for the runtime pass.

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
- [ ] Remaining action handlers, by group. Done: arithmetic, flags, indirect commands, `call`, `load.logics`, scan start, `parse`, and all 19 tests
- [x] `interpreter/input-parsing` and `said`
- [ ] `interpreter/variables-and-flags`: every reserved slot

### Slice 3: objects and drawing

- [ ] `interpreter/view-objects`: table layout, flag bits, cycling, motion, collision
- [ ] `interpreter/control-lines`, `interpreter/priority-bands`
- [ ] `entities/view`, `concepts/rle-encoding`
- [ ] `entities/picture`, `concepts/picture-rendering`, `concepts/screen-layers`, `concepts/ega-palette`

### Slice 4: sound, data files, and memory

- [ ] `entities/sound`, `concepts/pcjr-sound-encoding`: playback timing and voices
- [ ] `entities/object`, `entities/words-tok`
- [ ] `entities/dir-file`, `entities/vol-file`, `concepts/offset-encoding`
- [ ] `interpreter/memory-layout`, resource auto-discard
- [ ] `interpreter/debug-modes`, save and restore

### Slice 5: proof and the document

- [ ] Runtime pass: capture traces and screens from the real interpreter for every "Runtime only" item
- [ ] Mark out-of-scope v3 pages as unaudited rather than deleting them
- [ ] Generate the start-to-finish build document from the wiki
