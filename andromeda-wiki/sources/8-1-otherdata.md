# 8-1-OtherData: OBJECT File Format

**Chapter:** §8.1 OBJECT File Format
**Source:** `AGI_Specifications/Specifications/8-1-OtherData.html`
**Author:** Lance Ewing (`be@ihug.co.nz`)
**Date:** 31 August 1997 (retrieved from Internet Archive)

## Scope

Complete byte-level specification of the OBJECT inventory file: 3-byte header, 3-byte-per-item entry array, null-terminated name section, and optional Avis-Durgan XOR encryption. **Opens Group 7 (Other).**

Despite the chapter title "OtherData", scope is exclusively the OBJECT resource. AGIDATA.OVL, AGI.EXE internals, and other distribution-layer files are not covered.

## Pages informed

- [[entities/object]] — created. Full on-disk layout with encryption, header, entry, and name-section sections.
- [[concepts/agi-data-types]] §Inventory Item — back-reference to the new entity page (existing forward-link upgraded).

## Notable findings

- **Encryption is version-conditional.** v2.089 and v2.272 ship OBJECT in cleartext; v2.411 onward and all v3 use the Avis-Durgan cyclic XOR [[sources/2-8-interpreter]]. Decoders must check interpreter version.
- **Key reuse with LOGIC text.** Same `"Avis Durgan"` 11-byte key encrypts both OBJECT and v2 LOGIC text-message sections [[entities/logic]]. Historical artifact of minimal-effort Sierra encryption.
- **Spec's offset semantics vs. andromeda's decoder.** The spec defines the name-section offset as relative to "the start of entry 0" (file byte 3). `resource/objects.py:31` adds `+ 5` instead of `+ 3` to reach the name section. This discrepancy is documented as an open item on the entity page; cross-check needed against `object.pas:50-52` (which uses `+ 3`).
- **Object cap and animation slots.** Header byte 2 is the maximum simultaneous animated-object count, used to size the runtime VIEW-object table — not the inventory-entry count, which is implicit in the name-section offset.

## Open items

- Reconcile `resource/objects.py:31` (`+ 5`) vs. spec's `+ 3` vs. `object.pas:50-52` (also `+ 3`). The Python decoder works on SQ1 so something else compensates, or the read pipeline strips/prepends 2 bytes upstream.
- Maximum inventory size and per-name length are not bounded by the spec; in practice both are limited by the 64 KB OBJECT file size and the LE u16 offset width.

## See also

- [[entities/object]] — OBJECT resource format.
- [[sources/2-8-interpreter]] — version-fingerprint table; documents the v2.411 encryption introduction.
- [[sources/4-1-logic]] — same Avis-Durgan key applied to LOGIC text sections.
- [[sources/8-3-samplecode]] — `object.pas` reference decoder closes Group 7.
