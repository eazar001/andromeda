# VOL (Volume) File

A VOL file is the on-disk binary container that stores game resources (LOGIC, PICTURE, VIEW, SOUND). Each resource is prefixed with a uniform 5-byte header so the file is seekable: a directory entry's `(vol, offset)` pair lands directly on the start of the resource's header [3-2-Files.html §VOL File Format].

## Overview

VOL files are flat sequences of concatenated resources, each preceded by a 5-byte header. A game may have multiple VOL files (numbered 0–15 in the 4-bit VOL field of [[concepts/offset-encoding]]). A [[entities/dir-file]] entry maps each resource ID to a `(vol, offset)` pair; seeking to `offset` in `VOL.<vol>` lands on the start of the resource's header [3-2-Files.html §VOL File Format].

The VOL header carries no resource-type tag. The resource's type (LOGIC / PICTURE / VIEW / SOUND) is implicit from which directory file supplied the offset (LOGDIR / PICDIR / VIEWDIR / SNDDIR respectively) — a VOL file on its own is an untyped blob of headered chunks.

## Resource header

Every resource in a VOL file starts with a 5-byte header:

```
Bytes 0–1:  Signature   (big-endian, 16-bit, always 0x1234)
Byte 2:     VOL number  (0–15)
Bytes 3–4:  Length      (little-endian, 16-bit)
```

- **Signature** — Always `0x12 0x34` (read big-endian as `0x1234`). Acts as a magic number marking the start of a resource [3-2-Files.html §VOL File Format; resource/header.py:13].
- **VOL number** — The number of the VOL file containing this resource [3-2-Files.html §VOL File Format; resource/header.py:14]. 2.917 uses it as a wrong-disk check, together with the signature; see "How AGI 2.917 reads a resource". The working code in [resource/volume.py] does not validate it. On all 462 SQ1 resources the signature is `0x1234` and the VOL number matches the directory entry [SQ1 data check, log 2026-11-01].
- **Length** — Byte count of the resource payload that follows the header, *not* including the 5 header bytes [3-2-Files.html §VOL File Format; resource/header.py:15].

Code reference: [resource/header.py:ResourceHeader.parse] parses this header; [resource/volume.py:VolumeReader.read_resource] returns the parsed header and the payload bytes.

### Version 3 resource header

AGI v3 resources use a 7-byte header instead of the v2 5-byte variant [3-3-Files.html §Version 3 Resource Storage]:

```
Bytes 0–1:  Signature         (big-endian, 16-bit, always 0x1234)
Byte 2:     VOL + flags       (bits 0–3 = VOL number 0–15; bit 7 = PICTURE flag; bits 4–6 reserved)
Bytes 3–4:  Uncompressed size (little-endian, 16-bit)
Bytes 5–6:  Compressed size   (little-endian, 16-bit)
```

- **Signature** — Always `0x12 0x34`, as in v2 [3-3-Files.html §Version 3 Resource Storage].
- **VOL + flags** — Low nibble (bits 0–3): VOL number 0–15. Bit 7: set if the resource is a PICTURE; selects [[concepts/picture-compression]] over [[concepts/lzw-compression]] when decompressing. Bits 4–6: reserved [3-3-Files.html §Version 3 Resource Storage].
- **Uncompressed size** — Byte count of the resource *after* decompression [3-3-Files.html §Version 3 Resource Storage].
- **Compressed size** — Byte count of the resource as stored in the VOL file [3-3-Files.html §Version 3 Resource Storage].

The interpreter detects compression by comparing the two sizes: equal → resource is stored uncompressed; unequal → decompress, choosing the scheme by the PICTURE flag (bit 7 set → [[concepts/picture-compression]]; otherwise → [[concepts/lzw-compression]]) [3-3-Files.html §Version 3 Resource Storage].

**Implementation status:** [resource/header.py:ResourceHeader.parse] and [resource/volume.py:VolumeReader.read_resource] currently parse only the v2 5-byte header. The v3 7-byte variant, the size fields, and all decompression are not yet implemented.

## How AGI 2.917 reads a resource

Static reading, not run [AGI 2.917 1000:2E32, 1000:2E56, 1000:3080].

**Opening.** The files `vol.0` to `vol.4` are opened together on first use, and a file that doesn't exist simply stays unopened. SQ1 has only 0–2. The handle table has 10 slots, but only these 5 are ever opened, so a directory entry naming VOL 5–14 can never be read.

**Reading.**

1. Take the VOL number and offset from the directory entry, and seek to the offset.
2. Read 5 bytes, and check the signature bytes `12 34` and that the VOL byte equals the entry's VOL number.
3. Take the little-endian length, allocate that many bytes unless the caller supplied a buffer, and read the payload. The header is not kept.

**Failures.** Each of these retries the whole read from the start, after restoring the heap top. A retry can loop until the player quits.

| Failure | Message | Response |
|---|---|---|
| VOL file not open | "Please insert disk" and a number | Reopens all VOL files and retries |
| Bad signature or VOL byte | "That is the wrong disk", then the same request | Files are closed first. Enter reopens them and retries. Esc quits |
| Short read, or a DOS critical error while opening | A disk error message, chosen by the error code | Enter retries. Esc quits |

The disk number shown is the entry's VOL number, or for VOL 0 the last non-zero one, or else 1. So VOL 0 is treated as present on every disk.

**Low memory.** `show.obj` and `show.obj.v` set a mode where the read gives up and returns nothing if the resource is larger than free memory, and the command then shows a message instead of the object [AGI 2.917 1000:2F8E, 1000:5E3A]. In every other case the allocator decides; see [[interpreter/memory-layout]], where the out-of-memory behavior is still unread.

A reimplementation with no disk swapping can treat all of these as fatal errors.

## Resource payload

Bytes 5 through `5 + length - 1` contain the resource data. The interpretation depends on the resource type — LOGIC bytecode, PICTURE drawing commands, VIEW cel imagery, or SOUND audio data — and will be documented in those entity pages as later chapters are ingested.

## Design notes

The v2 5-byte header's 2-byte little-endian length field caps an individual resource at 64 KB. The signature isn't used to resynchronize; a bad one just means the wrong disk.

The v3 7-byte header keeps both size fields at 16 bits, so the compressed payload stays ≤ 64 KB; the uncompressed size can exceed that after LZW expansion. The bit-7 PICTURE flag lets the interpreter pick the right decompression scheme without consulting the DIR or any other type metadata.

## Standalone files not stored in VOL

[[entities/words-tok]] (vocabulary) and [[entities/object]] (inventory) are standalone per-game files alongside the VOL containers, not VOL payloads. They are reached by filename rather than through a `*DIR` lookup.
