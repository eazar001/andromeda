# Runtime Memory Layout

How AGI 2.917 arranges memory and manages its heap, read from the interpreter from SQ1. Nothing here was observed running, and other versions are unchecked. The spec's one-paragraph layout [2-4-Interpreter.html] is compared region by region under "Spec layout against 2.917".

## Segments

The interpreter uses three separate areas, and only one is the heap's.

- **Code** sits in its own segment, `1000` in analysis addresses, and is not part of the data area.
- **Data segment.** `DS` is `19F5` in analysis addresses [AGI 2.917 1000:66E5]. Once the heap exists, the stack moves here too, so `SS` equals `DS` [AGI 2.917 1000:00A3]. The fixed data and the whole heap are reached by 16-bit near offsets from this one segment, so nothing in the heap can lie more than 64K from `DS`.
- **Screen buffer.** A separate DOS block of `0x690` paragraphs (26,880 bytes, which is 160×168) holds its segment at `DS:1365` [AGI 2.917 1000:4240]. On monitor type 2 the block is `0xD20` paragraphs, with a second buffer at `+0x690`, and a further `0xC0`-paragraph block holds the `HGC_Font` file [AGI 2.917 1000:423B, 1000:425F]. The use as a screen buffer is inferred from the size and from the drawing routines that load this segment [AGI 2.917 1000:5190, 1000:5631].

## Heap setup

The heap comes from DOS, once, at startup [AGI 2.917 1000:41C6]:

1. Shrink the program's block to end at the initial stack segment (function `4Ah`). The carry result isn't checked.
2. Allocate `0x1000 + DS − 0x1BDC` paragraphs (function `48h`). That is `0xE19` paragraphs, or 57,744 bytes, whatever the machine has. The `0x1000` is a literal, not a relocated segment, so the size doesn't depend on the load address.
3. Convert the returned segment to an offset from `DS`. That offset is both the heap's base and its first free byte. The top is base plus size.

If DOS refuses any allocation, including the screen buffer, the interpreter prints "Sorry, your computer does not have enough memory to play this game.", beeps, and exits with code 1 [AGI 2.917 1000:42E7, DS:0B17]. It never asks for more than this, so extra RAM doesn't help.

**The top wraps.** DOS places a block after its one-paragraph header, so the block should start at `DS + 0x1E8`. Then the base is `DS:1E80` and the top is `0x10010`, which is stored in 16 bits as `0x0010`. All size checks subtract in 16 bits, so they still get the right answer. But near pointers can't reach the block's last 16 bytes, and a heap filled to the very end would write over `DS:0000`–`DS:000F`. Runtime only: neither the returned segment nor this overflow has been observed.

## The allocator

Four words track the heap, all offsets from `DS` [AGI 2.917 1000:13D6, 1000:14BD]:

| Address | Role | `show.mem` label |
|---|---|---|
| `DS:0A4F` | Base | |
| `DS:0A4D` | Next free byte | `now` |
| `DS:0A53` | Top | `heapsize` |
| `DS:0A51` | Resident mark: `new.room` releases down to here | `rm.0, etc.` |
| `DS:0A57` | Highest next-free value reached, never lowered | `max` |

It is a bump allocator. There are no free blocks, headers, or compaction. Allocating compares the request with top minus next as unsigned 16-bit values, returns the old next-free offset, and advances it. New memory isn't cleared. Releasing is only moving next-free back [AGI 2.917 1000:143C], which frees everything above that point.

**Running out is fatal.** If a request exceeds what's left, the interpreter shows a window reading "No memory. Want *n*, have *m*", waits for the player, shuts down, and exits to DOS with code 0 [AGI 2.917 1000:13ED, 1000:02AE, DS:09F5]. The numbers print as signed, so a request of 32K or more looks negative. There is no attempt to discard anything and retry. The one soft failure is `show.obj`: while it loads a view, a resource that doesn't fit returns zero instead, and `show.obj` prints "Not now." [AGI 2.917 1000:2F8E, 1000:5E3A, DS:1505]. That path leaves an empty record on the view list, skips the redraw after loading, and leaves script recording off until the next `new.room` [AGI 2.917 1000:3A5F, 1000:5E60].

**`var(8)`** is the free space shifted down 8 bits, so whole 256-byte pages rounded down. It starts near `0xE1` [AGI 2.917 1000:14A0]. It is recalculated by each allocation, by the heap release, by `discard.pic` and `discard.view`, and by two checks made during `show.obj` loading. It is **not** recalculated by the other paths that lower next-free: the end of a temporary `call`, the rollback on a failed read, and the release of object save areas. So it can read lower than the real free space until the next allocation. Startup zeroes all variables after the directories, `WORDS.TOK`, and `OBJECT` are loaded, so `var(8)` is first meaningful after LOGIC 0's record is allocated [AGI 2.917 1000:106E, 1000:11BB].

