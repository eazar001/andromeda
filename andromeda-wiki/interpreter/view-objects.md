# VIEW Objects

VIEW objects are runtime instances of VIEW *resources* — animated screen sprites under interpreter control. Each object is bound to one entry in the **VIEW object table**, a heap-resident structure that tracks the object's position, animation state, direction, priority, and collision flags. This page documents the table entry structure as of SQ2 [6-2-VIEW.html §VIEW TABLE ENTRY].

Note the terminology distinction: a **VIEW** is a resource file (VIEWxxx.vxx) containing sprite graphics; a **VIEW object** is a runtime instance of a VIEW, with per-frame mutable state. Multiple VIEW objects can share the same VIEW resource — e.g., five crocodiles animated by the same resource but in different positions with independent cycle timings [6-2-VIEW.html §overview].

## View object table structure

In SQ2, each table entry is **43 bytes** (0x00–0x2A) [6-2-VIEW.html §VIEW TABLE ENTRY]. Other games may use different sizes; this value is interpreter-version-specific and not enumerated in the spec [6-2-VIEW.html].

| Offset | Bytes | Field | Notes |
|---|---|---|---|
| 0–1 | 2 | `step_time` (stored twice) | Denominator for movement speed: motion advances 1 unit every N cycles. Stored redundantly [6-2-VIEW.html §VIEW TABLE ENTRY offset 00-01]. |
| 2 | 1 | ?? | Purpose unknown [6-2-VIEW.html §VIEW TABLE ENTRY offset 02]. |
| 3–4 | 2 | `x_position` (LE) | Horizontal pixel coordinate; the object's hot-spot x [6-2-VIEW.html §VIEW TABLE ENTRY offset 03-04]. |
| 5–6 | 2 | `y_position` (LE) | Vertical pixel coordinate; the object's hot-spot y [6-2-VIEW.html §VIEW TABLE ENTRY offset 05-06]. |
| 7 | 1 | `current_view` | VIEW resource number (0–255) [6-2-VIEW.html §VIEW TABLE ENTRY offset 07]. |
| 8–9 | 2 | `view_data_ptr` (LE) | Pointer to start of VIEW resource data in memory [6-2-VIEW.html §VIEW TABLE ENTRY offset 08-09]. |
| 0A | 1 | `current_loop` | Loop index within the VIEW (0–254) [6-2-VIEW.html §VIEW TABLE ENTRY offset 0A]. |
| 0B | 1 | `num_loops` | Total number of loops in the current VIEW (0–254) [6-2-VIEW.html §VIEW TABLE ENTRY offset 0B]. |
| 0C–0D | 2 | `loop_data_ptr` (LE) | Pointer to the current loop's header in memory [6-2-VIEW.html §VIEW TABLE ENTRY offset 0C-0D]. |
| 0E | 1 | `current_cel` | Cel index within the current loop (0–254) [6-2-VIEW.html §VIEW TABLE ENTRY offset 0E]. |
| 0F | 1 | `num_cels` | Total number of cels in the current loop (0–254) [6-2-VIEW.html §VIEW TABLE ENTRY offset 0F]. |
| 10–11 | 2 | `cel_data_ptr` (LE) | Pointer to the current cel's data in memory [6-2-VIEW.html §VIEW TABLE ENTRY offset 10-11]. |
| 12–13 | 2 | `cel_data_ptr_copy` (LE) | Duplicate of offset 10–11 [6-2-VIEW.html §VIEW TABLE ENTRY offset 12-13]. Purpose unclear; may be used internally during rendering [6-2-VIEW.html §VIEW TABLE ENTRY]. |
| 14–15 | 2 | ?? | Purpose unknown [6-2-VIEW.html §VIEW TABLE ENTRY offset 14-15]. |
| 16–17 | 2 | `x_position_copy` (LE) | Copy of offset 3–4 (x_position). Updated during rendering [6-2-VIEW.html §VIEW TABLE ENTRY offset 16-17]. |
| 18–19 | 2 | `y_position_copy` (LE) | Copy of offset 5–6 (y_position). Updated during rendering [6-2-VIEW.html §VIEW TABLE ENTRY offset 18-19]. |
| 1A–1B | 2 | `x_size` (LE) | Width in AGI logical pixels [6-2-VIEW.html §VIEW TABLE ENTRY offset 1A-1B]. |
| 1C–1D | 2 | `y_size` (LE) | Height in AGI logical pixels [6-2-VIEW.html §VIEW TABLE ENTRY offset 1C-1D]. |
| 1E | 1 | `step_size` | Motion distance (pixels) per movement step [6-2-VIEW.html §VIEW TABLE ENTRY offset 1E]. |
| 1F–20 | 2 | `cycle_time` (stored twice) | Denominator for animation speed: cel advances every N cycles. Stored redundantly [6-2-VIEW.html §VIEW TABLE ENTRY offset 1F-20]. |
| 21 | 1 | `direction` (heading) | 8-way or 4-way direction code [6-2-VIEW.html §VIEW TABLE ENTRY offset 21]: `0 = stationary`, `1 = north`, `2 = northeast`, `3 = east`, `4 = southeast`, `5 = south`, `6 = southwest`, `7 = west`, `8 = northwest`. |
| 22 | 1 | `motion_type` | Animation motion state [6-2-VIEW.html §VIEW TABLE ENTRY offset 22]: `0 = normal.motion`, `1 = wander`, `2 = follow.ego`, `3 = move.obj` (follow another object). |
| 23 | 1 | `cycle_type` | Animation cel-sequencing mode [6-2-VIEW.html §VIEW TABLE ENTRY offset 23]: `0 = normal.cycle`, `1 = end.of.loop`, `2 = reverse.loop`, `3 = reverse.cycle`. |
| 24 | 1 | `priority` | Priority band 0–14 for depth-sorting against the PICTURE background. See [[interpreter/priority-bands]] [6-2-VIEW.html §VIEW TABLE ENTRY offset 24]. |
| 25–26 | 2 | `view_flags` (LE bitfield) | Runtime state flags; see layout below [6-2-VIEW.html §VIEW TABLE ENTRY offset 25-26]. |
| 27 | 1 | ?? | Purpose unknown; "storage for some view related command parameters" per spec [6-2-VIEW.html §VIEW TABLE ENTRY offset 27]. |
| 28 | 1 | ?? | Purpose unknown; same as offset 27 [6-2-VIEW.html §VIEW TABLE ENTRY offset 28]. |
| 29 | 1 | ?? | Purpose unknown; same as offset 27 [6-2-VIEW.html §VIEW TABLE ENTRY offset 29]. |
| 2A | 1 | ?? | Purpose unknown; same as offset 27 [6-2-VIEW.html §VIEW TABLE ENTRY offset 2A]. |

