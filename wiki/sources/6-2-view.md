# 6-2-VIEW.html

**Chapter:** 6.2 VIEW Table & VIEW Test Commands
**Author:** Lance Ewing (`be@ihug.co.nz`)
**Last updated:** 31 August 1997
**Provenance:** Retrieved from the Internet Archive; vendored at `AGI_Specifications/Specifications/6-2-VIEW.html`.

## Summary

Specifies the runtime VIEW object table — the interpreter's in-memory state structure for animated screen objects. Distinguishes between the VIEW *resource* (on-disk format, 6-1) and a VIEW *object* (a runtime instance of a VIEW resource, bound to a 43-byte table entry in SQ2). Documents all per-object properties: position, velocity, animation state, flags, and priority. Also specifies four collision-test commands (`posn`, `right.posn`, `center.posn`, `obj.in.box`) that reference the object's "hot-spot" pixel (typically the bottom-left corner of the cel).

This chapter covers runtime object state and collision semantics, not the on-disk format. It is paired with 6-1 (the disk-format spec).

## Pages informed

- [[interpreter/view-objects]] — VIEW object table entry structure (43 bytes in SQ2), complete property enumeration with byte offsets and bit layouts for flag fields, collision-test command semantics and hot-spot reference points.
- [[interpreter/event-loop]] — resolves the forward-reference to view-object animation and state updates in step 10 (rendering).
- [[interpreter/memory-layout]] — resolves the forward-reference to the VIEW object table's location in the heap.

## Notable findings

- **Entry size is interpreter-specific.** The chapter specifies 43 bytes for SQ2; other games may use different sizes (noted in the chapter as probable but not enumerated) [6-2-VIEW.html §VIEW TABLE ENTRY].
- **Unknown/unspecified bytes.** Offsets 02, 14–15, 27–2A contain "??" (purposes not documented in the spec). These are held open for reverse-engineering or ScummVM cross-check [6-2-VIEW.html §VIEW TABLE ENTRY].
- **Collision test hot-spot semantics.** The four test commands vary which pixel point within an object's bounding box they test (left, right, center, or whole-bottom-row), all relative to the default hot-spot at bottom-left corner. The formula for each is given; the test is true iff the selected point(s) fall within the specified rectangle [6-2-VIEW.html §TEST COMMANDS AND VIEWS].

## Related sources

- [[sources/6-1-view]] — VIEW *resource* format (on-disk), complementary to the runtime table here.
- [[sources/2-2-interpreter]], [[sources/4-4-logic]] — event-loop and LOGIC command semantics that interact with object state.

## Open items

- Interpretation of unknown/unspecified bytes at offsets 02, 14–15, 27–2A.
- Per-interpreter-version entry-size variation (SQ2 = 43 bytes; other games not enumerated).
- View flag bits marked "??" in the Bits 0, 4, 6, 7, 10, 12, 14, 15 positions: purpose unknown.
