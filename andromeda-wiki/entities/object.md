# OBJECT Resource

The OBJECT file stores inventory-item metadata: the display name of each inventory item (e.g. "brass key", "goblet") and the starting room where the item begins the game (or `0xFF` meaning "carried by the player at game start"). One OBJECT file per game; inventory items are global, shared across all rooms.

This page documents the on-disk format and the commands that use it (`$5C get` through `$61 get.room.v`).

## File location and naming

OBJECT is a standalone file in the game directory (alongside `VOL.*`, `*DIR`, `WORDS.TOK`). It is **not** stored inside a VOL container and **not** indexed by the directory files [8-1-OtherData.html].

## Encryption

Most OBJECT files are XOR-encrypted with the repeating 11-byte key `"Avis Durgan"`, applied cyclically across the entire file [8-1-OtherData.html §The file encryption]. Decryption is just the same XOR applied a second time.

**Version conditionality.** Early AGI v2 (v2.089, v2.272) did *not* encrypt OBJECT; encryption was introduced in v2.411 and applies to all later v2 and v3 games [[sources/2-8-interpreter]]. A compliant decoder must consult the interpreter version before applying decryption. 2.917 XORs the whole file unconditionally, starting at key index 0 [AGI 2.917 1000:0FD3].

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
| 2 | 1 | Highest object number | 2.917 allocates this value plus 1 object slots, at 43 bytes each [AGI 2.917 1000:1001, 1000:100B]. SQ1's value is 17, so it has 18 slots, numbered 0–17. The spec calls it the maximum number of animated objects. |

### Inventory entries

The entry array begins at file byte 3 and continues until file byte `3 + name_section_offset`. Each entry is 3 bytes [8-1-OtherData.html §The first three bytes]:

| Offset within entry | Size | Field | Meaning |
|---|---|---|---|
| 0–1 | 2 | Name offset | Little-endian u16. Byte offset (relative to file byte 3) into the name section pointing at the first character of this item's name. |
| 2 | 1 | Starting room | Room number where the item begins, or `0xFF` meaning "carried by the player". All 25 SQ1 items start in room 0 [SQ1 data check, log 2026-11-01]. |

### Name section

Null-terminated ASCII strings. The name offset in each entry points to the first character of its name (not the terminator) [8-1-OtherData.html §The inventory name section]. **Always resolve names through the entry's pointer**, as the interpreter does [AGI 2.917 1000:3266]. Strings are not one-per-item in entry order: SQ1's section starts with a `?\0` placeholder at offset 75, item 0 (`dummy`) points to offset 77, and item 17 points back to the placeholder [SQ1 data check, log 2026-11-01].

## How AGI 2.917 uses it

**In memory.** The decrypted file stays in memory, and the entry array is used in place. Commands change the room byte directly, so the name offsets and the item table share one buffer [AGI 2.917 1000:0FA5]. A file that can't be found shows a prompt where Enter retries and Esc quits [AGI 2.917 1000:3113].

**Commands** [AGI 2.917 1000:7471–1000:7545]:

| Command | Effect |
|---|---|
| `get(i)`, `get.v(v)` | Room byte = 255 |
| `drop(i)` | Room byte = 0 |
| `put(i, v)` | Room byte = `var(v)` |
| `put.v(a, b)` | Item `var(a)`, room byte = `var(b)` |
| `get.room.v(a, b)` | `var(b)` = room byte of item `var(a)` |

There is no `drop.v`, as the table in [[interpreter/commands]] already shows. `drop` means room 0, not the current room.

**Bounds.** All of these raise error `0x17` for an item past the end of the array. `var(18)` then holds the item number minus the item count, not the item number [AGI 2.917 1000:7571, 1000:75D5]. The tests `has` and `obj.in.room` don't check, and read whatever follows [AGI 2.917 1000:08AD, 1000:093B].

**`status`.** The inventory screen walks the array and lists items in room 255, using the pointer for each name. If there are none, it shows a fixed message from `DS:0F16`. Items sit in two columns, and an item number equal to `var(25)` starts highlighted [AGI 2.917 1000:3203]. The rest of the screen, including selection, is unread.

## Reference implementations

- **`AGI_Specifications/Code/object.pas`** (Peter Kelly, indexed by [[sources/8-3-samplecode]]) — interactive OBJECT viewer. Implements the cyclic-key decryption (`object.pas:25-37`), little-endian header parsing (`object.pas:50-52`), 3-byte-stride entry iteration (`object.pas:54-71`), and null-terminated name recovery.
- **`resource/objects.py`** (andromeda) — `Object.extract_inventory_objects` returns 24 of SQ1's 25 items: it reads names sequentially, drops item 17, and renumbers items 18–24 down by one [SQ1 data check, log 2026-11-01]. `decrypt_object_file` (`objects.py:72-73`) uses `util.crypto.xor_cycle` with the `"Avis Durgan"` key.

**Resolved: `+ 5` vs. `+ 3`.** The spec's `+ 3` is correct: the name section starts at `inventory_offset + 3`. The `+ 5` at `resource/objects.py:31` skips SQ1's two-byte `?\0` placeholder, which is why item 0 still reads `dummy`. Changing it to `+ 3` alone makes things worse, because every name moves down one item [SQ1 data check, log 2026-11-01]. The fix is pointer-based name lookup, which is also what 2.917 does.

## See also

- [[concepts/agi-data-types]] §Inventory Item — semantic data type for inventory references in LOGIC.
- [[interpreter/commands]] — `$5C get` through `$61 get.room.v`.
- [[entities/logic]] — same `"Avis Durgan"` XOR key used for v2 LOGIC text sections.
- [[sources/8-1-otherdata]] — chapter source.
- [[sources/8-3-samplecode]] — reference implementation (`object.pas`).
