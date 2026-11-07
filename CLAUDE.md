# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Andromeda is an emulator for Sierra's AGI game engine. This Python codebase is the prototype; a Rust rewrite is planned. So far it decodes some resources from AGI games (e.g., Space Quest 1) and draws VIEW cels, but it does not run game logic. AGI games store their resources in `VOL.*` volume files, indexed by `*DIR` directory files (VIEWDIR, LOGDIR, PICDIR, SNDDIR), plus standalone `OBJECT` (inventory) and `WORDS.TOK` (vocabulary) files.

See `DEVELOPMENT_PLAN.md` for the roadmap and known bugs.

## Commands

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run the test harness: plays every VIEW cel in a window, then prints the directory listings
uv run python -m main
```

The game code has no tests or lint configuration yet. `tools/picture_emu/` and `tools/agi_emu/` have their own tests; see their READMEs.

## Directory Structure

```
.
├── main.py              # Test harness entry point
├── gfx/                 # Screen buffers, palette, and cel compositing
├── resource/            # AGI resource decoding
├── util/                # Byte and XOR helpers
├── tools/ghidra/        # Headless Ghidra scripts for interpreter analysis
├── tools/picture_emu/   # Runs the interpreter's PICTURE routine under emulation, with tests
├── tools/agi_emu/       # Runs the whole interpreter under emulation: the runtime evidence for the wiki
├── andromeda-wiki/      # Distilled, cited AGI format knowledge base
├── AGI_Specifications/  # Vendored AGI spec and sample code (see below)
├── test_games/          # Local game data, gitignored
├── CLAUDE.md            # This file
├── DEVELOPMENT_PLAN.md  # Roadmap, milestones, and current status
├── BUILD_GUIDE.md       # Start-to-finish build guide generated from the audited wiki
├── PICTURE_DECODER.md   # Overview of the PICTURE format for M1
├── WIKI.md              # Wiki schema and conventions
├── WIKI_AUDIT_PLAN.md   # The audit of the wiki against the interpreter, now complete
├── README.md
└── pyproject.toml
```

## Architecture

### Resource Pipeline

AGI resources follow a two-step access pattern:

1. **`*DIR` files** → `resource/directory.py:read_dir()` parses 3-byte triplets, each encoding a VOL file number (hi nibble of byte 1) and a byte offset into that VOL file (lo nibble of byte 1 + bytes 2-3). Returns one `(vol, offset)` pair per slot, so list position is the resource number. Absent slots stay in the list with `vol == 0xF`; callers must skip them.
2. **`VOL.*` files** → `resource/volume.py:VolumeReader.read_resource(offset)` seeks to that offset, parses the 5-byte header, and returns `(ResourceHeader, payload)`.

### Modules

- **`util/byte.py`** — single `nibble()` helper that extracts the high or low nibble from a byte.
- **`util/crypto.py`** — `xor_cycle(key_string, file)` decrypts a file with a repeating XOR key.
- **`resource/directory.py`** — parses `*DIR` index files into one `(vol, offset)` pair per slot, reading at most 256. A slot is absent when `vol == 0xF`, whatever the offset; it stays in the list so numbering holds.
- **`resource/header.py`** — `ResourceHeader.parse(f, offset)` reads the 5-byte VOL header. The signature is parsed but not validated.
- **`resource/volume.py`** — `VolumeReader(path)` holds an open VOL file and reads resources from it.
- **`resource/objects.py`** — decrypts and parses the `OBJECT` file. `Object.extract_inventory_objects(file)` returns `Object(index, name, room)` instances, with `name` as bytes. **Known bug:** see Implementation Status.
- **`resource/view.py`** — `get_view_data(reader, view_offset)` takes a `VolumeReader` and returns `View(desc_offset, loops=[Loop(loop_idx, cels=[Cel(...)])])`. `Cel` holds width, height, mirror, non_mirror_idx, alpha, and `cel_data` as `(color, count)` pairs that include the `(0, 0)` row terminators.
- **`gfx/screens.py`** — `VisualScreen` (default fill 15) and `PriorityScreen` (default fill 4) buffers.
- **`gfx/palette.py`** — the 16-color EGA palette; `visual_screen_to_bytes()` converts a screen to horizontally doubled RGBA, and `visual_screen_buffer_to_texture()` makes an SDL texture from it.
- **`gfx/view_render.py`** — `composite_cel(screen, loop_idx, cel)` writes a cel into a screen buffer, handling transparency and mirroring. It always draws at the top-left corner; x/y placement and priority come in M4.
- **`main.py`** — test harness; plays every VIEW cel through `composite_cel` in an SDL window, then prints the `(vol, offset)` pairs from all four DIR files.

### Encoding Details

- **VIEW cels**: RLE encoded; each byte encodes `(color nibble, count nibble)`. `0x00` terminates a row.
- **VIEW cel header byte 2**: bit 7 = mirror flag, bits 6-4 = non-mirrored loop index, bits 3-0 = transparent color.
- **VIEW offsets**: stored as little-endian 16-bit values. Description and loop offsets are relative to the payload start (`view_offset + 5`); cel offsets are relative to their loop's start.
- **OBJECT file**: XOR-encrypted with the repeating key `"Avis Durgan"`. Entry name pointers are relative to file byte 3.
- **EGA palette**: hardcoded 16-color palette in `gfx/palette.py`.

### AGI Specification Reference

**Consult `andromeda-wiki/index.md` first for AGI format questions.** It is a distilled, cited knowledge base maintained by this agent (schema in `WIKI.md` at repo root). Fall back to `AGI_Specifications/` only when the wiki is silent or when verifying a contested byte-level claim against source-of-truth.

Peter Kelly's AGI Specifications are vendored at `AGI_Specifications/` (index: `AGISpecifications.html`, chapters: `Specifications/`). **Do not read this by default** — it is ~640K of HTML across 30+ chapters and will bloat context if ingested broadly. Consult it only when you need byte-level format details that aren't covered in this file or clear from the existing decoders in `resource/`, and read just the specific chapter section you need (e.g., `6-1-VIEW.html` for VIEW resource layout). If the local spec is ambiguous or seems wrong, cross-check against ScummVM source or AGI Studio rather than trusting agidev.com.

### Game Data

Place game files under `test_games/<game>/` (e.g., `test_games/sq1/`). The expected files are `VIEWDIR`, `LOGDIR`, `PICDIR`, `SNDDIR`, `OBJECT`, `WORDS.TOK`, and `VOL.0` (plus higher-numbered VOL files for other resources). Never commit game files, including decoded interpreters such as `AGI.decoded`.

The interpreter binaries (`AGI`, `*.OVL`) may be read and analyzed. See `andromeda-wiki/sources/agi-2917-binary.md` for the setup and routine map.

### Implementation Status

Working on all of SQ1: DIR parsing by slot, VOL header and payload reading, VIEW decoding, and cel compositing (transparency and mirroring).

Parsed, with a known bug to fix before M3:

- **`OBJECT`** names are read sequentially rather than through entry pointers, so SQ1 returns 24 of 25 items and items 18–24 are misnumbered. The `+ 5` at `resource/objects.py:31` only works by skipping SQ1's `?\0` placeholder; do not change it to `+ 3` without moving to pointer lookup.

Still needed: LOGIC (bytecode and interpreter), PICTURE (background), SOUND, WORDS.TOK, and AGI v3 support. `LOGDIR`, `PICDIR`, and `SNDDIR` are read only as indexes.
