# Source: 3-3-Files.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/3-3-Files.html`. Specifies AGI v3 resource storage: 7-byte header layout with compression-detection fields, LZW decompression algorithm, and PICTURE-specific compression.

## Scope

Resource header format for AGI v3 (7-byte layout with uncompressed/compressed size fields), the LZW compression algorithm (adaptive 9-to-11-bit codes with start/end markers), and the PICTURE-specific 4-bit color-packing scheme. Does not cover PICTURE/LOGIC/VIEW/SOUND internal formats.

## Informs

- [[entities/vol-file]] — v3 7-byte resource header variant with compression-detection fields
- [[concepts/lzw-compression]] — adaptive LZW algorithm and code-width progression
- [[concepts/picture-compression]] — lightweight PICTURE-specific compression scheme

## Notes

- No conflicts observed between the spec and existing wiki pages.
- **Implementation gap:** [resource/header.py] and [resource/volume.py] do not yet handle v3 headers or any decompression. v3 games cannot currently be decoded by the Python prototype; likely deferred to the Rust rewrite phase.
- The LZW algorithm is stated to match early SCI compression, lending it plausibility. Neither the PICTURE-compression bit-packing rule nor the LZW edge case ("code 256 always arrives before 12-bit codes are needed") has been validated against a working v3 game (agidev, unverified).
