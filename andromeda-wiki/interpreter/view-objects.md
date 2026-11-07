# VIEW Objects

VIEW objects are runtime instances of VIEW *resources*: animated screen sprites under interpreter control. Each object is one entry in the **object table**, which tracks position, animation state, direction, priority and collision flags. A **VIEW** is a resource file holding graphics. Several objects can share one VIEW, each with its own position and timing [6-2-VIEW.html §overview].

Everything cited to the binary comes from static reading of AGI 2.917 and applies to that version only. Claims cited `[2.917 runtime: …]` were also observed on the running interpreter; see [[sources/agi-2917-runtime]]. Handler-level behavior is in [[interpreter/command-semantics]] §"Objects".

## The table

Each entry is 43 bytes (`0x2B`) in 2.917, the same as the spec's SQ2 figure [AGI 2.917 1000:10E6, 1000:7E17; 6-2-VIEW.html §VIEW TABLE ENTRY]. The table has one entry more than the value of byte 2 of the decrypted OBJECT header. It is allocated once, filled with zeros, and each entry's byte 2 gets its object number [AGI 2.917 1000:0FE6–1000:1061]. `DS:0963` points at the table, and `DS:0965` at its end.

All pointers in the entry are near pointers into `DS`, including those to VIEW data on the heap. `SS` equals `DS` once the main loop is running [AGI 2.917 1000:00A3], so the `BP`-based accesses in the control check reach the same table [AGI 2.917 1000:55F8]. Comparisons on coordinates are signed 16-bit unless noted.

| Offset | Size | Field | Notes |
|---|---|---|---|
| `00` | 1 | Step time | Reload value for `01` [AGI 2.917 1000:154D]. |
| `01` | 1 | Step countdown | The motion and auto-loop routines only act when this is 1. It isn't a redundant copy, as the spec says [AGI 2.917 1000:0667, 1000:05C7, 1000:1542]. |
| `02` | 1 | Object number | The spec has this as unknown [AGI 2.917 1000:105E]. Used for border reporting, self-exclusion in collisions, and the EGO test in the control check. |
| `03` | 2 | `x` | Left edge of the cel. |
| `05` | 2 | `y` | Bottom row of the cel. |
| `07` | 1 | View number | |
| `08` | 2 | View data pointer | Zero when no view is set; cleared by `new.room` [AGI 2.917 1000:17C5]. |
| `0A` | 1 | Current loop | |
| `0B` | 1 | Loop count | Copied from byte 2 of the VIEW data [AGI 2.917 1000:3B22]. |
| `0C` | 2 | Loop pointer | Points at the loop's cel-count byte [AGI 2.917 1000:3C34]. |
| `0E` | 1 | Current cel | |
| `0F` | 1 | Cel count | |
| `10` | 2 | Cel pointer | Points at the cel's width byte [AGI 2.917 1000:3D81]. |
| `12` | 2 | Previous cel pointer | What the screen copy used last time. The spec's "duplicate of 10–11" holds only right after that copy [AGI 2.917 1000:0A57, 1000:56AF]. |
| `14` | 2 | Background save node | Set when the object is added to a draw list, and cleared by `new.room` [AGI 2.917 1000:9038, 1000:17CA]. |
| `16` | 2 | Previous `x` | Last settled position. See "Did not move" below. |
| `18` | 2 | Previous `y` | Also used for crossing detection in collisions. |
| `1A` | 2 | Width | From the cel, zero-extended [AGI 2.917 1000:3D8C]. |
| `1C` | 2 | Height | Same. |
| `1E` | 1 | Step size | Pixels per step. |
| `1F` | 1 | Cycle time | Reload value for `20` [AGI 2.917 1000:0607]. |
| `20` | 1 | Cycle countdown | Not a redundant copy either. At 0, the object never cycles [AGI 2.917 1000:05EF]. |
| `21` | 1 | Direction | 0 stopped, then 1 to 8 clockwise from north. The step tables confirm the compass [AGI 2.917 DS:0A59, DS:0A6B]. |
| `22` | 1 | Motion type | 0 normal, 1 wander, 2 follow EGO, 3 move to a point [AGI 2.917 1000:06AD]. |
| `23` | 1 | Cycle type | 0 normal, 1 end of loop, 2 reverse loop, 3 reverse cycle [AGI 2.917 1000:4960]. |
| `24` | 1 | Priority | See "Priority" below. |
| `25` | 2 | Flags | See below. |
| `27` | 1 | Parameter 1 | See "Shared parameters". |
| `28` | 1 | Parameter 2 | |
| `29` | 1 | Parameter 3 | |
| `2A` | 1 | Parameter 4 | |

