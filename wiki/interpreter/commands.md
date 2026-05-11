# AGI Command Catalogue

Complete opcode tables for the AGI LOGIC bytecode interpreter, transcribed from [4-3-Logic.html]. Two opcode spaces:

- **Test commands** (opcodes `$01..$12`) — boolean predicates valid only inside an `if` block (between `$FF` open and `$FF` close). 18 opcodes.
- **Action commands** (opcodes `$00..$B5`) — imperative instructions executed in normal mode. 182 opcodes.

Companion pages:

- [[entities/logic]] — bytecode container format: header layout, `$FC..$FF` control-flow opcodes, AGIDATA.OVL argument-type-byte dispatch, text section, `said` variable-argument encoding.
- [[interpreter/command-evolution]] — the four version-conditional argument-count mutations (`quit`, `print.at`, `print.at.v`, unknown #176).
- [[concepts/agi-data-types]] — argument-type semantics (variable, flag, message, S obj, I obj, string, word, controller).

## Conventions

- All opcodes are 1-byte unsigned values. Hex notation throughout.
- Per-opcode argument count is authoritative; in the spec's HTML tables some rows carry stray cells (e.g. literal "string" in arg-slot 2 of a 1-arg command) that do not represent real arguments and are markup artifacts — ignored in the transcription below.
- `???` denotes an argument type the spec marks as undocumented. Pending cross-check against ScummVM or AGI Studio source.
- `(agidev, unverified)` applies to the entire catalogue at page level: there is no LOGIC decoder in the Python prototype, so every opcode listed here is unvalidated against working code.
- For arg type abbreviations, see [[concepts/agi-data-types]]. Quick legend:
  - `var` — variable index (8-bit)
  - `num` — numeric literal (8-bit)
  - `flag` — flag index (8-bit)
  - `S obj` — screen-object index (runtime VIEW instance)
  - `I obj` — inventory-item index (OBJECT-table entry)
  - `message` — LOGIC-resident message number (8-bit)
  - `string` — string-buffer index (8-bit)
  - `cntrl` — controller code (8-bit)
  - `word` — vocabulary word slot (for `word.to.string`)
  - `said` (test) takes a variable count of 16-bit word codes — see [[entities/logic]] §"The `said` test command".

## Test commands (`$01..$12`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$01` | `equaln` | 2 | var, num |
| `$02` | `equalv` | 2 | var, var |
| `$03` | `lessn` | 2 | var, num |
| `$04` | `lessv` | 2 | var, var |
| `$05` | `greatern` | 2 | var, num |
| `$06` | `greaterv` | 2 | var, var |
| `$07` | `isset` | 1 | flag |
| `$08` | `issetv` | 1 | var |
| `$09` | `has` | 1 | I obj |
| `$0A` | `obj.in.room` | 2 | I obj, var |
| `$0B` | `posn` | 5 | S obj, num, num, num, num |
| `$0C` | `controller` | 1 | cntrl |
| `$0D` | `have.key` | 0 | — |
| `$0E` | `said` | var | 16-bit word codes, count-prefixed (see [[entities/logic]]) |
| `$0F` | `compare.strings` | 2 | string, string |
| `$10` | `obj.in.box` | 5 | S obj, num, num, num, num |
| `$11` | `center.posn` | 5 | S obj, num, num, num, num |
| `$12` | `right.posn` | 5 | S obj, num, num, num, num |

The spec's outer condition range from [4-1-Logic.html §TEST CONDITIONS] is `$00..$12`; `$00` is not used as a test opcode — it doubles as the action-command `return`.

## Action commands (`$00..$B5`)

Organized by opcode index. Section headers below group adjacent opcodes by purpose but the dispatch space is flat — the index is the dispatch key.

### Flow control and arithmetic (`$00..$11`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$00` | `return` | 0 | — (also terminator inside `$FF` if-blocks) |
| `$01` | `increment` | 1 | var |
| `$02` | `decrement` | 1 | var |
| `$03` | `assignn` | 2 | var, num |
| `$04` | `assignv` | 2 | var, var |
| `$05` | `addn` | 2 | var, num |
| `$06` | `addv` | 2 | var, var |
| `$07` | `subn` | 2 | var, num |
| `$08` | `subv` | 2 | var, var |
| `$09` | `lindirectv` | 2 | var, var |
| `$0A` | `rindirect` | 2 | var, var |
| `$0B` | `lindirectn` | 2 | var, num |
| `$0C` | `set` | 1 | flag |
| `$0D` | `reset` | 1 | flag |
| `$0E` | `toggle` | 1 | flag |
| `$0F` | `set.v` | 1 | var |
| `$10` | `reset.v` | 1 | var |
| `$11` | `toggle.v` | 1 | var |

### Rooms, LOGIC, and PICTURE loading (`$12..$1D`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$12` | `new.room` | 1 | num |
| `$13` | `new.room.v` | 1 | var |
| `$14` | `load.logics` | 1 | num |
| `$15` | `load.logics.v` | 1 | var |
| `$16` | `call` | 1 | num |
| `$17` | `call.v` | 1 | var |
| `$18` | `load.pic` | 1 | var |
| `$19` | `draw.pic` | 1 | var |
| `$1A` | `show.pic` | 0 | — |
| `$1B` | `discard.pic` | 1 | var |
| `$1C` | `overlay.pic` | 1 | var |
| `$1D` | `show.pri.screen` | 0 | — |

### Views and screen objects (`$1E..$50`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$1E` | `load.view` | 1 | num |
| `$1F` | `load.view.v` | 1 | var |
| `$20` | `discard.view` | 1 | num |
| `$21` | `animate.obj` | 1 | S obj |
| `$22` | `unanimate.all` | 0 | — |
| `$23` | `draw` | 1 | S obj |
| `$24` | `erase` | 1 | S obj |
| `$25` | `position` | 3 | S obj, num, num |
| `$26` | `position.v` | 3 | S obj, var, var |
| `$27` | `get.posn` | 3 | S obj, var, var |
| `$28` | `reposition` | 3 | S obj, var, var |
| `$29` | `set.view` | 2 | S obj, num |
| `$2A` | `set.view.v` | 2 | S obj, var |
| `$2B` | `set.loop` | 2 | S obj, num |
| `$2C` | `set.loop.v` | 2 | S obj, var |
| `$2D` | `fix.loop` | 1 | S obj |
| `$2E` | `release.loop` | 1 | S obj |
| `$2F` | `set.cel` | 2 | S obj, num |
| `$30` | `set.cel.v` | 2 | S obj, var |
| `$31` | `last.cel` | 2 | S obj, var |
| `$32` | `current.cel` | 2 | S obj, var |
| `$33` | `current.loop` | 2 | S obj, var |
| `$34` | `current.view` | 2 | S obj, var |
| `$35` | `number.of.loops` | 2 | S obj, var |
| `$36` | `set.priority` | 2 | S obj, num |
| `$37` | `set.priority.v` | 2 | S obj, var |
| `$38` | `release.priority` | 1 | S obj |
| `$39` | `get.priority` | 2 | S obj, var |
| `$3A` | `stop.update` | 1 | S obj |
| `$3B` | `start.update` | 1 | S obj |
| `$3C` | `force.update` | 1 | S obj |
| `$3D` | `ignore.horizon` | 1 | S obj |
| `$3E` | `observe.horizon` | 1 | S obj |
| `$3F` | `set.horizon` | 1 | num |
| `$40` | `object.on.water` | 1 | S obj |
| `$41` | `object.on.land` | 1 | S obj |
| `$42` | `object.on.anything` | 1 | S obj |
| `$43` | `ignore.objs` | 1 | S obj |
| `$44` | `observe.objs` | 1 | S obj |
| `$45` | `distance` | 3 | S obj, S obj, var |
| `$46` | `stop.cycling` | 1 | S obj |
| `$47` | `start.cycling` | 1 | S obj |
| `$48` | `normal.cycle` | 1 | S obj |
| `$49` | `end.of.loop` | 2 | S obj, flag |
| `$4A` | `reverse.cycle` | 1 | S obj |
| `$4B` | `reverse.loop` | 2 | S obj, flag |
| `$4C` | `cycle.time` | 2 | S obj, var |
| `$4D` | `stop.motion` | 1 | S obj |
| `$4E` | `start.motion` | 1 | S obj |
| `$4F` | `step.size` | 2 | S obj, var |
| `$50` | `step.time` | 2 | S obj, var |

### Motion and blocks (`$51..$5B`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$51` | `move.obj` | 5 | S obj, num, num, num, flag |
| `$52` | `move.obj.v` | 5 | S obj, var, var, num, flag |
| `$53` | `follow.ego` | 3 | S obj, num, flag |
| `$54` | `wander` | 1 | S obj |
| `$55` | `normal.motion` | 1 | S obj |
| `$56` | `set.dir` | 2 | S obj, var |
| `$57` | `get.dir` | 2 | S obj, var |
| `$58` | `ignore.blocks` | 1 | S obj |
| `$59` | `observe.blocks` | 1 | S obj |
| `$5A` | `block` | 4 | num, num, num, num |
| `$5B` | `unblock` | 0 | — |

### Inventory and rooms (`$5C..$61`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$5C` | `get` | 1 | I obj |
| `$5D` | `get.v` | 1 | var |
| `$5E` | `drop` | 1 | I obj |
| `$5F` | `put` | 2 | I obj, var |
| `$60` | `put.v` | 2 | var, var |
| `$61` | `get.room.v` | 2 | var, var |

### Sound (`$62..$64`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$62` | `load.sound` | 1 | num |
| `$63` | `sound` | 2 | num, flag |
| `$64` | `stop.sound` | 0 | — |

### Print, display, screen (`$65..$71`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$65` | `print` | 1 | message |
| `$66` | `print.v` | 1 | var |
| `$67` | `display` | 3 | num, num, message |
| `$68` | `display.v` | 3 | var, var, var |
| `$69` | `clear.lines` | 3 | num, num, num |
| `$6A` | `text.screen` | 0 | — |
| `$6B` | `graphics` | 0 | — |
| `$6C` | `set.cursor.char` | 1 | message |
| `$6D` | `set.text.attribute` | 2 | num, num |
| `$6E` | `shake.screen` | 1 | num |
| `$6F` | `configure.screen` | 3 | num, num, num |
| `$70` | `status.line.on` | 0 | — |
| `$71` | `status.line.off` | 0 | — |

### Strings, parsing, input (`$72..$78`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$72` | `set.string` | 2 | string, message |
| `$73` | `get.string` | 5 | string, message, num, num, num |
| `$74` | `word.to.string` | 2 | word, string |
| `$75` | `parse` | 1 | string |
| `$76` | `get.num` | 2 | message, var |
| `$77` | `prevent.input` | 0 | — |
| `$78` | `accept.input` | 0 | — |

### Input bindings and PIC composition (`$79..$7B`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$79` | `set.key` | 3 | num, num, cntrl |
| `$7A` | `add.to.pic` | 7 | num, num, num, num, num, num, num |
| `$7B` | `add.to.pic.v` | 7 | var, var, var, var, var, var, var |

### Game lifecycle (`$7C..$80`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$7C` | `status` | 0 | — |
| `$7D` | `save.game` | 0 | — |
| `$7E` | `restore.game` | 0 | — |
| `$7F` | `init.disk` | 0 | — |
| `$80` | `restart.game` | 0 | — |

### Object queries, RNG, control (`$81..$85`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$81` | `show.obj` | 1 | num |
| `$82` | `random` | 3 | num, num, var |
| `$83` | `program.control` | 0 | — |
| `$84` | `player.control` | 0 | — |
| `$85` | `obj.status.v` | 1 | var |

### Quit, debug, misc (`$86..$92`)

| Opcode | Mnemonic | Args | Signature | Version notes |
|--------|----------|------|-----------|---------------|
| `$86` | `quit` | 1 | num | **0 args in interpreter 2.089**; see [[interpreter/command-evolution]] |
| `$87` | `show.mem` | 0 | — | |
| `$88` | `pause` | 0 | — | |
| `$89` | `echo.line` | 0 | — | |
| `$8A` | `cancel.line` | 0 | — | |
| `$8B` | `init.joy` | 0 | — | |
| `$8C` | `toggle.monitor` | 0 | — | |
| `$8D` | `version` | 0 | — | |
| `$8E` | `script.size` | 1 | num | |
| `$8F` | `set.game.id` | 1 | message | Argument is a LOGIC-resident message; resolves the source-syntax half of the 2-5 forward-pointer about `set.game.id` (runtime semantics — what the interpreter does with the ID — remain in [[sources/2-5-interpreter]]). |
| `$90` | `log` | 1 | message | |
| `$91` | `set.scan.start` | 0 | — | Companion to `reset.scan.start`; see [[entities/logic]] §"Entry-point control". |
| `$92` | `reset.scan.start` | 0 | — | See [[entities/logic]] §"Entry-point control". |

### Reposition, trace, print.at (`$93..$98`)

| Opcode | Mnemonic | Args | Signature | Version notes |
|--------|----------|------|-----------|---------------|
| `$93` | `reposition.to` | 3 | S obj, num, num | |
| `$94` | `reposition.to.v` | 3 | S obj, var, var | |
| `$95` | `trace.on` | 0 | — | |
| `$96` | `trace.info` | 3 | num, num, num | |
| `$97` | `print.at` | 4 | message, num, num, num | **3 args in versions before "2.400"** (spec typo, plausibly 2.440); see [[interpreter/command-evolution]] §conflict. |
| `$98` | `print.at.v` | 4 | message, var, var, var | Same version-conditional boundary as `print.at`. |

### Late v2 additions (`$99..$A9`)

| Opcode | Mnemonic | Args | Signature |
|--------|----------|------|-----------|
| `$99` | `discard.view.v` | 1 | var |
| `$9A` | `clear.text.rect` | 5 | num, num, num, num, num |
| `$9B` | `set.upper.left` | 2 | ???, ??? |
| `$9C` | `set.menu` | 1 | message |
| `$9D` | `set.menu.item` | 2 | message, cntrl |
| `$9E` | `submit.menu` | 0 | — |
| `$9F` | `enable.item` | 1 | cntrl |
| `$A0` | `disable.item` | 1 | cntrl |
| `$A1` | `menu.input` | 0 | — |
| `$A2` | `show.obj.v` | 1 | var |
| `$A3` | `open.dialogue` | 0 | — |
| `$A4` | `close.dialogue` | 0 | — |
| `$A5` | `mul.n` | 2 | var, num |
| `$A6` | `mul.v` | 2 | var, var |
| `$A7` | `div.n` | 2 | var, num |
| `$A8` | `div.v` | 2 | var, var |
| `$A9` | `close.window` | 0 | — |

### Unknown commands (`$AA..$B5`) — eleven undocumented

| Opcode | Mnemonic | Args | Signature | Version notes |
|--------|----------|------|-----------|---------------|
| `$AA` | `unknown170` | 1 | ??? | |
| `$AB` | `unknown171` | 0 | — | |
| `$AC` | `unknown172` | 0 | — | |
| `$AD` | `unknown173` | 0 | — | |
| `$AE` | `unknown174` | 1 | ??? | |
| `$AF` | `unknown175` | 1 | ??? | |
| `$B0` | `unknown176` | 0 | — | **1 arg in interpreter 3.002.086**; 0 in all later v3 (see [[interpreter/command-evolution]]). |
| `$B1` | `unknown177` | 1 | ??? | |
| `$B2` | `unknown178` | 0 | — | |
| `$B3` | `unknown179` | 4 | ???, ???, ???, ??? | |
| `$B4` | `unknown180` | 2 | ???, ??? | |
| `$B5` | `unknown181` | 0 | — | |

These eleven opcodes match the [2-8-Interpreter.html] note "the last eleven we do not know the names of". Recovery candidates: ScummVM `engines/agi/op_*.cpp` and AGI Studio source. Tracking under [[sources/2-8-interpreter]] §Notes.

**Note on `$9B set.upper.left`.** [4-4-Logic.html §OTHER COMMANDS] describes the command (under the mnemonic `upper.left`) as a **0-arg state toggle** that switches the collision-detection base-point reference, contradicting 4-3's 2-arg signature with `???` types. See [[interpreter/command-semantics]] §"`set.upper.left` argument-count conflict" for the conflict callout. Provisional reading favors 4-4's 0-arg form.

## Notes

**Argument-type prefixes from 4-2.** [[sources/4-2-logic]] documents source-syntax prefixes (`v`, `f`, `m`, `o`, `i`, `s`, `w`, `c`) that compilers/decoders display. The bytecode itself is untyped — the AGIDATA.OVL bit-encoded type byte (see [[entities/logic]] §"Argument dispatch") tells the interpreter which arguments to dereference vs. consume as immediates.

**Spec table markup artifacts.** The HTML table in 4-3 contains stray cells (literal `string` text) in argument slots beyond the declared count for many rows from `$3E..$71`. These do not appear to encode anything — the declared argument count is correct, and the stray cells are markup noise (possibly an editing accident with rowspan / colspan). All entries in the tables above were validated against the declared argument count, ignoring stray cells.

**Coverage of dangling forward-references.** This page resolves [[interpreter/commands]] — previously forward-referenced from [[interpreter/overview]] §"The LOGIC virtual machine", [[concepts/agi-data-types]] §"Message", and [[interpreter/command-evolution]] §"See also". The remaining dangling forward-refs from overview (`priority-bands`, `control-lines`, `view-objects`, `debug-modes`) are not resolved here — they're runtime-state subsystems, distinct from this opcode dispatch table.

**Semantics not specified.** 4-3 lists opcode signatures only; behavioral semantics (what `animate.obj` actually does to the screen-object table, the exact pixel-priority rules for `set.priority`, how `random` seeds its RNG, etc.) are documented separately in [[interpreter/command-semantics]] from [4-4-Logic.html], which covers high-value items (multi-step procedures, edge cases, conflicts) — for full per-opcode prose, refer directly to `AGI_Specifications/Specifications/4-4-Logic.html`. This page is a dispatch reference, not a behavior reference.