### View flags (offsets 25–26, 16-bit bitfield)

Bit layout [6-2-VIEW.html §VIEW TABLE ENTRY offset 25-26, View Flags table]:

| Bit | Meaning |
|---|---|
| 0 | ?? Purpose unknown [6-2-VIEW.html]. |
| 1 | `0 = observe blocks`, `1 = ignore blocks`. If set, collision detection with control-line barriers is disabled [6-2-VIEW.html]. |
| 2 | `0 = priority released`, `1 = priority fixed`. If set, priority value is locked and not auto-recomputed by the interpreter [6-2-VIEW.html]. |
| 3 | `0 = observe horizon`, `1 = ignore horizon`. If set, the horizon line (y boundary) is not enforced for this object [6-2-VIEW.html]. |
| 4 | ?? Purpose unknown [6-2-VIEW.html]. |
| 5 | `0 = stop cycling`, `1 = cycling`. If set, cel animation advances per cycle; if clear, animation is frozen [6-2-VIEW.html]. |
| 6 | ?? Purpose unknown [6-2-VIEW.html]. |
| 7 | ?? Purpose unknown [6-2-VIEW.html]. |
| 8 | `1 = view on water`. If set, object is treated as floating on the water surface [6-2-VIEW.html]. |
| 9 | `0 = observe objects`, `1 = ignore objects`. If set, collision detection against other VIEW objects is disabled [6-2-VIEW.html]. |
| 10 | ?? Purpose unknown [6-2-VIEW.html]. |
| 11 | `1 = view on land`. If set, object is treated as on solid ground (vs. water) [6-2-VIEW.html]. |
| 12 | ?? Purpose unknown [6-2-VIEW.html]. |
| 13 | `0 = loop released`, `1 = loop fixed`. If set, the loop index is locked and not auto-recomputed by `release.loop` [6-2-VIEW.html]. |
| 14 | ?? Purpose unknown [6-2-VIEW.html]. |
| 15 | ?? Purpose unknown [6-2-VIEW.html]. |

