# Offset encoding

A 3-byte format (a "triplet") that combines a VOL file number and a byte offset into a single locator. Used by every entry in [[entities/dir-file]] [3-1-Files.html §Version 2 directories].

## Format

Three consecutive bytes decode as:

```
Byte 0: [VVVVPPPP]  (high nibble = VOL number, low nibble = offset bits 16–19)
Byte 1: [PPPPPPPP]  (offset bits 8–15)
Byte 2: [PPPPPPPP]  (offset bits 0–7)
```

- **V** (4 bits, byte 0 high nibble) — VOL number, range 0–15 [3-1-Files.html §Version 2 directories]
- **P** (20 bits) — byte offset into the VOL file, big-endian within the 3-byte span [3-1-Files.html §Version 2 directories]

## Decoding algorithm

Given bytes `[b0, b1, b2]`:

```
vol    = (b0 >> 4) & 0xF
offset = ((b0 & 0xF) << 16) | (b1 << 8) | b2
```

If the decoded pair is `(0xF, 0xFFFFF)` — i.e., all three bytes `0xFF` — the entry signals a nonexistent resource; see [[entities/dir-file#Resource nonexistence]].

Code reference: [resource/directory.py:read_byte_triplet] implements this exactly.

## Where it appears

Currently documented for: directory entries ([[entities/dir-file]]). Other AGI structures that share the same 3-byte form will be back-linked here as they're ingested.

## Design rationale

20-bit offsets give each VOL up to ~1 MB of resource storage; the 4-bit VOL field supports 16 VOL files per game — together enough headroom for the largest commercial AGI titles (agidev, unverified).
