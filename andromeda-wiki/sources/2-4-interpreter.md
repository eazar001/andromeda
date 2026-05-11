# Source: 2-4-Interpreter.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/2-4-Interpreter.html`.

## Scope

Coarse-grained map of the AGI interpreter's runtime heap, showing the order of major regions from the data-area header through dynamically-loaded resources. Sizes are exact for variables (256 bytes), flags (32 bytes), and string buffers (12×40 or 24×40 bytes); other regions are labeled "variable" or "unknown". Does not specify byte-level offsets, the internal structure of any region, or which interpreter version the layout reflects.

## Informs

- New: [[interpreter/memory-layout]] — heap layout reference page.
- Updated: [[interpreter/variables-and-flags]] — cross-link from the `var(8)` (free memory) row to the new layout page.
- Updated: [[interpreter/overview]] — Implementation-status note that runtime memory layout joins the list of subsystems whose claims cannot be cross-checked against working code.

## Notes

- Authored by Lance Ewing, "Retrived from the Internet Archive" per the chapter header (typo in original) — not by Peter Kelly. Other chapters in the corpus are predominantly Kelly's; verify per-chapter authorship from the source HTML rather than assuming.
- Chapter is structurally thin: one paragraph + one 17-row table, no sub-sections. The wiki page covers nearly all of the chapter's substance; further detail must come from external sources or original-binary reverse engineering.
- The `"Avis Durgan"` encryption-string row in the heap table is the only mention of encryption in the corpus so far. The chapter does not pin it to a resource type; the Python prototype uses it for OBJECT-file XOR (`resource/objects.py`). LOGIC group ingest (Group 3) is expected to detail any role in resource encryption more broadly.
- No conflicts with existing pages.
