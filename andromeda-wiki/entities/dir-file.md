# DIR (Directory) File

The directory file is the master index that locates every resource inside the VOL files. AGI v2 games carry four separate directory files (`LOGDIR`, `PICDIR`, `VIEWDIR`, `SNDDIR`); AGI v3 games merge them into a single unified `*DIR` file with an 8-byte header [3-1-Files.html §Version 2 directories; §Version 3 directories].

## Overview

A directory file is a flat sequence of fixed-size entries (each a 3-byte triplet). The entry's index in the file *is* the resource ID — entry 0 in `PICDIR` locates `PICTURE.0`, entry 5 locates `PICTURE.5`, and so on. Up to 256 entries per directory are supported [3-1-Files.html §Version 2 directories].

Each entry resolves to a `(vol, offset)` pair via [[concepts/offset-encoding]]; the offset lands on the start of a 5-byte resource header inside the VOL file (see [[entities/vol-file]]).

## Version 2 (separate files)

In AGI v2, each resource type owns a directory file with no header — just a sequence of 3-byte entries [3-1-Files.html §Version 2 directories].

### Entry layout

```
Byte 0: [VVVVPPPP]  (high nibble = VOL number, low nibble = high 4 bits of offset)
Byte 1: [PPPPPPPP]  (middle byte of offset)
Byte 2: [PPPPPPPP]  (low byte of offset)
```

Where:

- **V** (4 bits) — VOL number, range 0–15 [3-1-Files.html §Version 2 directories]
- **P** (20 bits) — byte offset into that VOL file, big-endian within the 3-byte span [3-1-Files.html §Version 2 directories]

The decoding algorithm is documented under [[concepts/offset-encoding]] and implemented in [resource/directory.py:read_byte_triplet].

### Example

Entry 45 in `SNDDIR` with bytes `12 3D FE`:

- VOL number = `0x1` (high nibble of byte 0)
- Offset = `0x23DFE` (low nibble of byte 0, then bytes 1–2)
- Resource `SOUND.45` is at byte offset `0x23DFE` in `VOL.1`.

## Version 3 (unified file)

In AGI v3, all four directories are merged into a single file named `*DIR`, where `*` is the game code (e.g., `BCDIR`, `KQ4DIR`) [3-1-Files.html §Version 3 directories]. The file starts with an 8-byte header listing the offsets of the four directory sections, followed by `LOGDIR`, `PICDIR`, `VIEWDIR`, and `SNDDIR` in that order [3-1-Files.html §Version 3 directories].

### Header layout

```
Bytes 0–1:  LOGDIR offset  (little-endian, 16-bit)
Bytes 2–3:  PICDIR offset  (little-endian, 16-bit)
Bytes 4–5:  VIEWDIR offset (little-endian, 16-bit)
Bytes 6–7:  SNDDIR offset  (little-endian, 16-bit)
```

The `LOGDIR` offset is always 8 (encoded as bytes `08 00` little-endian), since `LOGDIR` immediately follows the 8-byte header [3-1-Files.html §Version 3 directories]. Each section that follows uses the same 3-byte entry format as v2.

## Resource nonexistence

An entry value of `FF FF FF` (all three bytes `0xFF`) signals that the resource slot is unused — distinct from a resource that exists with zero length. The directory reserves the numbering slot but no VOL storage is allocated [3-1-Files.html §Version 2 directories].

This enables sparse numbering: a game can define `PICTURE.5` without `PICTURE.0`–`PICTURE.4`, with the unused entries marked `FF FF FF`. [resource/directory.py:read_dir] filters these entries out when reading a directory.

## Design notes

The encoding supports 16 VOL files (0–15) and up to ~1 MB offset per file (20-bit addressing), matching the file-size norms of 1990s DOS systems (agidev, unverified).

## Standalone files not indexed by DIR

Not every game-data file is reached through a `*DIR` entry. [[entities/words-tok]] (vocabulary) and [[entities/object]] (inventory) are standalone per-game files in the game directory; the directory files only index the resource types stored inside VOL containers (LOGIC, PICTURE, VIEW, SOUND).
