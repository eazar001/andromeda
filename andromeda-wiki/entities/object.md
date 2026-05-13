# OBJECT Resource

The OBJECT file stores inventory-item metadata: the display name of each inventory item (e.g. "brass key", "goblet") and the starting room where the item begins the game (or `0xFF` meaning "carried by the player at game start"). One OBJECT file per game; inventory items are global, shared across all rooms.

This page documents the on-disk format. Runtime acquisition/disposal semantics (`$67 get`, `$74 drop`, `$76 get.num`) live under [[interpreter/commands]].

## File location and naming

OBJECT is a standalone file in the game directory (alongside `VOL.*`, `*DIR`, `WORDS.TOK`). It is **not** stored inside a VOL container and **not** indexed by the directory files [8-1-OtherData.html].

## Encryption

Most OBJECT files are XOR-encrypted with the repeating 11-byte key `"Avis Durgan"`, applied cyclically across the entire file [8-1-OtherData.html §The file encryption]. Decryption is just the same XOR applied a second time.

**Version conditionality.** Early AGI v2 (v2.089, v2.272) did *not* encrypt OBJECT; encryption was introduced in v2.411 and applies to all later v2 and v3 games [[sources/2-8-interpreter]]. A compliant decoder must consult the interpreter version before applying decryption.

**Key reuse.** The same `"Avis Durgan"` key encrypts v2 LOGIC text-message sections ([[entities/logic]]) and is embedded literally in the interpreter heap ([[interpreter/memory-layout]]).

## Format

```
+------------------------------+
| Header (3 bytes)             |  name-section offset (LE u16) + max animated objects (u8)
+------------------------------+
| Inventory entries (3 B each) |  name offset (LE u16) + starting room (u8)
+------------------------------+
| Name section                 |  null-terminated ASCII strings
+------------------------------+
```

[8-1-OtherData.html §The first three bytes, §The inventory name section]

### Header (3 bytes)

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0–1 | 2 | Inventory name-section offset | Little-endian u16. Offset (relative to the start of the inventory-entry array, i.e. file byte 3) where the null-terminated name strings begin. Also the implicit end of the entry array. |
| 2 | 1 | Max animated objects | Maximum simultaneous on-screen VIEW objects the interpreter must allocate for this game. Typically 16–32. |

### Inventory entries

The entry array begins at file byte 3 and continues until file byte `3 + name_section_offset`. Each entry is 3 bytes [8-1-OtherData.html §The first three bytes]:

| Offset within entry | Size | Field | Meaning |
|---|---|---|---|
| 0–1 | 2 | Name offset | Little-endian u16. Byte offset (relative to file byte 3) into the name section pointing at the first character of this item's name. |
| 2 | 1 | Starting room | Room number 0–254 where the item begins, or `0xFF` meaning "carried by the player at game start". |

### Name section

Null-terminated ASCII strings, one per inventory item, in the same order as the entries that reference them. The name offset in each entry points to the first character of its name (not the terminator) [8-1-OtherData.html §The inventory name section].

## Reference implementations

- **`AGI_Specifications/Code/object.pas`** (Peter Kelly, indexed by [[sources/8-3-samplecode]]) — interactive OBJECT viewer. Implements the cyclic-key decryption (`object.pas:25-37`), little-endian header parsing (`object.pas:50-52`), 3-byte-stride entry iteration (`object.pas:54-71`), and null-terminated name recovery.
- **`resource/objects.py`** (andromeda) — `Object.extract_inventory_objects` parses real SQ1 OBJECT data end-to-end. `decrypt_object_file` (`objects.py:72-73`) uses `util.crypto.xor_cycle` with the `"Avis Durgan"` key.

> [!conflict] `resource/objects.py:31` computes `inventory_start = inventory_offset + 5`, but the spec defines the name-section offset as relative to the start of the entry array (file byte 3) — which would make file-byte name-section start `inventory_offset + 3`, not `+5`. The decoder works in practice on SQ1, suggesting either an undocumented file-prefix wrapper in andromeda's read path or a 2-byte off-by-N kludge that happens to land in valid name-section interior. Flagged as an open item — cross-check `object.pas:50-52` (which uses `+ 3`) against andromeda's read pipeline before treating the spec's "offset relative to entry 0" definition as ratified.

## See also

- [[concepts/agi-data-types]] §Inventory Item — semantic data type for inventory references in LOGIC.
- [[interpreter/commands]] — `$67 get`, `$74 drop`, `$76 get.num` and related opcodes.
- [[entities/logic]] — same `"Avis Durgan"` XOR key used for v2 LOGIC text sections.
- [[sources/8-1-otherdata]] — chapter source.
- [[sources/8-3-samplecode]] — reference implementation (`object.pas`).