## What is on the heap

From the bottom, in allocation order. Every caller of the allocator is listed in the citations; a scan of the raw code for near calls finds the same 13 sites.

| Order | Contents | Size | Lifetime | Source |
|---|---|---|---|---|
| 1 | Stack | 2,560 bytes (`0xA00`), filled with `0x73`, guard word `0xAAAA` at the bottom, base saved at `DS:0000` | Resident | [AGI 2.917 1000:0086] |
| 2 | `logdir`, `picdir`, `viewdir`, `snddir`, in that order | File size | Resident | [AGI 2.917 1000:4305, DS:1162] |
| 3 | `words.tok` | File size | Resident | [AGI 2.917 1000:0F73] |
| 4 | `object` | File size | Resident | [AGI 2.917 1000:0FC1] |
| 5 | Object table | 43 bytes per slot, allocated only once | Resident | [AGI 2.917 1000:1013] |
| 6 | LOGIC 0 record and data | 10 bytes, then the resource | Resident | [AGI 2.917 1000:0F8E] |
| 7 | Script buffer | 2 bytes per entry; see "The script buffer" | Resident | [AGI 2.917 1000:6FCE] |
| 8 | Menu records | 18 bytes per menu, 14 per item | Resident after `submit.menu` | [AGI 2.917 1000:9080, 1000:913A, 1000:9207] |
| 9 | Room resources, in load order | See below | Until released | |
| 10 | Object save areas | 16-byte node, plus cel width × height | Released and rebuilt around permanent changes | [AGI 2.917 1000:8FD0] |

The resident mark is set after LOGIC 0, after the script buffer is first allocated, and by `submit.menu` [AGI 2.917 1000:0F94, 1000:6FD7, 1000:9207]. Each sets it to the current next-free offset, so anything loaded by then also becomes permanent. Rows 7 and 8 can swap, depending on when a game runs its `submit.menu` and first `new.room`.

Resources are read in two steps: a small record, then the data at its full length from the VOL header [AGI 2.917 1000:2FAE]:

| Type | Record | List head | Fields |
|---|---|---|---|
| LOGIC | 10 bytes | `DS:096F` | Next, number, message count, start, scan start, messages [AGI 2.917 1000:119A] |
| VIEW | 5 bytes | `DS:0FF2` | Next, number, data [AGI 2.917 1000:3A28] |
| PICTURE | 5 bytes | `DS:1206` | Next, number, data [AGI 2.917 1000:4A6E] |
| SOUND | 14 bytes | `DS:1250` | Next, number, data, voice pointers [AGI 2.917 1000:508B] |

Lists are singly linked, and a new record goes at the tail. A failed read rolls next-free back to where the read began, then retries [AGI 2.917 1000:2FE0, 1000:2E32].

**Object save areas stay on top.** Save areas for animated objects live above all resources. Every load, discard, and other permanent change first releases them, newest first, then makes its change, then rebuilds them [AGI 2.917 1000:698D, 1000:69C7]. That is how a stack-only heap can gain a new resource while objects are on screen. From the call structure, the release restores the background under each object and the rebuild saves it and draws the object; the driver entries themselves are unread [AGI 2.917 1000:0307, 1000:045E]. `set.menu` and `set.menu.item` allocate without this bracket, so a menu built while save areas exist would land above them and be overwritten at the next release. Runtime only.

## Releasing memory

Three things release memory, and none of them fully agrees with the spec's rule that later resources are "automatically unloaded".

**`discard.pic` and `discard.view`** find the record and fail with an error if it isn't loaded: `0x15` for a picture, `1` for a view. Otherwise they cut the record and everything after it from that type's list, then move next-free back to the record [AGI 2.917 1000:4BCE, 1000:3F0D].

> [!conflict] 4-4 vs. AGI 2.917: later resources
> "When a resource is unloaded, all resources loaded after it ARE ALSO AUTOMATICALLY UNLOADED!" [4-4-Logic.html §COMMANDS TO LOAD AND UNLOAD RESOURCES]
>
> In 2.917 this is true of the memory, and of the lists only for the same type. Each list is cut separately, and nothing else is touched. So with `load.view(a); load.pic(b); discard.view(a);`, the memory for `b` is reclaimed, but its record stays on the picture list with a stale pointer. A later `load.pic(b)` sees it as loaded and does nothing, and `draw.pic(b)` decodes whatever now occupies that memory. The same applies to LOGIC and SOUND records. No check for objects still using a discarded view was found either. By reading only; queued for runtime.

