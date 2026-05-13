# 8-3-SampleCode: OBJECT and WORDS.TOK reference decoders

**Chapter:** §8.3 Sample Code
**Source:** `AGI_Specifications/Specifications/8-3-SampleCode.html`
**Author:** No chapter byline; both listed files attributed to Peter Kelly.
**Date:** None in chapter HTML; retrieved from Internet Archive.

## Scope

Sample-code index page only. A two-row table pointing at:

| File | Author | Description |
|---|---|---|
| `AGI_Specifications/Code/object.pas` | Peter Kelly | OBJECT file viewer (cleartext / decrypted) |
| `AGI_Specifications/Code/words.pas`  | Peter Kelly | WORDS.TOK file viewer |

Structurally parallel to [[sources/3-4-files]], [[sources/4-6-logic]], [[sources/5-3-picture]], [[sources/6-3-view]], and [[sources/7-2-sound]] — each "Sample Code" closer is a pointer table rather than a specification.

## Reference implementations

- **`object.pas`** (Peter Kelly, Borland Pascal 7) — Interactive OBJECT viewer. Validates [[entities/object]]: Avis-Durgan cyclic XOR (`object.pas:25-37`), little-endian header parsing (`object.pas:50-52`), 3-byte-stride entry iteration (`object.pas:54-71`), null-terminated name recovery. Uses spec-conformant `+ 3` for the name-section offset (file byte 3 + index), unlike andromeda's `resource/objects.py:31` which adds `+ 5` — see open item on [[entities/object]].
- **`words.pas`** (Peter Kelly, Borland Pascal 7) — Interactive WORDS.TOK viewer / index builder. Validates [[entities/words-tok]]: prefix-share decoding (`words.pas:86-88`), `0x7F`-XOR character decode written as `chr(63 + 32 - curbyte)` arithmetic identity (`words.pas:92-102`), high-bit end-of-word marker (`words.pas:100-102`), big-endian word-number decode `msbyte*256 + lsbyte` (`words.pas:104-106`), pipe-separator joining for synonym groups sharing a word number (`words.pas:110`). Reads only the low byte of `A`'s alphabet-index offset (`words.pas:75-76`) — a code shortcut that assumes the Hi byte is `0x00`, satisfied by all real WORDS.TOK files but not a complete reading of the spec's 52-byte index.

## Validation outcome

No new format claims; both decoders corroborate the byte-level specs in 8-1 and 8-2 respectively. The single conflict surfaced is between `object.pas:50-52` (spec-conformant `+ 3`) and andromeda's `resource/objects.py:31` (`+ 5`) — documented on [[entities/object]] as an open item rather than treated as a code-validates-spec round-trip.

## See also

- [[entities/object]] — OBJECT format (validated by `object.pas`).
- [[entities/words-tok]] — WORDS.TOK format (validated by `words.pas`).
- [[sources/8-1-otherdata]] — OBJECT chapter.
- [[sources/8-2-words-tok]] — WORDS.TOK chapter.

**Closes Group 7 (Other).**
