# LZW Compression

AGI v3 non-PICTURE resources are frequently compressed using an adaptive form of LZW [3-3-Files.html §LZW COMPRESSION].

## Algorithm

Adaptive LZW starting with 9-bit codes, growing to 10-bit and then 11-bit as the code table fills. Codes 0–255 represent literal byte values; two special codes control the stream [3-3-Files.html §LZW COMPRESSION]:

- **Code 256** — "Start over" signal: clear the code table, reset to 9-bit encoding, resume with code 258 for new table entries.
- **Code 257** — End-of-resource marker.

Code 256 appears at the start of every compressed resource to initialize the decoder [3-3-Files.html §LZW COMPRESSION]. Table entries use codes 258 onward, storing prefix+character pairs until the code space fills. When code 512 is reached the decoder switches to 10-bit codes; at code 1024 to 11-bit codes [3-3-Files.html §LZW COMPRESSION].

The maximum code observed is 2047 (just below where 12-bit encoding would be required). The spec reports that code 256 ("start over") consistently arrives before 12-bit codes become necessary, but this is hedged in the spec itself ("seems," "appears") and has not been exhaustively verified across all known AGI v3 games (agidev, unverified).

## Decompression

The algorithm is described as identical to the compression used in early SCI games [3-3-Files.html §LZW COMPRESSION]. Detailed decompression pseudocode is not provided in the spec; implementers should consult standard LZW documentation alongside this page.

**Implementation status:** Not currently implemented in [resource/volume.py]. v3 resources are not yet decoded by the Python prototype.

## Where it appears

[[entities/vol-file]] (v3 variant — 7-byte header with separate uncompressed and compressed size fields). Does **not** apply to PICTURE resources, which use [[concepts/picture-compression]] instead.