**A temporary `call`.** A LOGIC that isn't loaded when it's called is loaded, run, and released on return: its link is cleared and next-free returns to its record [AGI 2.917 1000:12AE]. It is not recorded in the script buffer. So:

- It fits the same model as the discards, with the same gap. A view or picture loaded during the call has its memory reclaimed at return but stays on its list, stale. `var(8)` isn't updated either.
- A `new.room` inside such a call also returns through this cleanup. It then clears a link slot saved before the room change, which may now lie in reused memory or be LOGIC 0's own link, and moves next-free back to the old record, which can be above or below the new room's data. Runtime only. A LOGIC that was already loaded doesn't take this path.
- If an error unwinds through the call, this cleanup is skipped, but the error routine releases everything anyway.

**The full release** clears the object save lists without restoring backgrounds, zeroes the saved word at `DS:0A55`, moves next-free to the resident mark, and updates `var(8)` [AGI 2.917 1000:1485]. The list clears are separate [AGI 2.917 1000:10D0]: the view, sound, and picture list heads are zeroed, and LOGIC 0's next link is zeroed, so LOGIC 0 stays listed and the rest go. They are used like this:

- `new.room` keeps only what's below the mark, then reloads the room's LOGIC and, if `trace.info` chose one, the trace LOGIC [AGI 2.917 1000:1825, 1000:1832].
- The error routine does the same, then returns to the main loop, which reruns LOGIC 0 [AGI 2.917 1000:3FE8, 1000:01B0]. It doesn't touch the script buffer.
- `restart.game` releases and reinitializes the data [AGI 2.917 1000:24B8]; restore releases before replaying [AGI 2.917 1000:67A2].

No routine was found that calls `1000:144B` or `1000:145A`, a pair that saves and restores next-free using `DS:0A55`; a raw scan for near calls finds none.

## The script buffer

A log of what the room has loaded and drawn, which restore replays to rebuild the screen. Each entry is 2 bytes: a code, then a value [AGI 2.917 1000:6FEA].

| Code | Written by | Value | Written when |
|---|---|---|---|
| 0 | `load.logics`, `load.logics.v`, `new.room` | LOGIC | **Always**, even if already loaded [AGI 2.917 1000:117D] |
| 1 | `load.view`, `load.view.v` | View | Only if newly loaded [AGI 2.917 1000:3A1E] |
| 2 | `load.pic` | Picture | Only if newly loaded [AGI 2.917 1000:4A58] |
| 3 | `load.sound` | Sound | Only if newly loaded [AGI 2.917 1000:50A4] |
| 4 | `draw.pic` | Picture | Always [AGI 2.917 1000:4AF8] |
| 5 | `add.to.pic` family | 0, then 3 entries of raw arguments | Always, 4 entries in all [AGI 2.917 1000:2D52] |
| 6 | `discard.pic` | Picture | Always [AGI 2.917 1000:4BF3] |
| 7 | `discard.view` | View | Always [AGI 2.917 1000:3F35] |
| 8 | `overlay.pic` | Picture | Always [AGI 2.917 1000:4B60] |

Not recorded: the `call` auto-load, LOGIC 0's startup load, and `show.obj`, which turns recording off while it runs [AGI 2.917 1000:5E1B, 1000:5F5C].

**State.** Size in entries at `DS:0141`, 50 by default [AGI 2.917 DS:0141]; buffer at `DS:16FD`; write position at `DS:16FF`; count at `DS:0143`; replay position at `DS:1701`; recording enabled at `DS:1703`; most entries ever used at `DS:1705`, shown by `show.mem` as `max script`.

**Writing.** With `flag(7)` set, the routine does nothing. With recording off, it writes nothing but still updates the high-water value. Otherwise it checks the write position against buffer + 2 × size, unsigned. If full, it raises error `0x0B` with the high-water value as the extra information, so `var(17)` = 11 and `var(18)` = the most entries used, which unwinds to the main loop [AGI 2.917 1000:7015]. The entry isn't written and the buffer isn't reset, so each later recorded command fails the same way until the next `new.room`.

**Recording** starts off and is turned on by each `new.room` [AGI 2.917 1000:17A3]. So nothing is recorded before the first `new.room`.

**Allocation** happens at most once, the first time the reset routine runs with a size above zero and no buffer yet [AGI 2.917 1000:6FB5]. That is the first `script.size` or `new.room`, whichever comes first. It moves the resident mark. The reset then empties the log. `new.room` runs the reset after the heap release, so the buffer lands just above what's already resident.

