# Andromeda — AGI Interpreter Development Plan

A personal working document for building a Python prototype of Sierra's AGI (Adventure Game Interpreter) targeting AGI v2 games (Space Quest 1, King's Quest 1/2, Leisure Suit Larry 1, etc.), prototyped against PySDL2.

---

## 0. Ground rules and caveats

- **Sources.** The AGI 2.917 interpreter from SQ1 is the authority for that version's behavior. Every wiki claim has been audited against it, by reading its code and by running it whole under `tools/agi_emu/` (see `WIKI_AUDIT_PLAN.md`). Where the published specs disagree with it, the interpreter wins. Consult `andromeda-wiki/` first; the specs and the references below matter only where the wiki is silent, or for versions other than 2.917.
- **Build companion.** `BUILD_GUIDE.md` is the audited, stage-by-stage reference for building against 2.917: the rules, the traps, and the wiki pages behind each stage. This plan tracks milestones and status; when a per-milestone note here disagrees with the guide or the wiki, the guide and the wiki win.
- **Oracle.** `tools/agi_emu/` runs the real interpreter on the real game files with test resources substituted, and `tools/picture_emu/` runs its PICTURE routine alone. Use them to check a milestone's output against the interpreter's.
- **Scope target.** First playable milestone is **Space Quest 1 room 1** (outside the Arcada): PIC loaded, ego drawn, input parsed, basic `said()` dialogue works. Everything else is scaffolding toward that.
- **Language/stack.** Python 3.14, PySDL2 (already a dep). Avoid heavy dependencies — one goal is to keep the code pedagogical. This is the prototype: a Rust rewrite is planned, but its design and timing aren't covered in this plan yet.
- **AGI v2 only for now.** v3 adds LZW compression and a handful of opcodes; defer until v2 is playable.

### Other references

For versions other than 2.917, and anything the wiki doesn't cover. agidev.com has known byte-level errors; prefer ScummVM and NAGI where they disagree.

- ScummVM AGI specs: http://wiki.scummvm.org/index.php/AGI and `.../AGI/Specifications/*`
- AGI wiki: http://agiwiki.sierrahelp.com/
- Peter Kelly, "AGI Specifications" chapters — commonly mirrored at http://www.agidev.com/articles/agispec/
- NAGI interpreter (Nick Sonneveld, cleanroom reimplementation): https://github.com/sonneveld/nagi
- ScummVM source tree (secondary reference): `engines/agi/` in https://github.com/scummvm/scummvm — especially `cycle.cpp`, `op_cmd.cpp`, `picture.cpp`, `sound_pcjr.cpp`, `words.cpp`

---

## 1. Current state of the repo

What exists today (November 2026):

| Module | Status | Notes |
|---|---|---|
| `resource/directory.py` | ✅ Working | Moved from `util/dir.py`. Parses `*DIR` files to one `(vol, offset)` pair per slot, so `entries[n]` is resource `n`. Absent slots (`vol == 0xF`, any offset) stay in place; callers skip them, as `main.py` does. Slot and absent counts match the wiki on all four SQ1 directories. |
| `resource/volume.py` | ✅ Working | `VolumeReader(path)` holds an open file handle. `read_resource(offset)` returns `(ResourceHeader, payload_bytes)` without re-opening the VOL file. |
| `util/byte.py` | ✅ Working | `nibble(byte, 'hi'/'lo')` helper. `cel_mirror()` removed — mirror flag and loop index are now extracted inline in `resource/view.py`. |
| `resource/header.py` | ✅ Working | `ResourceHeader` dataclass with `@classmethod parse(f, offset)`. Reads the 5-byte VOL chunk header: 2-byte signature (`0x1234`, big-endian), 1-byte vol number, 2-byte LE resource length. Verified against all 462 SQ1 resources. The signature is parsed but not validated. |
| `resource/view.py` | ✅ Working | Moved from `view/vol.py`. `get_view_data(reader, offset)` takes a `VolumeReader`, parses via `BytesIO`, and returns a structured `View(desc_offset, loops=[Loop(loop_idx, cels=[Cel(...)])])` dataclass. Mirror flag and source loop index decoded from cel header nibble. |
| `gfx/view_render.py` | ✅ Working | `composite_cel(screen, loop_idx, cel)` writes a cel into a screen buffer, handling transparency and mirroring. Always draws at the top-left corner, with no x/y or priority yet (M4). All 1,652 SQ1 cels verified. |
| `resource/objects.py` | ✅ Working | Moved from `object/Object.py`. Decrypts `OBJECT` file via `util/crypto.py:xor_cycle`, extracts `(index, name, room)` for every 3-byte entry. Each name is resolved through its entry's pointer, so SQ1 returns all 25 items correctly numbered, with item 17 reading the `?` placeholder. Still always decrypts, though pre-2.411 files are unencrypted. |
| `util/crypto.py` | ✅ Working | `xor_cycle(key_string, file)` — standalone XOR decryption helper. Used by `objects.py`; will also be reused for LOGIC message decryption. |
| `main.py` | ✅ Working | Test harness: plays every VIEW cel through `composite_cel`, then prints the directory listings. Closing the window plays out the current view first. |

**Confirmed facts from the existing code worth preserving:**

