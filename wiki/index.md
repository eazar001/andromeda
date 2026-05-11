# Wiki Index

Distilled AGI-format knowledge base. Start here for any byte-level format question. See `WIKI.md` (repo root) for schema and conventions.

## Quick refs

_(Highest-traffic pages will be promoted here once content lands.)_

## Entities

Resource types and on-disk file formats. One page per resource.

- [[entities/dir-file]] — VOL/DIR addressing: v2 and v3 directory file layouts, entry decoding, sparse-numbering sentinel.
- [[entities/vol-file]] — VOL container format: 5-byte resource header (signature, VOL number, length) and payload structure.

## Concepts

Shared primitives referenced by multiple entities: encoding schemes, palettes, encryption keys, common header layouts.

- [[concepts/offset-encoding]] — 3-byte triplet encoding combining VOL number and byte offset; used in every directory entry.
- [[concepts/lzw-compression]] — adaptive LZW (9-/10-/11-bit codes) applied to most AGI v3 non-PICTURE resources.
- [[concepts/picture-compression]] — 4-bit color-packing scheme specific to AGI v3 PICTURE resources.
- [[concepts/agi-data-types]] — semantic data types used as AGI command parameters: variables, flags, strings, words, objects, inventory items, messages.

## Interpreter

The LOGIC VM and runtime model: opcode tables, event loop, priority bands, object state, screen state.

- [[interpreter/overview]] — high-level VM-model hub; one paragraph per subsystem with links into the detailed pages.
- [[interpreter/variables-and-flags]] — reserved `var(0)`–`var(26)` and `flag(0)`–`flag(15)`: complete assignment table, semantics, shared-namespace scoping.
- [[interpreter/event-loop]] — eleven-step per-frame cycle: input poll, LOGIC execution, post-LOGIC cleanup, rendering, room-transition check, with per-step variable/flag state management.
- [[interpreter/memory-layout]] — runtime heap organization: 256-byte variable region, 32-byte flag region, string buffers, jump table, encryption key, and loaded resources, in heap order.
- [[interpreter/input-parsing]] — player-input preprocessing (punctuation/case/space normalization, vocabulary lookup) and `said` test pattern matching (wildcards `1` and `9999`, equality, at-most-once-per-cycle semantics).
- [[interpreter/command-evolution]] — version-conditional command argument-count rules for LOGIC bytecode decoding (`quit`, `print.at`, `print.at.v`, unknown #176) plus command-count summary by interpreter version.

## Sources

One page per ingested AGI Specification chapter, with a short summary and links to the entity/concept pages it informed.

- [[sources/3-1-files]] — Directory files and VOL/DIR addressing scheme (AGI v2 and v3).
- [[sources/3-2-files]] — VOL file container format and 5-byte resource header.
- [[sources/3-3-files]] — AGI v3 resource storage: 7-byte headers, LZW compression, PICTURE compression.
- [[sources/3-4-files]] — Sample-code reference table (Lance Ewing's historical decoders). Bibliographic only; no new format content.
- [[sources/2-1-interpreter]] — Interpreter overview chapter (VM model at headline depth; subsystem detail deferred).
- [[sources/2-2-interpreter]] — Reserved variables/flags assignment tables and the eleven-step interpreter work cycle.
- [[sources/2-3-interpreter]] — Semantic data types: variables, flags, strings, words, objects, inventory items, messages.
- [[sources/2-4-interpreter]] — Runtime heap layout (memory-resident debugger view). Single-arena memory model with code, fixed state, and dynamic resources sharing one heap.
- [[sources/2-5-interpreter]] — Game IDs, loaders, and interpreter-binary 128-byte rolling-XOR encryption. Out-of-scope reference (distribution layer, not game-data format); no entity or concept pages derived.
- [[sources/2-6-interpreter]] — Input preprocessing pipeline and `said` test semantics. Sourced from the AGDS Russian-language manual (translated by Vassili Bykov), retrieved from the Internet Archive.
- [[sources/2-7-interpreter]] — Hobbyist-compiled cross-reference of AGI games to interpreter versions (v2: 2.089–2.936; v3: 3.002.086–3.002.149). Out-of-scope reference; empirical anchor for version-conditional format claims.
- [[sources/2-8-interpreter]] — Interpreter-version fingerprint table (binary sizes, command counts, OBJECT/LZW flags) and post-table observations: command argument-count discrepancies, v3 LOGIC-message-no-encryption and 4-bit PICTURE color-codes, string allocation. Closes Group 2.