`$AB` saves the count to `DS:05E1`, and `$AC` restores it and moves the write position to match [AGI 2.917 1000:70C4, 1000:70D6]. There's one level of saving, with no stack. [[interpreter/commands]] lists them as `push.script` and `pop.script`.

**Replay** resets the lists, turns recording off, releases the heap to the mark, and walks the entries from the start up to the saved count, dispatching each to the same routines used at run time. Code 5 reads its three extra entries. Unknown codes above 8 are skipped. A code 0 entry also restores that LOGIC's scan start, and a code 1 entry forces a reread if the view is already loaded. Recording then goes back on [AGI 2.917 1000:6755, 1000:7068, 1000:7085, 1000:684E]. Save and restore themselves are covered with the save and restore audit.

**SQ1** never uses `script.size`: walking all its LOGICs finds no `$8E` [SQ1 data check, memory unit, log 2026-11-01]. So its buffer holds the default 50 entries, 100 bytes, allocated at the first `new.room`.

## Spec layout against 2.917

The spec lists regions in order from the start of the data area [2-4-Interpreter.html], with "single heap" as its model. Fixed regions below are inside `AGIDATA.OVL`, of which 2.917 loads only the first `0x1E7` paragraphs, 7,792 bytes [AGI 2.917 1000:672A; overlay table entry]. The 128 non-zero bytes past that in the 8,192-byte file are never read.

| Spec region | Spec size | Address in 2.917 | Verdict |
|---|---|---|---|
| Data-area header | 2 bytes | `DS:0000` | **Contradicted.** See callout below |
| Game signature | 8 bytes | `DS:0002`, 7 bytes [AGI 2.917 1000:0E7E] | **Contradicted.** See callout below |
| Variables | 256 bytes | `DS:0009`, zeroed at setup [AGI 2.917 1000:106E] | Confirmed |
| Flags | 32 bytes | `DS:0109`, zeroed at setup [AGI 2.917 1000:7463] | Confirmed |
| Timers and special variables | unspecified | `DS:0129` onward, including the tick count and the control state | Refined; individual slots are in [[interpreter/variables-and-flags]] and [[interpreter/event-loop]] |
| Strings | 12×40 or 24×40 | `DS:020D`, 24×40 for 2.917 | Refined; see [[concepts/agi-data-types]] |
| Unknown | unspecified | `DS:05CD`–`DS:05E2`, partly identified: the cursor character at `DS:05D7`, and the `$AB` save at `DS:05E1` | Unread for the rest |
| UI strings | unspecified | First at `DS:05E3`, with most after the tables from `DS:09F5` | Refined: they fall on both sides of the tables |
| Command jump table | unspecified | Action table `DS:061D`, 174 entries; test table `DS:08F5`. The spec's ~181 and ~18 are other versions' counts | Refined |
| Encryption string | 12 bytes | `DS:08E9`, between the two tables | Confirmed |
| `AGIDATA.OVL` remainder | unspecified | Up to `DS:1E6F` | Refined: the file isn't wholly loaded |
| Unknown | unspecified | The stack, then the four directories | Refined: resolved by "What is on the heap" |
| `WORDS.TOK`, `OBJECT`, object table, LOGIC 0 | variable | Heap rows 3 to 6 | Confirmed, in this order |
| Other resources | variable | Heap row 9 | Confirmed; the mechanism is above |

> [!conflict] 2-4 vs. AGI 2.917: the first two regions
> The spec gives a 2-byte header holding "the length of the first data area" and an 8-byte signature, which would put variables at offset 10. In 2.917 variables are at `DS:0009`. `DS:0000` holds the stack base, read by the guard check in the timer [AGI 2.917 1000:008C, 1000:849E]. `set.game.id` copies up to 7 characters to `DS:0002` [AGI 2.917 1000:0E9D]. Saved games start their first block at `DS:0002` [AGI 2.917 1000:25D6], so the spec's header may describe a save-file length word instead of memory; that is unconfirmed here.

> [!conflict] 2-4 vs. AGI 2.917: one arena
> The earlier reading of the spec was a single-arena model where "code, fixed state, … and dynamically loaded resources all share one heap". In 2.917 code is in its own segment and the screen buffer in its own DOS block. Fixed data and the heap share only the `DS` segment, at separate addresses. The older note that heap direction and growth "would need to be recovered from a real DOS binary" is now answered: it grows upward, by bump allocation.

## See also

- [[interpreter/variables-and-flags]]: `var(8)`, `var(17)`, `var(18)`, `flag(7)`.
- [[interpreter/command-semantics]] §"Resource loading and unloading".
- [[entities/logic]]: LOGIC record and `call`.
- [[concepts/agi-data-types]]: string count by version and OBJECT-file naming.
- [[interpreter/view-objects]]: object table entries.