- VOL resource header is 5 bytes (two-byte signature `0x12 0x34` + vol# + LE length word). The same 5-byte prefix applies to PIC, LOGIC, SOUND.
- The DIR triplet encoding is: `nibble_hi(b0)` = vol number, `(nibble_lo(b0) << 16) | (b1 << 8) | b2` = byte offset into that VOL.
- XOR decryption key for obfuscated sections is the ASCII string `"Avis Durgan"` (11 bytes, repeating).

**Gaps to be aware of before writing new code:**

- No resource manager exists. `VolumeReader` keeps a file handle open, but nothing caches resources or honors sticky (game-global) vs. per-room lifetimes (see §3).
- The VIEW loader returns only `desc_offset`, not the description text (20 SQ1 views have one). A view with no loops crashes it, and a loop with no cels shifts later loops down a position; SQ1 has neither.
---

## 2. Architecture overview

AGI is, at its core, four things glued together:

1. **A resource container** — `*DIR` index files + `VOL.n` volume files, with PIC/VIEW/LOGIC/SOUND bodies after a 5-byte header. Plus the top-level `OBJECT` and `WORDS.TOK` files. This layer is already partially built.
2. **A bytecode VM** — LOGIC resources are a stack-less bytecode with ~175 action opcodes, ~18 test opcodes, and an `if`/`else`/`goto` structure built from three control bytes (`0xFF`, `0xFE`, `0xFD`/`0xFC`). The VM owns 256 flags, 256 variables, ~12 strings, a sprite table, and the two screens. LOGIC is the game's "scripting language."
3. **A rendering and animation pipeline** — two 160×168 4-bit screens (visual + priority), priority values 4–15 for Z-sorting, control values 0–3 for walkability/triggers, a ~16-slot screen-object table with auto-movers and auto-cyclers. Composited with a 40×25 text overlay and blitted to a 320×200 host window (X is doubled).
4. **A fixed-step main cycle** — nominally 20 Hz, throttled by reserved variable `v10`. Each cycle: poll input → run parser if ENTER → call LOGIC 0 → update objects → re-blit. `new.room(n)` runs the room-change procedure and re-enters LOGIC 0 with the "new room" flag (f5) set.

The subsystems connect like this:

```
                       ┌────────────────────┐
                       │     VOL files      │
                       └──────────┬─────────┘
                                  │
                     ┌────────────┴──────────────┐
                     │     ResourceManager       │
                     │  (open vols, cache, LRU,  │
                     │   sticky vs per-room)     │
                     └─┬────┬───────────┬───┬────┘
                       │    │           │   │
               ┌───────┘    │           │   └──────────┐
               ▼            ▼           ▼              ▼
           PicDecoder   ViewDecoder  LogicDecoder  SoundDecoder
               │            │            │              │
               ▼            ▼            ▼              ▼
     ┌─────────────┐   ┌─────────┐  ┌──────────┐  ┌──────────┐
     │ visual+prio │   │  cels   │  │ bytecode │  │ 4-ch mix │
     │   buffers   │   │ (RLE)   │  │   + msgs │  │          │
     └──────┬──────┘   └────┬────┘  └─────┬────┘  └─────┬────┘
            │               │             │             │
            └───────┬───────┴─────┬───────┘             │
                    ▼             ▼                     ▼
              ┌──────────────────────────┐      ┌──────────┐
              │    Interpreter           │      │SDL Audio │
              │  flags/vars/strings      │      └──────────┘
              │ LOGIC VM + cmd dispatch  │
              │  screen object table     │
              │     main cycle           │
              └─────────┬────────────────┘
                        │
                        ▼
                 ┌──────────────┐     ┌────────────┐
                 │ Compositor   │────▶│ SDL Video  │
                 │  + text ovl  │     └────────────┘
                 └──────────────┘
                        ▲
                        │
                 ┌──────┴──────┐
                 │    Parser   │◀── WORDS.TOK
                 │  input line │◀── SDL keyboard
                 └─────────────┘
```

---

## 3. Proposed module layout

One reasonable expansion of the current tree (not prescriptive — adapt as you go):

```
andromeda/
├── main.py
├── resource/
│   ├── __init__.py
│   ├── header.py          # 5-byte VOL resource header parsing
│   ├── directory.py       # (moved from util/dir.py)
│   ├── volume.py          # VolumeReader: opens VOL.n, random-access
│   ├── manager.py         # ResourceManager: sticky/per-room lifetimes
│   ├── pic.py             # PIC opcode stream decoder
│   ├── view.py            # VIEW loop/cel decoder (rework from view/vol.py)
│   ├── logic.py           # LOGIC bytecode + message section decoder
│   ├── sound.py           # SOUND channel-stream decoder
│   ├── words.py           # WORDS.TOK decoder
│   └── objects.py         # OBJECT file decoder (moved from object/Object.py)
├── runtime/
│   ├── __init__.py
│   ├── state.py           # GameState: flags[256], vars[256], strings[12]
│   ├── reserved.py        # constants for reserved vars/flags
│   ├── interp.py          # LOGIC bytecode interpreter (decoder + executor)
│   ├── commands.py        # agi command table + test command table
│   ├── sprites.py         # ScreenObject table + mover + cycler
│   ├── parser.py          # longest-match tokenizer + said() state
│   ├── cycle.py           # main game loop + new-room handling
│   └── errors.py          # NewRoomException, InterpreterError, ...
├── gfx/
│   ├── __init__.py
│   ├── screens.py         # visual (160x168x4bit) + priority (same)
│   ├── pic_render.py      # executes PIC ops into screens
│   ├── view_render.py     # composites cels into visual screen
│   ├── text_overlay.py    # 40x25 text layer, windows, status line, input line
│   ├── palette.py         # 16-color EGA palette
│   └── blit.py            # SDL2 output: 2x X-double, palette convert, present
├── audio/
│   ├── __init__.py
│   ├── sn76489.py         # square + noise synth, attenuation table
│   └── player.py          # 4-channel mixer + SDL2 audio callback
├── io/
│   ├── __init__.py
│   ├── input.py           # SDL2 key → input line + controllers + v19
│   └── save.py            # save/restore serialization
├── util/
│   └── byte.py            # keep as-is
├── CLAUDE.md
├── DEVELOPMENT_PLAN.md
├── README.md
└── pyproject.toml
```

Migrate incrementally — don't do a big-bang rename. Each milestone below mentions which files change.

---

## 4. Phased milestones

### M0 — Foundation cleanup

**Goal:** Clean resource-layer seams so the rest of the work has a solid base.

- [x] Extract a `resource/header.py` that parses the 5-byte VOL resource header (signature check, volume number, LE length). Implemented as `ResourceHeader` dataclass with `@classmethod parse(f, offset)`. Reuse from PIC/LOGIC/SOUND. **Signature check not yet implemented.**
- [x] Add `resource/volume.py:VolumeReader(path)` that holds an open file handle and exposes `read_resource(offset) -> (ResourceHeader, bytes)`. Returns the parsed header and payload separately for clean caller access.
- [x] Move `util/dir.py` → `resource/directory.py`; kept the existing API.
- [x] Move `object/Object.py` → `resource/objects.py`; extracted `decrypt_file()` into `util/crypto.py:xor_cycle(key_string, file)`. `objects.py` now imports from there. Same helper will be reused for LOGIC message decryption.
- [x] Rework `view/vol.py` → `resource/view.py`: returns a structured `View(desc_offset, loops=[Loop(loop_idx, cels=[Cel(width, height, mirror, non_mirror_idx, alpha, cel_data)])])` dataclass. RLE decoding inline in `get_cel_data`.
- [x] Keep `view/render.py` → `gfx/view_render.py`, but now it takes `Cel` objects and composites into a `VisualScreen` buffer (not directly into the SDL renderer — see M1). `composite_cel(screen, loop_idx, cel)` writes color indices into `VisualScreen`; EGA palette extracted to `gfx/palette.py`. `draw_cel_data` has since been removed.

**Exit criteria:** `uv run python -m main` still prints DIR listings and can still render a test VIEW cel via the old harness path, now going through the new module names.

### M1 — PIC decoder and dual-screen compositor

**Goal:** Load and render a real room background (both visual and priority screens).

- [x] `gfx/screens.py`: `VisualScreen` (160×168, uint8 color index) and `PriorityScreen` (160×168, uint8 priority/control value). Clear visual to **15** (white) and priority to **4** (lowest valid band) on reset — this is critical for flood fill to work.
- [x] `gfx/palette.py`: the 16-color EGA palette (already in `gfx/view_render.py`). Add a helper that converts a `VisualScreen` buffer to a 320×200 RGBA SDL texture with horizontal doubling. Implemented as `visual_screen_buffer_to_texture(screen, renderer)` in `gfx/palette.py`; renders at 320×168 (play area only, X-doubled from 160).
- [ ] `resource/pic.py`: `decode_pic(payload: bytes) -> list[PicOp]`. Each `PicOp` is a structured command with its arguments resolved (colors, pen settings, absolute points), never a raw byte; the renderer shouldn't need to look at bytes again. Keep one command type per opcode so a printed op list maps one-to-one onto the bytes. PIC is a stream of opcodes `0xF0`–`0xFF`. `0xF1` and `0xF3` take no arguments; `0xF0`, `0xF2` and `0xF9` take exactly one byte, unchecked, so even `0xFF` is taken as the argument; the rest read arguments until the next byte `>= 0xF0`. Opcodes to implement:
  - `0xF0` set picture color + enable visual, `0xF1` disable visual
  - `0xF2` set priority color + enable priority, `0xF3` disable priority
  - `0xF4` Y-corner (alternating vert/horiz), `0xF5` X-corner
  - `0xF6` absolute line (polyline of (x,y) points)
  - `0xF7` relative short line (bit 7 = Δx sign, bits 6-4 = |Δx|, bit 3 = Δy sign, bits 2-0 = |Δy|)
  - `0xF8` flood fill (list of seed points)
  - `0xF9` set pen (bit 5 texture 0=solid/1=splatter, bit 4 shape 0=circle/1=square, bits 0-2 size 0-7)
  - `0xFA` plot pen (solid: `(x,y)` per point; splatter: `(pattern, x, y)` per point)
  - `0xFF` end of picture. Nothing checks the resource length, so stopping at the payload end is a safety net the original lacks.
  - `0xFB`–`0xFE`, and any byte below `0xF0` outside a command, are skipped silently up to the next valid opcode. They are not errors.
- [ ] Decoder rules (see `andromeda-wiki/entities/picture.md`):
  - Coordinates: X bytes `0xA0..0xEF` clamp to 159; Y bytes `0xA8..0xEF` clamp to 167.
  - A half-read group is dropped, so a lone `x` before the next opcode draws nothing.
  - `0xF7` steps add in 8 bits and then clamp: past 159 or 167 becomes the edge, but stepping left of 0 or above 0 wraps to the far edge. Δx = −7 can't be encoded, since that byte would be `>= 0xF0`.
  - Each picture starts with both layers disabled and pen `0` (solid circle, size 0), so `0xFA` reads pairs until an `0xF9` selects splatter. State does not carry over between pictures.
- [ ] `gfx/pic_render.py`: executes a decoded PIC op list into a `VisualScreen` + `PriorityScreen` pair. Implement:
  - Line drawing — use the integer rule in `andromeda-wiki/concepts/picture-rendering.md`, not textbook Bresenham. A different method can put pixels elsewhere and move fill boundaries, and the rule's 8-bit error terms make very long diagonals stop short; the next segment starts where the line actually ended.
  - Flood fill: **iterative** (stack-based), not recursive. The result is the 4-connected region of qualifying pixels around the seed, and the seed must itself qualify. Fill rules:
    - Visual enabled only: no fill if the visual color is 15; otherwise fill pixels currently == 15 (white).
    - Priority enabled only: no fill if the priority color is 4; otherwise fill cells currently == 4.
    - Both enabled: **visual drives** — no fill if the visual color is 15; otherwise flood the visual on the "== 15" rule and write priority at every filled pixel, whatever it was. Do **not** apply the priority-only rule.
    - Both disabled: consume coordinates, no-op.
  - Splatter pen: 2.917 generates the pattern with an 8-bit shift register (`andromeda-wiki/concepts/picture-rendering.md`). The spec's tables are an equivalent precomputed form: a 32-byte, 255-bit pattern that wraps from bit 254 to bit 0, and a 120-entry offset table (`andromeda-wiki/entities/picture.md`). SQ1 has no `0xF9`, so this isn't needed for the first playable.
  - Pens: all eight circle sizes (0–7) come from the mask table in `andromeda-wiki/concepts/picture-rendering.md` — don't rasterize from `math.hypot`. Every pen is `size + 1` columns wide and `2·size + 1` rows tall in the 160-wide frame, not square.
- [ ] Main-file smoke test: load `PICDIR` → pick pic 1 → decode → render both screens → blit visual to an SDL window.

**Gotchas called out by research:**
- Variable parameter runs end when the next byte is `>= 0xF0`, not when a count is exhausted. Rewind one byte and re-dispatch. The one-byte arguments of `0xF0`, `0xF2` and `0xF9` are exempt.
- Keep PIC rendering in logical 160×168 space; X-doubling happens only at blit time.
- Control cells (priority values 0–3) overlay the priority screen. When the sprite system later needs "true" priority under a control cell, search downward (increasing y) in the priority buffer until a value ≥ 4 is found.

**Exit criteria:** Room 1 of SQ1 renders recognizably on screen. Priority screen can be toggled via a debug key.

### M2 — LOGIC decoder (parse, don't execute)

**Goal:** Given a LOGIC resource body, produce a structured IR (bytecode instructions + decrypted messages) without running it.

- [ ] `resource/logic.py`: `decode_logic(payload: bytes) -> Logic`:
  - Header: `messages_offset = u16 LE` at byte 0. Bytecode is `payload[2 : 2 + messages_offset]`; message section starts at `2 + messages_offset`.
  - Message section: `num_messages (u8)`, `end_offset (u16 LE)`, then `num_messages` u16 LE pointers to strings. String bodies are null-terminated and XOR-encrypted with `"Avis Durgan"`. Offset 0 in the pointer table = missing message. Messages are 1-indexed. **Pointers and `end_offset` are relative to the byte after `num_messages`**, not the section start.
  - XOR key range is **only** the string body area (from the first string onward up to `end_offset`), not the pointer table. Getting this bound off by one scrambles every message.
- [ ] `runtime/commands.py`: the **opcode arity table**. This is the single most important piece of data in the whole project — one wrong arity and every instruction after it is garbage. Sources:
  - `andromeda-wiki/interpreter/commands.md` (from spec chapter 4-3). Argument counts for every 2.917 test command and action commands `$00..$AD` match the interpreter's own tables, and all 101 SQ1 LOGICs decode without desyncs.
  - Opcodes `$AE..$B5` don't exist in 2.917; their counts, and every other version's, are still unverified.
  - Store as a `dict[int, CommandSpec]` where `CommandSpec` is `(name, num_args, arg_kinds)`. `arg_kinds` is metadata like `"var" | "flag" | "obj" | "msg" | "num" | "str"` for prettier disassembly later.
- [ ] `runtime/interp.py:disassemble(logic: Logic) -> str`: walk the bytecode, emit human-readable assembly. Handles the three special control bytes:
  - `0x00` = return
  - `0xFF` = `if (` ... `)` — inside, AND is implicit, `0xFC` opens/closes an OR group, `0xFD` is unary NOT on the next test term. After the closing `0xFF` comes a **signed int16 LE** displacement (jump-if-false).
  - `0xFE` = unconditional goto / else — followed by signed int16 LE displacement.
- [ ] **`said` is the one variable-arity test command.** Its operands are: 1 byte `count`, then `count` u16 LE word-group numbers. Every other test command is fixed arity.
- [ ] Write a pretty-printer for a Logic and run it on LOGIC 0 and LOGIC 1 of SQ1 to sanity-check the arity table. You'll know immediately if anything's wrong — disassembly desyncs into garbage.

**Exit criteria:** Disassemble SQ1's LOGIC 0 and LOGIC 1 end-to-end with no exceptions, and the message section round-trips to readable English.

### M3 — LOGIC interpreter (execute)

**Goal:** Actually run LOGIC code, one logic at a time, with mocked subsystems where needed.

- [ ] `runtime/state.py:GameState`:
  - `flags: bytearray` (256 bits, store as `bytearray(256)` 1 byte each for simplicity)
  - `vars: bytearray` (256 uint8)
  - `strings: list[str]` (start with 24 empty slots)
  - Setter hooks: writes to reserved indices (e.g., `v16` = ego view, `v10` = cycle delay) should route through property setters so side effects fire. Don't scatter side-effect checks at call sites.
- [ ] `runtime/reserved.py`: constants for the reserved vars/flags. Build the table from `andromeda-wiki/interpreter/variables-and-flags.md`; don't hardcode raw indices in command handlers. Minimum set to start with:
  - `V_CUR_ROOM = 0, V_PREV_ROOM = 1, V_EGO_BORDER = 2, V_SCORE = 3, V_OBJ_BORDER = 5, V_EGO_DIR = 6, V_MAX_SCORE = 7, V_UNKNOWN_WORD = 9, V_CYCLE_DELAY = 10, V_SECONDS = 11, V_MINUTES = 12, V_HOURS = 13, V_DAYS = 14, V_EGO_VIEW = 16, V_LAST_KEY = 19, V_WINDOW_TIMER = 21, V_MAX_INPUT_LEN = 24`
  - `F_ON_WATER = 0, F_EGO_INVISIBLE = 1, F_HAS_INPUT = 2, F_EGO_SIGNAL = 3, F_SAID_MATCHED = 4, F_NEW_ROOM = 5, F_RESTART = 6, F_SCRIPT_BLOCKED = 7, F_JOY_SENSITIVITY = 8, F_SOUND_ON = 9, F_DEBUGGER = 10, F_LOGIC0_FIRST = 11, F_RESTORE = 12, F_INVENTORY_SELECT = 13, F_MENU_ENABLED = 14, F_PRINT_MODE = 15`
  - These flags now follow spec chapter 2-2. `V_MAX_INPUT_LEN = 24` is unconfirmed: the spec lists `var(24)` only as `29h`.
- [ ] `runtime/interp.py:Interpreter`:
  - `run_logic(logic_num: int)` — loads logic from cache, sets up a PC at `bytecode_start`, executes opcodes via a dispatch dict `{opcode_byte: handler}`.
  - The `if` / `else` / `goto` parser is the trickiest piece. Structure:
    ```
    parse_if(): consume 0xFF; collect test terms until next 0xFF;
                read signed int16 displacement; return (ast, false_skip_bytes)
    ```
    Each test term is either: `0xFD next_term` (NOT), or `0xFC ... 0xFC` (OR group), or a test opcode + fixed operands (or `said` with its variable-length list).
  - Cache decoded instruction streams per logic — don't re-parse bytes every cycle. A simple "compile once on first load" pass suffices.
  - **`new.room(n)` must abort immediately.** Easiest Python implementation: `class NewRoomException(Exception): pass`, raise it from the handler, catch it at the top of the main cycle. Do not try to "return normally" — any code after `new.room` in the calling logic must not run. (Sources disagree on this timing; see the conflict in `andromeda-wiki/interpreter/event-loop.md`. Treat immediate abort as provisional.)
- [ ] Implement agi commands in groups, starting with the ones needed for a blank-screen boot:
  1. Control flow: `return`, `call`, `new.room`, `new.room.v`
  2. State: `set`, `reset`, `toggle`, `set.v`, `reset.v`, `toggle.v`, `assignn`, `assignv`, `addn`, `addv`, `subn`, `subv`, `lindirectn`, `lindirectv`
  3. Resource loading: `load.logic`, `load.view`, `load.pic`, `load.sound`, `discard.pic`, `discard.view` (mocked — the resource manager from M0 handles the real work)
  4. I/O stubs: `print`, `print.v`, `display`, `get.num` (print to stdout for now)
- [ ] Implement the important test commands: `equaln`, `equalv`, `lessn`, `lessv`, `greatern`, `greaterv`, `isset`, `issetv`, `has`, `obj.in.room`, `posn`, `controller`, `have.key`, `compare.strings`, `said` (the last one stubs to "always false" until M6).
- [ ] Write a test harness: load LOGIC 0 of SQ1, run it, see what happens. Expected behavior: it should dispatch to LOGIC 1 via `call(1)`, which is the intro. Lots of unimplemented-command stubs will fire; that's fine — log them and return false/zero.

**Gotchas:**
- `if`-displacement is signed (backward jumps are common for busy-waits).
- `call` is real subroutine — push PC, run the called logic to its `return`, restore PC.
- Message numbers are 1-based; `print(0)` is invalid.
- The XOR key "Avis Durgan" applies only to strings, not to the pointer table or bytecode.
- v3 LOGICs may have pre-XOR'd messages *before* LZW compression; for v2 always XOR after decode. You're only targeting v2 at this stage.

**Exit criteria:** LOGIC 0 of SQ1 runs one full cycle without crashing the interpreter. All invoked opcodes are either implemented or cleanly stubbed + logged.

### M4 — Screen objects and animation

**Goal:** Draw ego on screen and make it move when the arrow keys are pressed.

- [ ] `runtime/sprites.py:ScreenObject` dataclass with: `x, y, prev_x, prev_y, view_num, loop, cel, direction, step_size, step_time, step_count, cycle_time, cycle_count, motion_type, cycle_type, priority, flags` (drawn/update/animate/ignore_blocks/ignore_horizon/ignore_objs/on_water/on_land/fixed_loop/fixed_priority/cycle/motion).
- [ ] `ScreenObjectTable` — fixed-size array of ~16 slots. Slot 0 is ego.
- [ ] Mover: per-tick, for each active object, compute a candidate step from `direction × step_size`, check priority/control pixels along the base-line (1 px under the cel) for obstacles, commit or stop.
- [ ] Auto-cycler: every `cycle_time` ticks, advance `cel` per `cycle_type` (normal.cycle, end.of.loop, reverse.cycle, reverse.loop).
- [ ] Direction-driven loop selection: for 4-loop views, loop = direction-derived (north=3, east=0, south=2, west=1 in Sierra's convention — verify); for 2-loop views, loop = east/west only.
- [ ] Draw order: **by priority band, low-to-high** for erase, high-to-low for redraw. Mixing the two causes flicker.
- [ ] Priority computation: if object has no explicit `set.priority`, compute from y-coordinate via the 15-band priority table (`y < 48` is band 4, then a new band every 12 pixels up to band 14; see `andromeda-wiki/interpreter/priority-bands.md`).
- [ ] Implement the agi commands `animate.obj`, `unanimate.all`, `set.view`, `set.loop`, `set.cel`, `position`, `position.v`, `draw`, `erase`, `set.priority`, `release.priority`, `start.cycling`, `stop.cycling`, `start.motion`, `stop.motion`, `step.size`, `step.time`, `cycle.time`, `set.dir`, `get.dir`.
- [ ] Mount ego (object 0) with the default SQ1 view and verify it renders in the correct spot. Hook arrow keys temporarily to write `v6` (direction) and watch ego walk.

**Exit criteria:** Ego walks around room 1 of SQ1, correctly clipped by priority bands and blocked by control cell 0 (obstacles).

### M5 — Main cycle, wired

**Goal:** Close the loop between LOGIC, objects, rendering, and a real game clock.

- [ ] `runtime/cycle.py:GameCycle`:
  ```
  while running:
      sleep_to_tick_rate(v10)   # v10 is in units of 1/20s
      clear keyboard buffer; clear f2, f4
      poll_sdl_events() → key queue, quit
      update_input_line() → input buffer, v19 = last key
      process_controllers() → check bound keys, set controller-fired bits
      advance_clock() → v11..v14
      if v21 > 0: v21 -= 1   # window timer
      parse_input_if_enter() → set f2, populate parser groups
      update EGO direction; recalculate object motion; refresh status line
      while True:
          try:
              interpreter.run_logic(0)
          except NewRoomException:
              handle_new_room()
              continue          # re-enter LOGIC 0: no delay, no input poll
          apply v6 to EGO; clear v4, v5, f5, f6, f12
          update_objects() → mover + cycler
          render() → pic + cels + text overlay → SDL blit
          break
  ```
- [ ] `handle_new_room()`:
  1. Stop sound
  2. Reset input line; clear parser state
  3. Discard non-sticky resources (see ResourceManager in M0 — this is why sticky bits matter)
  4. Reset sprite table — erase all, clear most flags, **keep ego view and inventory**
  5. `v1 = v0; v0 = target; v4=v5=v9=0; v16 = ego.view`; reposition ego from `v2`, then `v2 = 0`; clear f2
  6. Set f5 (new-room marker, lifetime = exactly one cycle)
  7. Return — the outer loop re-enters LOGIC 0, which sees f5 and runs init.
- [ ] Honor `v10` for cycle delay. A common value is 2, giving ~10 Hz. Don't hardcode 50 ms.
- [ ] `print` should pause the cycle (don't advance objects) until the window is dismissed or `v21` expires.

**Exit criteria:** Entering SQ1, pressing ENTER past the intro, and walking room-to-room works end-to-end. Rooms load PICs and VIEWs correctly. `new.room` transitions don't leak state.

### M6 — Parser and WORDS.TOK

**Goal:** Typed commands like `look at ship` reach LOGIC as group-id sequences.

- [ ] `resource/words.py:load_words_tok(path) -> dict[str, int]`:
  - Read 26 big-endian u16 offsets at bytes 0x00–0x32 — one per letter a–z. Zero means "no words for this letter."
  - For each letter block, decode entries using prefix compression. Per-entry:
    - `prefix_len (u8)` — number of leading chars shared with the previous word in this letter block (resets to empty at start of each letter block — do not carry state across letters)
    - then characters: for each byte `b`, `ch = (b & 0x7F) ^ 0x7F`; if `b & 0x80` is set, it's the last char.
    - Then `u16 big-endian` group number.
  - Returns a dict mapping full phrase string → group id. **Phrases can contain spaces** (e.g., `"pick up"` is a single entry, not two words). They're stored with ASCII 0x20 (XOR'd to 0x5F on disk) just like any other char; the end-of-word bit is the only delimiter.
- [ ] `runtime/parser.py`:
  - Normalize: lowercase, collapse whitespace, strip stray punctuation.
  - **Longest-match** tokenization: at each cursor position, try the longest possible remaining prefix against the phrase dict and consume matched tokens. A simple `split()`-per-word approach is wrong because of multi-word entries. A trie keyed on space-separated tokens is the efficient approach; a dict of phrases sorted longest-first works for a prototype.
  - Drop all tokens whose group is **0** (noise/filler).
  - If any input word can't be matched, remember it (for `v9` / the "I don't know X" message), set `said_ok = False`, return.
  - Append `9999` (`rol`) as the end-of-input sentinel.
  - Expose `groups: list[int]` and `said_ok: bool` to the interpreter.
- [ ] `said(...)` test command implementation:
  - Args are baked-in u16 group-id sequences in the bytecode.
  - Match iff `said_ok == True` AND `f2 == True` (input this cycle) AND `f4 == False` (no earlier match this cycle).
  - Group-0 words are already removed from input; compare only against non-0 groups.
  - `1` (`anyword`) in the pattern matches any single non-0, non-9999 input id.
  - `9999` (`rol`) matches "zero or more remaining input ids" — usually terminal in the pattern.
  - No trailing `9999` in the pattern → exact-length match required.
  - On first `said()` match in a cycle, set `f4` so subsequent `said()` calls in the same cycle return false.

**Exit criteria:** Typing `look at ship` in SQ1 produces a real game response.

### M7 — Text overlay, input line, controllers, menus

**Goal:** The status line, `print` windows, input echo, and F-key / menu controllers.

- [ ] `gfx/text_overlay.py`: 40×25 character grid. Needs a bitmap font (Sierra's 8×8 is most authentic; you can substitute any 8×8 mono font to get going, and swap in the authentic font later).
- [ ] Status line: row 0 by default, shows score/sound from reserved vars. Commands: `status.line.on/off`, `configure.screen`.
- [ ] Print windows: pop-up text boxes with a border. Block the cycle until dismissed (or `v21` expires).
- [ ] Input line: bottom row. Append printable keys to a buffer, handle BACKSPACE, submit on ENTER. Echo via the text overlay, not via SDL_ttf.
- [ ] Controllers: `set.key(key_code, controller_num)` binds a key combo to a controller id. When that key fires during a cycle, mark it; `controller(n)` returns true once for that cycle. Used for F-keys, ESC menu, etc.
- [ ] Menu bar: `set.menu`, `set.menu.item`, `submit.menu`, `enable.item`, `disable.item`, `menu.input`. When the player triggers menu mode, the interpreter takes over, lets them pick, and fires the selected controller id. Defer if time is short — not strictly required for M6 exit.

**Exit criteria:** SQ1 intro plays through correctly with proper text windows, status line shows score, F-keys work.

### M8 — Sound

**Goal:** Music and sound effects play back, even if imperfectly.

- [ ] `resource/sound.py:decode_sound(payload: bytes) -> Sound`:
  - After the 5-byte VOL header, first 8 bytes are an offset table: 4 × u16 LE, one per channel (3 tone + 1 noise). Offsets are relative to the start of the decoded payload.
  - Each channel is a stream of 5-byte notes:
    - bytes 0-1: duration u16 LE (the vendored spec doesn't state the unit; 1/60s ticks is unconfirmed)
    - bytes 2-3: tone divisor = `((byte2 & 0x3F) << 4) + (byte3 & 0x0F)`, per the formula in spec 7-1 Appendix 1 (verify by ear or against ScummVM `sound_pcjr.cpp`)
    - byte 4: low 4 bits are attenuation, 0 = loudest, 0x0F = silent; the high bits are the register address
  - `duration == 0xFFFF` terminates the channel.
  - Channel 3 (noise) reinterprets byte 3: bit 2 = feedback (0=periodic, 1=white), bits 0-1 = shift-rate select (0=/512, 1=/1024, 2=/2048, 3=use channel 2 freq).
- [ ] `audio/sn76489.py`:
  - Tone voice: phase accumulator at `hz = 111860 / divisor` (111860 = NTSC colorburst / 32). Emit ±amp square wave at 50% duty. `divisor == 0` is silence. `atten == 0x0F` is silence. Atten steps are 2 dB.
  - Noise voice: 15- or 16-bit LFSR at selected shift rate; periodic = single-tap, white = XOR-tap feedback.
- [ ] `audio/player.py`:
  - 60 Hz tick advances all four channels' note cursors.
  - Per-sample mixing in an SDL2 audio callback. Sum and soft-clip; pre-scale each channel to ~0.25.
  - Simple queue for "play sound N" from the `sound` agi command; honor flag 9 (sound on/off).
- [ ] Gotcha: **attenuation 0x0F is silence, not max volume.** This is the #1 beginner mistake and every channel will be mute if inverted.
- [ ] Gotcha: 0xFFFF terminator on duration. 0x0000 duration is legal (advance immediately).

**Exit criteria:** SQ1 intro music plays recognizably.

### M9 — Save/restore

**Goal:** F5/F7 save and load.

- [ ] `io/save.py`:
  - Serialize: game ID, interpreter version stamp, all 256 flags + 256 vars, all strings, current room number, the full sprite table, the loaded-resource list, inventory room assignments, script event buffer.
  - **Don't** serialize a PC inside a logic — logics are assumed to run to completion each cycle, so save points are always at cycle boundaries.
  - Deserialize clobbers state, then triggers the same path as `new.room` so the target room re-init runs via f5.
- [ ] Wire `save.game` / `restore.game` agi commands; default-bind F5/F7 via controllers in a sane way (or let game LOGIC 0 do it).

**Exit criteria:** Save in room 1, quit, reload, continue in room 1 with ego at the saved position.

### M10 — AGI v3 support (deferred)

- LZW decompression on resources (flag in DIR header / resource header)
- A handful of new opcodes
- v3 LOGIC pre-XOR trick (messages are XOR'd before LZW, so don't re-XOR after decompression — check the flag byte)
- Custom v3 PIC compression (separate from LZW — used only on picture resources)

Not on the critical path to a playable SQ1.

---

## 5. Key reference tables (summaries; the wiki has the audited detail)

### LOGIC control bytes

| Byte | Meaning |
|---|---|
| `0x00` | return (end of logic) |
| `0xFC` | OR-group delimiter (inside an `if`) |
| `0xFD` | NOT prefix on next test term |
| `0xFE` | unconditional goto / else, followed by signed int16 LE displacement |
| `0xFF` | if begin AND if end; after closing `0xFF`, signed int16 LE = jump-if-false displacement |

### PIC opcodes

| Byte | Purpose | Params |
|---|---|---|
| `0xF0` | set picture color + enable visual | 1 byte |
| `0xF1` | disable visual | — |
| `0xF2` | set priority color + enable priority | 1 byte |
| `0xF3` | disable priority | — |
| `0xF4` | Y-corner polyline | `x,y` then alt `y,x,y,x,…` |
| `0xF5` | X-corner polyline | `x,y` then alt `x,y,x,y,…` |
| `0xF6` | absolute line polyline | `x,y,x,y,…` |
| `0xF7` | relative short line | `x,y` then per-byte Δ packed |
| `0xF8` | flood fill | `(x,y)` seeds |
| `0xF9` | set pen descriptor | 1 byte |
| `0xFA` | plot pen | solid: `(x,y)`; splatter: `(pat,x,y)` |
| `0xFB`–`0xFE` | unused; skipped to the next valid opcode | — |
| `0xFF` | end of picture | — |

Variable parameter runs end when the next byte is `>= 0xF0`. The one-byte arguments of `0xF0`, `0xF2` and `0xF9` are taken unchecked.

### Priority band quick reference

- Values **0–3** = control cells (0=unconditional barrier, 1=conditional barrier, 2=alarm/signal, 3=water)
- Values **4–15** = Z-depth bands, low=deep, 15=always in front
- `y < 48` is band 4, band 5 starts at y=48, and each band is 12 px tall up to band 14; 15 is never y-derived for ego but is used by pictures and `set.priority`

### Resource headers

All VOL resources (PIC, VIEW, LOGIC, SOUND) begin with the same 5-byte header:

```
b0 b1 : 0x12 0x34  (signature)
b2    : volume number (redundant)
b3 b4 : uint16 LE length (bytes that follow)
```

Then:
- **VIEW**: 7 bytes into the resource (5-byte header + 2-byte VIEW-specific header), then `num_loops` byte, then 2-byte description offset, then loop offset table. See `resource/view.py` for the current implementation.
- **PIC**: payload is raw opcode stream, terminated by `0xFF`.
- **LOGIC**: payload starts with `u16 LE messages_offset`; bytecode in `[2, 2+messages_offset)`; message section follows.
- **SOUND**: payload starts with 4 × `u16 LE` channel offset table.

### XOR key

`"Avis Durgan"` (11 bytes, cycled). Applied to:
- The `OBJECT` file entirely.
- LOGIC message strings (just the string body area, not the pointer table).

Some later AGI games also use `"Alex Simkin"` for certain v3 resource types; irrelevant for v2.

---

## 6. Testing strategy

- **Unit tests** for every decoder: feed a known resource bytes blob, assert the parsed structure. Golden files from SQ1 are the easiest source.
- **Disassembly round-trip** for LOGIC: decode → pretty-print → save as `.logic.txt` files you can diff when you change the decoder.
- **Visual regression** for PIC: render each pic to a PNG, diff against a saved baseline. `PIL` or `Pillow` handles this.
- **Interpreter smoke test**: one test that runs LOGIC 0 for N cycles with a mock resource manager and asserts no crashes, no unimplemented-opcode hits.
- **End-to-end "walk room 1"**: scripted input sequence that walks ego through a fixed path and asserts ego ends at expected coordinates.

Put test games under `test_games/sq1/` (as the existing code already expects) and gate tests with `pytest.mark.skipif` so they skip when game data is missing — never check game files in.

---

## 7. Open questions to resolve as you go

1. **Exact reserved var/flag indices** — M3's flags now follow spec chapter 2-2. Cross-check against a modern ScummVM build only if a particular flag isn't behaving.
2. **SN76489 divisor bit layout** — the interpreter's own chip writes match the stored divisors on a Tandy (`andromeda-wiki/entities/sound.md`). M8 now follows the spec's formula, but it's untested on audio. Write a test tone and verify against a known SQ1 music sample (any YouTube recording of the opening will do as reference).
3. **Priority band y-coordinates** — documented in `andromeda-wiki/interpreter/priority-bands.md`, and confirmed against the running interpreter's own table.
4. **`said()` semantics for ambiguous groups** — settled for 2.917: group-0 words never reach the word list, so `anyword` and `rol` can't see them. See `andromeda-wiki/interpreter/input-parsing.md`.
5. **`v10 == 0` behavior** — settled for 2.917: no wait at all, so the cycle runs as fast as the machine allows. See `andromeda-wiki/interpreter/event-loop.md`.
6. **Cycle-vs-tick distinction** — AGI documentation mixes 20 Hz and 60 Hz loosely. Sound uses 60 Hz ticks (see §M8); game logic uses 20 Hz / `v10` cycles. Keep them as separate concepts in the code.

---

## 8. Recommended work order / critical path

Shortest path to a playable SQ1 room 1:

```
M0 foundation cleanup
   ↓
M1 PIC decoder + dual screens  ───┐
   ↓                              │
M2 LOGIC decoder                  │
   ↓                              │
M3 LOGIC interpreter (stub I/O)   │
   ↓                              │
M4 screen objects + animation  ───┤
   ↓                              │
M5 main cycle                 ←───┘
   ↓
M6 parser + WORDS.TOK
   ↓
M7 text overlay + controllers
   ↓
M8 sound    M9 save/restore   (parallelizable, either order)
```

Each milestone has a concrete "exit criteria" you can demo. If you find yourself blocked inside a milestone, the most common cause is a bad opcode arity or a wrong XOR range — re-read the relevant spec section against the actual bytes before assuming your code is wrong.

---

## 9. One-page summary

- **Target:** Python prototype of AGI v2, playable SQ1 first, ahead of a planned Rust rewrite.
- **Stack:** Python 3.14 + PySDL2.
- **Critical data:** opcode arity table (LOGIC), PIC opcode dispatch (0xF0–0xFF), reserved var/flag constants, the "Avis Durgan" XOR key, the SN76489 frequency constant (111860 / divisor).
- **Critical semantics:** `new.room` aborts the cycle, `said_ok` is per-cycle state, flood fill is "visual drives priority tags along," priority values 0–3 are control cells, message offsets are 1-based, all VOL resources share a 5-byte header.
- **Biggest risks:** getting the opcode arity table wrong (silent desync), getting the PIC line rule wrong (flood-fill leaks), getting the SN76489 bit layout wrong (octave-off audio), getting reserved flag/var indices wrong (game-specific weirdness).
- **Biggest win:** once M5 exits, every subsequent milestone is visible in the running game, which makes debugging far easier.