> [!conflict] 6-2 vs. AGI 2.917, motion type 3
> [6-2-VIEW.html §VIEW TABLE ENTRY offset 22] glosses `3 = move.obj` as "follow another object". In 2.917, type 3 moves toward a fixed point held in the entry [AGI 2.917 1000:6C3D, 1000:1672]. Only type 2 follows anything, and it only follows EGO.

> [!conflict] 6-2 vs. AGI 2.917, doubled fields
> 6-2 says step time and cycle time are "stored redundantly", and that `12–13` duplicates `10–11`. In 2.917 each first byte is a reload value and each second is a live countdown, and `12–13` is the previous cel pointer.

## Flags

Word at offset `25`. Bit numbers match the spec, which left seven of them unknown [6-2-VIEW.html §View Flags].

| Bit | Mask | Meaning | Verdict |
|---|---|---|---|
| 0 | `0001` | Drawn. Set by `draw`, cleared by `erase` [AGI 2.917 1000:0A70, 1000:0B08] | New |
| 1 | `0002` | Ignore blocks: both the `block` box and conditional barriers [AGI 2.917 1000:06C1, 1000:568E] | Refined |
| 2 | `0004` | Fixed priority | Confirmed |
| 3 | `0008` | Ignore horizon | Confirmed |
| 4 | `0010` | Updating. Clear means the object is static and neither cycles nor moves [AGI 2.917 1000:0587, 1000:6A8F] | New |
| 5 | `0020` | Cycling | Confirmed |
| 6 | `0040` | Animated. Set by `animate.obj` [AGI 2.917 1000:0528] | New |
| 7 | `0080` | Last stopped by the `block` box. Written only, and nothing reads it [AGI 2.917 1000:078D, 1000:0786, 1000:06BA] | New |
| 8 | `0100` | On water | Confirmed |
| 9 | `0200` | Ignore objects. Either party having it skips the collision [AGI 2.917 1000:4721, 1000:4746] | Refined |
| 10 | `0400` | Repositioned: skip the next step, without skipping the bounds checks. Cleared after every step [AGI 2.917 1000:1568, 1000:1664] | New |
| 11 | `0800` | On land | Confirmed |
| 12 | `1000` | Skip the next cel change. Set by `end.of.loop` and `reverse.loop`, cleared by `set.cel` and `draw` [AGI 2.917 1000:48BE, 1000:6B08, 1000:3C81, 1000:0A86] | New |
| 13 | `2000` | Fixed loop. This suppresses the automatic choice, which the screen pass makes. `release.loop` computes nothing and only clears this bit [AGI 2.917 1000:0593, 1000:49C0] | Refined |
| 14 | `4000` | Did not move on its last step [AGI 2.917 1000:04BB] | New |
| 15 | `8000` | No use found in any instruction Ghidra recovered | Unread beyond that |

An object is **active** when bits 0, 4 and 6 are all set (mask `0x51`). Only active objects get motion, cycling or steps. `animate.obj` sets bits 4, 5 and 6, and `draw` sets bits 0 and 4. So a `draw` without `animate.obj` sets bit 0 but puts nothing on either draw list, because both lists require bit 6 [AGI 2.917 1000:691D, 1000:693E].

## Shared parameters

Offsets `27`–`2A` hold whatever the current motion or cycle mode needs, and those uses overlap:

| Mode | `27` | `28` | `29` | `2A` |
|---|---|---|---|---|
| `end.of.loop`, `reverse.loop` | Completion flag | | | |
| `wander` | Steps left | | | |
| `follow.ego` | Stop distance | Completion flag | Retreat distance left, `0xFF` on the first update | |
| `move.obj` | Target x | Target y | Saved step size | Completion flag |

