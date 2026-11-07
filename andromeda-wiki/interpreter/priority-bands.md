# Priority Bands

The interpreter divides the screen into eleven horizontal **priority bands**, numbered 4 to 14, based on a screen object's `y` coordinate. An object's priority is a runtime value, taken from this table unless `set.priority` has fixed it [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS; AGI 2.917 1000:560E].

Priority controls per-pixel occlusion against the priority nibble of the screen buffer, which PICTURE resources fill in [[entities/picture]]. As an object moves down the screen its priority increases: "as an object moves down it approaches the viewer" [4-4-Logic.html].

Priorities 0 to 3 are not bands. They hold the control lines described in [[interpreter/control-lines]]. Values 0 to 2 are treated specially when a cel is drawn, while 3 is compared like any other priority [AGI 2.917 1000:9DE7].

## y → priority table

The table is 168 bytes at `DS:1270`, built at startup: 48 entries of 4, then 12 entries each for 5 through 14 [AGI 2.917 1000:55DA, 1000:5471]. This matches the spec [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS, `release.priority`].

| `y` range (inclusive low, exclusive high) | Priority |
|---|---|
| `0 ≤ y < 48`   | 4  |
| `48 ≤ y < 60`  | 5  |
| `60 ≤ y < 72`  | 6  |
| `72 ≤ y < 84`  | 7  |
| `84 ≤ y < 96`  | 8  |
| `96 ≤ y < 108` | 9  |
| `108 ≤ y < 120`| 10 |
| `120 ≤ y < 132`| 11 |
| `132 ≤ y < 144`| 12 |
| `144 ≤ y < 156`| 13 |
| `156 ≤ y < 168`| 14 |

The table the interpreter builds at runtime matches these bands exactly, rows 0 to 167 [2.917 runtime: priority_table_and_cycle_delay].

The screen is 168 rows tall. The lookup uses the low byte of `y` as an unchecked index, so it relies on the placement checks keeping `y` at 167 or less [AGI 2.917 1000:5607, 1000:5974].

## When automatic priority is assigned

Refined from "whenever `y` changes". Priority is reset from the table only inside the baseline test, when the object's fixed-priority bit is clear [AGI 2.917 1000:5601–1000:560E]. The one other assignment from the table is in `add.to.pic` [AGI 2.917 1000:5725]. A raw byte search of the interpreter found no other writes to the priority field apart from `set.priority` and `set.priority.v` [AGI 2.917 1000:79E0, 1000:7A79].

So the value follows `y` through motion steps and placement, but not at once:

- `position` and `position.v` only write the coordinates [AGI 2.917 1000:7B53, 1000:7B90], so `get.priority` straight after them returns the old value. Confirmed at runtime: an object at `y` 60 read priority 6 before and straight after `position(1, 50, 150)`, and 13 two cycles later [2.917 runtime: get_priority_after_position].
- Objects that aren't updating, such as those under `stop.update`, keep their value until something tests them again.

## How a cel pixel is compared

For each non-transparent cel pixel, the interpreter reads the priority already on screen at that position [AGI 2.917 1000:9DE2–1000:9DF4]:

- Screen priority 3 to 15: the pixel draws if the object's priority is greater than or equal to it, and the byte becomes the object's priority and the cel's color. Otherwise nothing changes.
- Screen priority 0 to 2: the search-downwards rule in [[interpreter/control-lines]] decides, and the control value stays in place if the pixel draws.

A tie draws, so an object drawn at the same priority as the background appears in front of it.

Only the low nibble of the object's priority field is used here [AGI 2.917 1000:9DB5]. If no pixel draws, EGO sets `flag(1)`; otherwise EGO clears it [AGI 2.917 1000:9E2C]. Drawing writes into the same buffer, so an object's priority is left in the priority nibble until its background is restored.

## Priority 15

Value 15 is the band closest to the viewer [5-2-PICTURE.html]. It sits outside the y table, so EGO can never reach it by walking [5-1-PICTURE.html; AGI 2.917 1000:55DA]. It is in real use: SQ1 draws it in 45 of 73 pictures (15.5% of all priority pixels), and its scripts call `set.priority(n, 15)` 32 times [SQ1 data check, log 2026-11-01].

Refined from "objects cannot move in front of it": objects with automatic priority can't, but an object fixed at 15 ties and draws over it. An object fixed at 15 also skips the baseline test [AGI 2.917 1000:562A], and `show.obj` and `add.to.pic` use that value during their own steps [AGI 2.917 1000:5EA1, 1000:2DEC].

## Draw order

Cels are drawn back to front. Each list of objects is sorted by a key, which is `y` for automatic priority and `(priority - 5) * 12 + 48` for fixed priority, so fixed priorities 5 to 14 sort with the top row of their band [AGI 2.917 1000:0397–1000:03AF, 1000:4CBB]. The lowest key draws first, and ties go to the earlier slot in the object table [AGI 2.917 1000:03EE].

Static objects are drawn before updating ones. Backgrounds are restored in the reverse order, updating objects first [AGI 2.917 1000:69C7, 1000:698D]. See [[entities/view]] §"Composition with screens".

## Related commands

Opcodes consuming or producing priority [4-3-Logic.html, [[interpreter/commands]]], all Confirmed against 2.917:

- `$36 set.priority(S obj, num)` and `$37 set.priority.v` store the byte and set the fixed-priority bit. The value isn't masked or range-checked [AGI 2.917 1000:79B9, 1000:7A41].
- `$38 release.priority(S obj)` clears the fixed-priority bit. The value itself stays until the next baseline test [AGI 2.917 1000:79E9].
- `$39 get.priority(S obj, var)` reads the stored value [AGI 2.917 1000:7A0E].

## Control-line interaction

Black, blue, green, and cyan pixels on the priority screen are **control lines**. See [[interpreter/control-lines]].