## Hot-spot reference point

By default, an object's position (`x_position`, `y_position` at offsets 3–6) refers to the **bottom-left pixel** of the cel's bounding box [6-2-VIEW.html §overview, hot-spot diagram]. The four collision-test commands reference different points within that bounding box relative to this hot-spot [6-2-VIEW.html §TEST COMMANDS AND VIEWS]:

```
      +-----------+
      | cel image |
      | ........ |
      | ........ |
      +-----------+
      X .........
      ^
      hot-spot (x, y)
```

The hot-spot can be overridden on a per-object basis by the `set.upper.left` command (changing the reference to the top-left corner). The argument count of this command is disputed across spec chapters — see [[interpreter/command-semantics]] §"`set.upper.left` argument-count conflict" for details.

## Collision-test commands

Four test commands check whether an object falls within a rectangular region on the screen. They differ in which point they test [6-2-VIEW.html §TEST COMMANDS AND VIEWS].

All commands take the form: `command(obj_num, left, top, right, bottom)` and return TRUE iff the tested point(s) fall within the rectangle.

### Test formula

For each command, define `X1` and `X2` as the x-coordinates tested:

| Command | X1 | X2 | Note |
|---|---|---|---|
| `posn` | `x` | `x` | Tests left edge of cel (the hot-spot itself). |
| `right.posn` | `x + xsize - 1` | `x + xsize - 1` | Tests right edge of cel. |
| `center.posn` | `x + (xsize / 2)` | `x + (xsize / 2)` | Tests horizontal center of cel. |
| `obj.in.box` | `x` | `x + xsize - 1` | Tests entire bottom row (left to right). |

All use `y` (the object's y_position) for the vertical test.

**Test condition** [6-2-VIEW.html §TEST COMMANDS AND VIEWS, test formula]:

```
TRUE iff  (X1 >= left) && (y >= top) && (X2 <= right) && (y <= bottom)
```

The rectangle is inclusive on all four bounds [6-2-VIEW.html §TEST COMMANDS AND VIEWS].

## Runtime object lifecycle

Objects are created and destroyed dynamically by LOGIC commands; the interpreter updates all resident objects every frame during the event loop's step 10 (rendering) — see [[interpreter/event-loop]] §"Step 10". The details of object state transitions (animating, stopping, deleting) are documented in [[interpreter/commands]] (e.g., `animate.obj`, `erase`, `draw`). This page covers the static table entry structure; the LOGIC-command semantics are separate.

## Notes

- The table entry size (43 bytes) is specific to SQ2. Other games or interpreter versions may use different sizes [6-2-VIEW.html §VIEW TABLE ENTRY, note].
- Many bytes marked "??" (purpose unknown) and several flag bits are not documented by the spec. These are candidates for reverse-engineering or cross-check against ScummVM's object-table implementation [6-2-VIEW.html §VIEW TABLE ENTRY].
- The chapter explicitly notes: "In attempting to write an AGI interpreter, you would not have to restrict yourself to this format, just as long as you store this information in some manner that the interpreter can have access to" [6-2-VIEW.html §NOTE after table]. This is a statement about implementation freedom, not a format requirement — custom implementations can reorganize the table, as long as all properties are available.

## See also

- [[entities/view]] — VIEW *resource* format (on-disk binary layout). Complementary to the runtime object table here.
- [[interpreter/event-loop]] — the per-frame cycle that updates all VIEW objects.
- [[interpreter/priority-bands]] — y → priority band table used by the `priority` field (offset 24).
- [[interpreter/command-semantics]] — `set.upper.left` base-point conflict and other object-manipulation opcode semantics.
- [[sources/6-1-view]] — VIEW resource format chapter (complementary on-disk spec).
- [[sources/6-2-view]] — this chapter's provenance.