The first row and the others share a byte. So `end.of.loop(n, f)` followed by `move.obj(n, x, ...)` leaves `x` in the slot that the loop end reads as its flag number. The loop end then sets `flag(x)`, not `flag(f)` [AGI 2.917 1000:6B12, 1000:6C46, 1000:4919]. SQ1 has this exact pair, in the same order and on the same object, in LOGICs 53 and 78 [SQ1 data check, log 2026-11-01]. Neither LOGIC's flow is proven to reach it. **Confirmed at runtime:** after `end.of.loop(1, 100)` and `move.obj(1, 80, …)`, the loop end set `flag(80)` and never `flag(100)` [2.917 runtime: end_of_loop_shares_parameter_1].

## What happens each cycle

The order comes from [[interpreter/event-loop]], steps 7 and 13.

**Motion pass, before LOGIC 0.** For each active object whose step countdown is 1, the motion type picks a new direction, and then the block box is checked [AGI 2.917 1000:0644, 1000:067A]. A step time of 0 keeps the countdown at 0, so such an object still steps every cycle but never gets this pass. Its motion mode and block check don't run [AGI 2.917 1000:1542]. **Confirmed at runtime:** with step time 0, an object under `move.obj` walked past its target, and one moving east kept its loop, where step time 1 stopped on the target and switched to the east loop [2.917 runtime: step_time_zero].

**Screen pass, after LOGIC 0.** Unless `text.screen` is active [AGI 2.917 1000:0241], the interpreter does the following:

1. For each active object, choose a loop if its loop isn't fixed and its step countdown is 1, then count down cycling. Reaching zero advances the cel and reloads the countdown [AGI 2.917 1000:0563].
2. If no object is active, stop here. Nothing below happens, including the clears in steps 4 and 8.
3. Erase the updating objects from the screen [AGI 2.917 1000:0614].
4. Clear `var(2)`, `var(4)` and `var(5)`, then step each active object whose countdown is due [AGI 2.917 1000:150A].
5. Rebuild the updating list in draw order and draw it [AGI 2.917 1000:0621].
6. Copy each object to the screen [AGI 2.917 1000:0488].
7. Update "did not move" for each object that has just reloaded its step countdown.
8. Clear EGO's on-water and on-land bits [AGI 2.917 1000:0639]. Those two commands therefore last one screen pass on EGO, and LOGIC must reissue them to keep them in force. Other objects keep them.

### Taking a step

When the countdown is due, the step works as follows [AGI 2.917 1000:150A]:

1. Add step size times the direction's offsets to the position, unless the object was just repositioned.
2. Apply the limits, which can record one border code. The later check wins: `x < 0` sets `x` to 0 with code 4, and `x + width > 160` sets `x` to `160 - width` with code 2. Then, for y, `y - height < -1` sets `y` to `height - 1` with code 1, and `y > 167` sets `y` to 167 with code 3. Otherwise, without ignore-horizon, `y <= horizon` sets `y` to `horizon + 1` with code 1.
3. Test the new position for a collision and against the control check. If either refuses it, restore the old position, drop the border code, and run the position fixer below.
4. If a border code survives, EGO writes it to `var(2)`, and any other object writes its number to `var(4)` and the code to `var(5)`. Then a `move.obj` in progress ends, as if it had arrived.
5. Clear the repositioned bit.

The horizon comparison is against the word at `DS:012D`. `set.horizon` stores its byte there, and `new.room` sets 36 [AGI 2.917 1000:7DC4, 1000:17F9].

### Position fixer

This routine makes a position legal [AGI 2.917 1000:5872]. `draw`, `add.to.pic`, the reposition commands and a refused step all call it.

First, an object at or above the horizon that doesn't ignore it moves to `horizon + 1`. If the position is then legal, the routine stops. Otherwise it walks an outward square spiral, starting left 1, down 1, right 2, up 2, left 3, and so on, stopping at the first legal position [AGI 2.917 1000:58C5–1000:5929, 1000:593E].

