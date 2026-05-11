# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Andromeda is a Sierra AGI game engine emulator written in Python. It decodes and renders resources from Sierra On-Line AGI games (e.g., Space Quest 1). AGI games store their resources in `VOL.*` volume files, indexed by `*DIR` directory files (VIEWDIR, LOGDIR, PICDIR, SNDDIR), plus an `OBJECT` file for inventory.

## Commands

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Run the main entry point
uv run python -m main
```

There are no tests or lint configurations currently.

## Directory Structure

```
.
├── main.py              # Entry point
├── gfx/                 # Graphics/rendering modules
├── resource/            # AGI resource decoding
├── util/                # Utility helpers
├── CLAUDE.md            # This file
├── DEVELOPMENT_PLAN.md
├── README.md
└── pyproject.toml
```

## Architecture

### Resource Pipeline

AGI resources follow a two-step access pattern:

1. **`*DIR` files** → `resource/directory.py:read_dir()` parses 3-byte triplets, each encoding a VOL file number (hi nibble of byte 1) and a byte offset into that VOL file (lo nibble of byte 1 + bytes 2-3). Returns `(vol, offset)` pairs.
2. **`VOL.*` files** → the offset from step 1 is used to seek into the appropriate volume file and read the resource data.

### Modules

- **`util/byte.py`** — single `nibble()` helper that extracts the high or low nibble from a byte.
- **`resource/directory.py`** — parses `*DIR` index files into `(vol, offset)` pairs; skips entries where both equal `0xF`/`0xFFFFF` (missing resource sentinel).
- **`resource/objects.py`** — decrypts and parses the `OBJECT` file (XOR-encrypted with the key `"Avis Durgan"`). Exposes `Objects.extract_inventory_objects(file)` to get a list of `Object(index, name, room)` instances.
- **`resource/view.py`** — reads VIEW resources from a VOL file. Entry point is `get_view_data(vol_path, offset)`, which returns `(desc_offset, cels)`. Navigates the VIEW header → loop offsets → cel offsets, then reads each cel's width/height/alpha/mirror and RLE-encoded pixel rows.
- **`gfx/view_render.py`** — renders decoded cel data using PySDL2. `read_cel_data(image)` maps each byte to `(color, num_pixels)` nibble pairs. `draw_cel_data(renderer, width, height, pixels, alpha)` paints them using the 16-color EGA palette, treating the `alpha` color index as transparent.
- **`main.py`** — entry point; currently iterates all four DIR files and prints `(vol, offset)` pairs. Contains a commented-out `render_test()` flow for rendering VIEW cels via SDL2.

### Encoding Details

- **VIEW cels**: RLE encoded; each byte encodes `(color nibble, count nibble)`. `0x00` terminates a row.
- **Offsets in VIEW/loop headers**: stored as little-endian 16-bit values, relative to `view_offset + 5`.
- **OBJECT file**: XOR-encrypted with the repeating key `"Avis Durgan"`.
- **EGA palette**: hardcoded 16-color palette in `gfx/view_render.py`.

### AGI Specification Reference

**Consult `wiki/index.md` first for AGI format questions.** It is a distilled, cited knowledge base maintained by this agent (schema in `WIKI.md` at repo root). Fall back to `AGI_Specifications/` only when the wiki is silent or when verifying a contested byte-level claim against source-of-truth.

Peter Kelly's AGI Specifications are vendored at `AGI_Specifications/` (index: `AGISpecifications.html`, chapters: `Specifications/`). **Do not read this by default** — it is ~640K of HTML across 30+ chapters and will bloat context if ingested broadly. Consult it only when you need byte-level format details that aren't covered in this file or clear from the existing decoders in `resource/`, and read just the specific chapter section you need (e.g., `6-1-VIEW.html` for VIEW resource layout). If the local spec is ambiguous or seems wrong, cross-check against ScummVM source or AGI Studio rather than trusting agidev.com.

### Game Data

Place game files under `test_games/<game>/` (e.g., `test_games/sq1/`). The expected files are `VIEWDIR`, `LOGDIR`, `PICDIR`, `SNDDIR`, and `VOL.0` (plus higher-numbered VOL files for other resources).

### Implementation Status

Decoding is complete for: OBJECT, VIEWDIR, VIEW, LOGDIR, PICDIR, SNDDIR.
Still needed: LOG (bytecode), PIC (background), SND (sound), and AGI v3+ support.
