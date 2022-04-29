# Priority Bands

The interpreter divides the screen into eleven horizontal **priority bands**, indexed 4–14, based on a screen object's `y` coordinate. Bands are not stored in PICTURE or VIEW resources — they are a runtime property assigned dynamically by `release.priority` (and overridden by `set.priority`) for any object that has not had an explicit priority set [4-4-Logic.html §OBJECT DESCRIPTION COMMANDS].

Priority controls per-pixel occlusion against the priority screen layer carried in [[entities/picture]] (PICTURE resources). A view-object pixel with priority *p* is occluded by any background pixel whose priority is greater than *p*. As an object moves down the screen its priority increases — the spec phrases this as "as an object moves down it approaches the viewer" [4-4-Logic.html].

Priorities 0–3 are reserved for non-band uses ([[interpreter/control-lines]] reserves the low priorities for control semantics: priority 0 = unconditional barrier, priority 1 = conditional barrier, priority 2/3 = other control roles documented in 4-4 §OBJECT CONTROL COMMANDS).

## y → priority table

[4-4-Logic.html §OBJECT DESCRIPTION COMMANDS, `release.priority`]

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

The screen is 168 pixels tall in AGI's coordinate system. The y=0..47 band (priority 4) covers the top of the screen above the horizon zone; y=156..167 (priority 14) covers the bottom strip closest to the viewer. Band heights are not uniform — the top band is 48 pixels tall, all other bands are 12 pixels tall.

## Related commands

Opcodes consuming or producing priority [4-3-Logic.html, [[interpreter/commands]]]:

- `$36 set.priority(S obj, num)` / `$37 set.priority.v` — override the auto-assigned band.
- `$38 release.priority(S obj)` — re-enable auto-priority based on the y-band table above.
- `$39 get.priority(S obj, var)` — read current priority into a variable.

The auto-assignment runs whenever the object's y-coordinate changes while priority is in release mode, so an object walking south progresses through bands 4 → 5 → 6 → ... → 14 as it descends.

## Control-line interaction (preview)

Black, blue, green, and cyan pixels in the priority screen act as **control lines** triggering interpreter behavior (motion blocking, alarm signaling, water confinement). The exact control-line semantics are documented separately in [[interpreter/control-lines]]; this page covers only the y→priority auto-assignment for view-objects.

## Implementation status

Validating these bands against working code requires either a LOGIC decoder + screen-renderer (none in `resource/`) or instrumented inspection of priority-screen output from a running AGI game. The y-band boundaries are nonetheless concrete numeric values, not under-specified spec prose — `(agidev, unverified)` applies as a process tag (no working renderer) rather than a content-quality tag.
