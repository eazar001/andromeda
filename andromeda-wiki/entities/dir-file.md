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

- **V** (4 bits) — VOL number, range 0–15 by format [3-1-Files.html §Version 2 directories]. 2.917 can read only 0–4, and treats 15 as absent. See "How AGI 2.917 uses directories".
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

In AGI 2.917, an entry is absent when the high nibble of its first byte is `F`. The other 20 bits are ignored [AGI 2.917 1000:434E].

> [!conflict] What marks an absent resource
> **Refined:** the spec names only `FF FF FF` [3-1-Files.html §Version 2 directories]. On SQ1 that form accounts for 86 of the 87 absent entries. The other is `SNDDIR` slot 0, `FF 23 C1`, which earlier looked like an invalid entry pointing at `VOL.15`. The interpreter's rule covers it [SQ1 data check, log 2026-11-01].

This enables sparse numbering: a game can define `PICTURE.5` without `PICTURE.0`–`PICTURE.4`. [resource/directory.py:read_dir] filters out only `FF FF FF`, which also loses the numbering: list position no longer equals resource number. On SQ1, 61 of 101 LOGIC, 73 of 73 PICTURE, 228 of 238 VIEW, and 46 of 51 SOUND entries sit at the wrong position [SQ1 data check, log 2026-11-01]. LOGIC addresses resources by number, so a reader must key entries by slot and apply the high-nibble rule.

SQ1's counts of absent slots are 23 of 124 in `LOGDIR`, 32 of 105 in `PICDIR`, 16 of 254 in `VIEWDIR` and 16 of 66 in `SNDDIR` [SQ1 data check, log 2026-11-01].

## How AGI 2.917 uses directories

- **Loading:** the files `logdir`, `viewdir`, `picdir` and `snddir` are read whole into memory at startup. A missing file shows "Can't find" with a prompt: Enter retries and Esc quits [AGI 2.917 1000:4305, 1000:3113].
- **Lookup:** the resource number times 3 indexes the loaded file, with no check against the file's size [AGI 2.917 1000:4371, 1000:43A5, 1000:43D9, 1000:440D]. A number past the end reads whatever follows in memory. A reimplementation should treat it as absent.
- **Absent resources are fatal:** the interpreter shows `logic`, `view`, `picture` or `sound`, then "%d not found", and exits. This doesn't go through `var(17)` [AGI 2.917 1000:4441].

## Design notes

The format has room for 16 VOL numbers and about 1 MB per file (20-bit addressing). See [[entities/vol-file]] §"How AGI 2.917 reads a resource" for what the interpreter actually opens.

## Standalone files not indexed by DIR

Not every game-data file is reached through a `*DIR` entry. [[entities/words-tok]] (vocabulary) and [[entities/object]] (inventory) are standalone per-game files in the game directory; the directory files only index the resource types stored inside VOL containers (LOGIC, PICTURE, VIEW, SOUND).