A position is legal when all of these hold: it's inside the screen limits and below the horizon as above, with no collision, and the control check accepts it [AGI 2.917 1000:594C, 1000:4719, 1000:55F0]. The walk has no limit, so a screen with no legal position hangs. **Confirmed at runtime:** with the horizon at 167, `draw` never returned, and every timer tick for five seconds interrupted the spiral at `5872`–`5995` [2.917 runtime: placement_with_no_legal_position]. It also reruns the control check at each trial position, which can change the object's automatic priority and EGO's flags.

### Collision with other objects

An object collides with another when all of the following hold [AGI 2.917 1000:4719]:

- Neither has ignore-objects set, the other is animated and drawn, and they're different objects.
- Their x ranges overlap, by the test `x + width >= other.x` and `x <= other.x + other.width`. Those bounds aren't reduced by 1, so objects one pixel apart still count as overlapping.
- They have the same `y`, or they have swapped vertical order since their previous positions. Offsets `16`/`18` hold those positions.

The second object needn't be updating, so a static object still blocks.

### The control check

`1000:55F0` decides whether the object's baseline may be at its current position, and it's also where automatic priority is set. For a non-fixed-priority object it first sets offset `24` from the y-to-priority table at `DS:1270`. See [[interpreter/control-lines]] and [[interpreter/priority-bands]] for the pixel rules.

### The block box

The box is the point `(x, y)` strictly inside the rectangle set by `block`, with its edges outside [AGI 2.917 1000:7B1F]. If an active object isn't ignoring blocks and has a direction, the check compares "inside now" with "inside after one step". When they differ, the object's direction becomes 0, and `var(6)` too for EGO [AGI 2.917 1000:06D9]. This stops an object crossing either way, so an object outside can't enter. The spec's "may not leave" covers only half of that. Only the point is tested, not the width, and a step large enough to jump over the box isn't caught.

### Did not move

For an object whose step countdown equals its step time, offsets `16`/`18` are compared with the current position [AGI 2.917 1000:04A4]. If they match, bit 14 is set. Otherwise they're updated and the bit clears. `wander` and `follow.ego` use this to detect being stuck.

## Choosing a loop

See [[interpreter/command-semantics]] §"`release.loop`". The choice uses exactly 2 or 3 loops, or exactly 4, from the tables at `DS:08D5` and `DS:08DF` [AGI 2.917 1000:059A].

## Cycling

When the cycle countdown fires, and the skip bit isn't set, the cel changes by cycle type [AGI 2.917 1000:48B3]:

- **Normal:** next cel, wrapping to 0.
- **End of loop:** next cel. On reaching the last cel, or if already there, finish.
- **Reverse loop:** previous cel. On reaching cel 0, or if already there, finish.
- **Reverse cycle:** previous cel, wrapping to the last.

Finishing sets the mode's flag (offset `27`), clears the cycling bit, sets the direction to 0 and the cycle type to normal. Clearing the direction is new and can stop a moving object. The new cel applies in the same pass.

Applying any cel also corrects the position. If the cel no longer fits, `x` or `y` moves it back on screen and sets the repositioned bit. For a `y` correction, the horizon also applies [AGI 2.917 1000:3CCB].

## Motion types

Each runs from the motion pass.

- **Wander:** counts offset `27` down. When it was already 0, or the object didn't move, it picks a random direction from 0 to 8 (0 stops it), and copies it to `var(6)` for EGO. While `27` is under 6 it draws a new count, giving 6 to 50 [AGI 2.917 1000:3F5A, 1000:3FA3].
- **Follow EGO:** compares the object's x center and `y` with EGO's x center and `y`, using the stop distance described below. When it gets within range, it sets direction 0 and motion 0, and sets the flag. After being stuck it picks a random non-zero direction and holds it for a random distance. That distance is one step if half the Manhattan distance to EGO plus one is no larger than a step. Otherwise it's at least one step and below that figure. It counts down by step size. The first update skips this [AGI 2.917 1000:0B36].
- **Move to a point:** see below. On arrival it finishes [AGI 2.917 1000:1672, 1000:16B9].

