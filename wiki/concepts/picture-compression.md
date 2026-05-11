# PICTURE Compression

AGI v3 PICTURE resources use a lightweight, lossless compression scheme specific to PICTURE data — distinct from [[concepts/lzw-compression]] [3-3-Files.html §PICTURE COMPRESSION].

## Scheme

The scheme exploits redundancy in two PICTURE opcodes that change visual and priority color:

- **`0xF0`** — Set visual color (followed by a 1-byte color index, range 0–15).
- **`0xF2`** — Set priority color (followed by a 1-byte color index, range 0–15).

In uncompressed PICTURE data these opcodes always consume two bytes (opcode + color). Since only 16 colors exist, the color byte wastes its high 4 bits. The compression scheme packs colors into 4 bits and re-aligns following bytes [3-3-Files.html §PICTURE COMPRESSION].

### Example

Uncompressed:

```
F0 06 F8 12 45 F0 07 F2 05 F8 14 67
```

Compressed:

```
F0 6F 81 24 5F 07 F2 5F 81 46 7
```

The exact bit-packing is reverse-engineered from this single example: when the decompressor sees `0xF0` or `0xF2`, it reads the next byte's high nybble as the color and treats the low nybble as the start of the next sequence's first byte [3-3-Files.html §PICTURE COMPRESSION] (agidev, unverified — bit-packing rule not formally specified).

## Applicability

Only PICTURE resources use this scheme. v3 PICTURE resources are identified by bit 7 of byte 2 (VOL+flags) in the v3 7-byte resource header; see [[entities/vol-file#Version 3 resource header]] [3-3-Files.html §Version 3 Resource Storage].

The spec notes: "As far as I can tell, none of the PICTUREs are compressed with LZW. This may well be possible though." So PICTURE compression appears to be the *only* compression applied to PICTURE resources in known AGI v3 games (agidev, unverified).

**Implementation status:** Not currently implemented in [resource/volume.py].
