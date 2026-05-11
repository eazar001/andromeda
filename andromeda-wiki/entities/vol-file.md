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
- **VOL number** — The number of the VOL file containing this resource (0–15) [3-2-Files.html §VOL File Format; resource/header.py:14]. This duplicates the VOL number already encoded in the directory entry; the working code in [resource/volume.py] does not validate the two against each other, so the rationale (corruption check? error recovery?) is unclear (agidev, unverified).
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

## Resource payload

Bytes 5 through `5 + length - 1` contain the resource data. The interpretation depends on the resource type — LOGIC bytecode, PICTURE drawing commands, VIEW cel imagery, or SOUND audio data — and will be documented in those entity pages as later chapters are ingested.

## Design notes

The v2 5-byte header's 2-byte little-endian length field caps an individual resource at 64 KB. Whether the signature is actually used for synchronization or error recovery is unclear from the spec and not exercised by the working code (agidev, unverified).

The v3 7-byte header keeps both size fields at 16 bits, so the compressed payload stays ≤ 64 KB; the uncompressed size can exceed that after LZW expansion. The bit-7 PICTURE flag lets the interpreter pick the right decompression scheme without consulting the DIR or any other type metadata.

## Standalone files not stored in VOL

[[entities/words-tok]] (vocabulary) and [[entities/object]] (inventory) are standalone per-game files alongside the VOL containers, not VOL payloads. They are reached by filename rather than through a `*DIR` lookup.