**Direction rule.** Each axis is classed as negative, near or positive by whether its difference is at most `-t`, inside `(-t, t)`, or at least `t`. The threshold `t` is the step size for `move.obj` and the stop distance for `follow.ego`. Two near axes give direction 0, and any other pair gives the matching compass direction [AGI 2.917 1000:16ED, 1000:172D, DS:0A7D]. So an object stops within `t` of its target on each axis without landing exactly on it.

**Finishing `move.obj`.** The saved step size returns, the flag is set, and motion goes to 0. For EGO, player control returns unconditionally and `var(6)` clears, even if the game had set program control beforehand [AGI 2.917 1000:16B9]. The direction is only cleared on the arrival path, so a border touch leaves it set.

## Priority

The automatic value is only written by the control check, so it changes when that check runs, not every cycle. `release.priority` only clears the bit, so `get.priority` straight after it returns the old value until the next check [AGI 2.917 1000:79E9, 1000:7A0E, 1000:5601].

## Draw order

There are two lists: static objects (animated and drawn but not updating) and updating objects. Static objects go on first and come off last. Each list draws from the lowest sort key up, where the key is `y`, or for a fixed-priority object `(priority - 5) * 12 + 48` [AGI 2.917 1000:0358, 1000:4CBB, 1000:69C7]. Ties draw in table order, so the lower-numbered object ends up underneath. The per-pixel priority rule belongs to [[interpreter/priority-bands]].

## Hot-spot

An object's position is the **bottom-left pixel** of its cel: the top row is `y - height + 1`, and the left column is `x` [AGI 2.917 1000:8FF7, 1000:56CD; 6-2-VIEW.html §overview]. The spec says `set.upper.left` moves this reference to the top-left corner, but in 2.917 that command does nothing [AGI 2.917 1000:4C15]. See [[interpreter/command-semantics]] §"`set.upper.left` argument-count conflict".

## Position tests

Four test commands check an object's position against a rectangle. These aren't collision tests despite this page's earlier heading. They take `(n, left, top, right, bottom)`, and the rectangle is inclusive on all four sides [6-2-VIEW.html §TEST COMMANDS AND VIEWS; AGI 2.917 1000:08C6–1000:0917]:

| Command | `x >= left` tests | `x <= right` tests |
|---|---|---|
| `posn` | `x` | `x` |
| `right.posn` | `x + width - 1` | `x + width - 1` |
| `center.posn` | `x + width / 2` | `x + width / 2` |
| `obj.in.box` | `x` | `x + width - 1` |

All four test `y` for the vertical. The values are computed and compared as unsigned bytes in 2.917, so a sum above 255 wraps [AGI 2.917 1000:0928]. Normal screen positions can't reach that.

## Lifecycle

- **`animate.obj`** sets flags to `0x70`, overwriting everything, and clears direction, motion type and cycle type. It does nothing if the object is already animated, and it leaves position, view and timings alone [AGI 2.917 1000:0521].
- **`new.room`** clears bits 0 and 6, sets bit 4, clears the view and cel pointers and offset `14`, and sets both step bytes, both cycle bytes and the step size to 1, for every entry [AGI 2.917 1000:17B6]. It leaves direction, motion type, cycle type and position as they were.
- **Restore** rebuilds objects from saved state. Offsets `02`/`03` hold temporary values during that rebuild, and `follow.ego`'s retreat byte is reset to `0xFF` [AGI 2.917 1000:6766–1000:68FB]. See [[interpreter/save-restore]].

The spec's "every frame during step 10 (rendering)" is wrong for 2.917, which has two passes as above. Its note that an interpreter doesn't have to copy this layout stands [6-2-VIEW.html §NOTE after table], with one exception: anything a saved game must round-trip depends on it. The shared parameters also behave differently if separated.

## See also

- [[entities/view]]: VIEW resource format on disk.
- [[interpreter/event-loop]]: the cycle that runs these passes.
- [[interpreter/priority-bands]]: y-to-priority table.
- [[interpreter/control-lines]]: pixel rules behind the control check.
- [[interpreter/command-semantics]]: per-command behavior.
- [[sources/6-1-view]], [[sources/6-2-view]], [[sources/agi-2917-binary]]: provenance.
