# Runtime Memory Layout

The AGI interpreter organizes its state on a single linear heap. This page documents the order of major regions as observed at runtime [2-4-Interpreter.html]. The layout is a historical reverse-engineering reference rather than a precise spec: the source chapter is a one-paragraph note plus a coarse-grained table, derived by Lance Ewing using an external memory-resident debugger (Game Wizard) and inserted into Peter Kelly's specification corpus from an Internet Archive snapshot. Region sizes are exact where the spec gives them and unspecified otherwise; the spec does not document the internal structure of regions it labels "unknown". The arrangement below cannot be validated against original interpreter binaries without external instrumentation and original DOS hardware (agidev, unverified — applies to the whole layout).

## Heap layout (in chapter-listed order)

| Region | Size | Notes |
|---|---|---|
| Data-area header | 2 bytes | Length of the first data area [2-4-Interpreter.html]. |
| Game signature | 8 bytes | Magic identifier for the game; format not specified at this chapter's depth [2-4-Interpreter.html]. |
| Variables | 256 bytes | The 256 8-bit variables `var(0)`–`var(255)`. Initialized to 0 on startup [2-2-Interpreter.html §Variables used by the interpreter]. See [[interpreter/variables-and-flags]]. |
| Flags | 32 bytes | The 256 single-bit flags `flag(0)`–`flag(255)`, packed 8 per byte. Initialized to 0 on startup [2-2-Interpreter.html §Flags used by the interpreter]. |
| Timers, blocks, and other special AGI variables | unspecified | The spec uses this exact phrasing without further detail [2-4-Interpreter.html]. Likely covers the interpreter's internal clock (`var(11)`–`var(14)`), border-touch registers, and similar runtime state surfaced through reserved variables. |
| Strings | 12×40 or 24×40 bytes | String parameter buffers, 40 bytes each, zero-terminated [2-3-Interpreter.html §(3) String]. The chapter gives the size as "12*40 bytes or 24*40 bytes" without attributing the choice to an interpreter version [2-4-Interpreter.html]; the per-version mapping is in [[concepts/agi-data-types]]. |
| Unknown | unspecified | Chapter labels this region "unknown" [2-4-Interpreter.html]. |
| UI strings | unspecified | Hardcoded interpreter messages such as `"Press ENTER to quit"` [2-4-Interpreter.html]. |
| Script command jump table | unspecified | Dispatch table for the ~181 LOGIC procedure commands and ~18 test commands [2-1-Interpreter.html §What are the AGI commands?]. Internal structure not given by 2-4. |
| Encryption string | 12 bytes | The string `"Avis Durgan"` (11 chars + zero terminator) embedded in the heap [2-4-Interpreter.html]. The chapter says only that this is an "encryption string"; it does not pin the string to a resource type. The Python prototype uses it as the XOR key for OBJECT-file decryption [resource/objects.py]. The LOGIC chapter (Group 3, not yet ingested) is expected to detail any role in resource encryption more broadly. |
| AGIDATA.OVL remainder | unspecified | Remaining bytes of the `AGIDATA.OVL` overlay (the interpreter's main code/data segment) [2-4-Interpreter.html]. |
| Unknown | unspecified | Second region labeled "unknown" [2-4-Interpreter.html]. |
| WORDS.TOK | variable | Loaded parser dictionary [2-4-Interpreter.html]. Entity page deferred to Group 7 ingest (`8-2-WORDS_TOK.html`). |
| OBJECT file | variable | Loaded inventory table [2-4-Interpreter.html]. Entity page deferred to Group 7 ingest (`8-1-OtherData.html`). |
| VIEW object table | variable | Runtime table of active screen-object instances — each an instance of a VIEW resource, controllable or non-controllable [2-4-Interpreter.html]. See [[interpreter/view-objects]] (deferred to a later Group-2 chapter). |
| LOGIC.0 | variable | The root LOGIC resource, loaded once at startup and resident for the entire session [2-4-Interpreter.html]. |
| Other loaded resources | variable | Dynamically loaded room-specific LOGICs and other resources, swapped in and out as gameplay progresses [2-4-Interpreter.html]. |

## Notes

The layout reflects a single-arena memory model: code, fixed state (variables, flags, string buffers), interpreter-internal data (jump table, encryption key, UI strings), and dynamically loaded resources all share one heap. `var(8)` reports the number of 256-byte pages still free in this heap [2-2-Interpreter.html §Variables used by the interpreter], giving LOGIC scripts a way to query allocation pressure.

The chapter does not specify where the heap begins in the address space, whether it grows up or down, or how the interpreter chooses between satisfying a new resource load from the "Other loaded resources" tail versus reclaiming an existing region. These details are likely interpreter-version- and host-machine-dependent and would need to be recovered from a real DOS binary to be stated with confidence.

## See also

- [[interpreter/variables-and-flags]] — full reserved-slot tables (the Variables and Flags rows above hold these contents at runtime).
- [[concepts/agi-data-types]] — string buffer count by interpreter version, plus the OBJECT-file vs. runtime-object nomenclature distinction relevant to the "OBJECT file" and "VIEW object table" rows.
