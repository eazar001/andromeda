# Source: 4-4-Logic.html

**Chapter:** 4.4 Description of the LOGIC Commands
**Path:** `AGI_Specifications/Specifications/4-4-Logic.html`
**Authors:** AGDS docs (Adventure Game Development System manual), translated from Russian by Vassili Bykov (`vbykov@cam.org`), with annotations from Lance Ewing.
**Last updated:** 4 December 1997
**Provenance:** "Retrived from the Internet Archive" (sic, in HTML)

## Scope

Prose behavioral documentation for the AGI LOGIC command set, mirroring the AGDS manual's chapter organization (real `<h3>` headers with hierarchical `I.2.6.x` numbering):

- §I.2.6.1 ARITHMETIC COMMANDS — increment/decrement saturation; assignn/assignv; addn/addv (overflow unresolved); subn/subv (underflow unresolved); lindirectn/lindirectv/rindirect; muln/mulv (overflow unresolved); divn/divv (division-by-zero unresolved); random; flag set/reset/toggle (literal and indirect).
- §I.2.6.2 COMMANDS TO LOAD AND UNLOAD RESOURCES — load/discard for LOGIC, PICTURE, VIEW, SOUND, with the auto-discard rule ("all resources loaded after an unloaded one are also unloaded") and the asymmetric command set (no `load.sound.v`, no `discard.logic`/`discard.sound`).
- §I.2.6.3 PROGRAM CONTROL COMMANDS — `new.room` eleven-step procedure with coordinated state writes to Var(0/1/2/4/5/16) and Flag(5); call / call.v / return; jump / set.scan.start / reset.scan.start.
- §I.2.6.4 OBJECT CONTROL COMMANDS — preconditions for movement (priority-0 unconditional barriers, priority-1 conditional, horizon, water/land); EGO as object 0.
- §I.2.6.4.1 OBJECT DESCRIPTION COMMANDS — animate.obj / unanimate.all; set.view / set.loop / fix.loop / release.loop (with two direction→loop tables); cel selection; priority management (the eleven-row y → priority auto-assignment table); positioning; cycling (start / stop / normal / reverse / end.of.loop / reverse.loop / cycle.time).
- §I.2.6.4.2 OBJECT MOTION CONTROL COMMANDS — horizon; block / unblock; obstacle observation flags; movement (move.obj, follow.ego, wander, normal.motion, set.dir/get.dir, distance, reposition*).
- §I.2.6.4.3 INVENTORY ITEM MANAGEMENT COMMANDS — get/drop/put for inventory items.
- §I.2.6.5 PICTURE RESOURCE MANAGEMENT COMMANDS — draw.pic / overlay.pic / show.pic; `add.to.pic` margin rule (with a gap at margin = 4); the load → draw → discard → show ordering constraint.
- §I.2.6.6 SOUND RESOURCE MANAGEMENT COMMANDS — sound / stop.sound.
- §I.2.6.7 TEXT MANAGEMENT COMMANDS — prevent/accept input; print / display / print.at; message format codes (`%v`, `%m`, `%0`, `%w`, `%s`, `%g`, with width specifier); cursor / attributes; clear / shake; status line.
- §I.2.6.8 STRING MANAGEMENT COMMANDS — set.string / get.string / word.to.string / parse / get.num.
- §I.2.6.9 INITIALIZATION COMMANDS — set.key; set.game.id (AGDS interpreter ID is `TQ`); script.size; trace.info / trace.on; log.
- §I.2.6.10 MENU MANAGEMENT COMMANDS — set.menu / set.menu.item / submit.menu / enable/disable.item / menu.input.
- §I.2.6.11 LOGICAL COMMANDS — §I.2.6.11.1 test commands (18 test opcodes with prose descriptions and the `said` matching algorithm); §I.2.6.11.2 general format of a logical command (AGDS `if_ ... else_ LABEL` syntax with precedence: not_ > conjunction > or_).
- §I.2.6.12 OTHER COMMANDS — configure.screen; obj.status.v; show.mem; show.pri.screen; show.obj (with VB / LE exchange clarifying it shows a VIEW, used for inventory-item pictures); shake.screen; echo.line / cancel.line; close.window; open.dialogue / close.dialogue; restart.game / save.game / restore.game; pause; quit; init.joy; toggle.monitor; upper.left.

## Informs

- **[[interpreter/priority-bands]]** — **new page**, the eleven y → priority bands from `release.priority`. Resolves the long-dangling `[[interpreter/priority-bands]]` forward-ref originally placed by the 2-1 ingest in [[interpreter/overview]] §"Screen objects and priority bands".
- **[[interpreter/command-semantics]]** — **new page**, selective behavioral coverage of high-value items from 4-4 (arithmetic edge cases, resource auto-discard, missing variants, `new.room` procedure, `release.loop` direction tables, base-point conflict, `set.upper.left` argument-count conflict between 4-3 and 4-4, mnemonic variants, `add.to.pic` margin gap at value 4, `said` algorithm corroborating 2-6, AGDS interpreter ID `TQ` for `set.game.id`).
- [[interpreter/overview]] — §"Screen objects and priority bands" updated: drop the `(agidev, unverified — exact band boundaries...)` qualifier now that the boundaries are nailed down; cross-link [[interpreter/command-semantics]] for opcode behavior.
- [[interpreter/commands]] — Notes section extended with link to [[interpreter/command-semantics]] for behavioral semantics; `$9B` row carries a conflict annotation pointing to the 4-4-vs-4-3 arity disagreement.
- [[interpreter/variables-and-flags]] — Var(0/1/2/4/5/16) and Flag(5) entries cross-link the `new.room` procedure; Var(9) entry cross-links the `said` algorithm in command-semantics; `(agidev, unverified)` tag on Var(9) is preserved (4-4 corroborates 2-6 — the algorithm is consistent across two AGDS translations — but consistency between two translations of the same source is not validation against working code).
- [[interpreter/input-parsing]] — note added that 4-4's `said` algorithm matches 2-6's verbatim (same AGDS source, same Bykov translator).
- [[concepts/agi-data-types]] — Controller section: confirm the latched-event semantics for `$0C controller(c)` test (the bound controller code from `set.key` or `menu.input` is what the test reads).

Deferred:

- Per-opcode prose for the ~150 commands whose 4-4 description is a straightforward restatement of their name (e.g., `stop.cycling(n)` disables cel animation for object n). Re-transcribing them into wiki pages would duplicate the chapter without adding value; `interpreter/command-semantics.md` surfaces only the non-obvious cases.
- Control-line semantics — 4-4 mentions priority-0/priority-1 barriers under §OBJECT CONTROL COMMANDS but does not document all four control-line colors (black / blue / green / cyan) in detail. The `[[interpreter/control-lines]]` forward-ref from overview remains dangling pending Group 4 (PICTURE) ingest.
- View-objects subsystem mechanics — 4-4 supplies direction → loop tables and the priority-band table but not the full screen-object model. The `[[interpreter/view-objects]]` forward-ref remains dangling pending Group 5 (VIEW) ingest.
- Debug-modes details — 4-4 covers `trace.on` / `trace.info` and Scroll-Lock activation in passing under §INITIALIZATION COMMANDS; not enough for a standalone page. The `[[interpreter/debug-modes]]` forward-ref remains dangling.

## Notes

**Same AGDS source as 2-6.** Both chapters are Vassili Bykov translations of the AGDS manual. 4-4's `said` algorithm matches 2-6's verbatim — corroboration that the wiki's transcription is faithful, not that the algorithm itself is validated against working code. 2-6 covered preprocessing + `said` matching; 4-4 covers the full command set. The two chapters together are the most substantial single source in the corpus.

**Two real conflicts surfaced.**

1. **Base-point conflict within 4-4 itself.** Line 363 (`get.posn` description) says "bottom **left** corner"; line 854 (`upper.left` description) says "bottom **right** corner". Documented as a `> [!conflict]` callout in [[interpreter/command-semantics]] §"Base-point semantics" — provisional reading favors bottom-left.

2. **`$9B set.upper.left` argument count: 4-3 vs 4-4 disagreement.** 4-3 lists 2 args (both `???`); 4-4 describes a 0-arg state toggle. Documented as a `> [!conflict]` callout in [[interpreter/command-semantics]] §"`set.upper.left` argument-count conflict" — provisional reading favors 4-4's 0-arg form.

**Mnemonic variants noted, not adopted.** 4-4 uses `assign` (not `assignn`), `load.logic` (not `load.logics`), `right.position` / `center.position` (not `right.posn` / `center.posn`), `upper.left` (not `set.upper.left`). The wiki uses 4-3's forms as canonical because they match AGI Studio and ScummVM conventions; 4-4's variants are recorded in [[interpreter/command-semantics]] §"Mnemonic variants across chapters" for cross-reference.

**Bykov / Ewing exchanges preserved.** The HTML carries explicit translator's-note brackets `[... --VB]` (Vassili Bykov) and `[... --LE]` (Lance Ewing). Several exchanges are preserved verbatim or paraphrased in [[interpreter/command-semantics]]:
- VB on `addn`/`addv`/`subn`/`subv`/`muln`/`mulv`/`divn` edge cases.
- VB / LE on missing `load_sound_v`, `discard_logic*`, `discard_sound*`.
- VB / LE on the `load.pic` literal-form-but-indirect-semantics asymmetry.
- VB / LE on whether `show.obj` shows a VIEW or an OBJECT (resolved: VIEW, used for inventory-item icons).

**Margin gap at value 4.** `add.to.pic`'s margin rule documents `margin ∈ {0,1,2,3}` (draws priority-margin rectangle) and `margin > 4` (no margin), leaving `margin == 4` unspecified — a small gap that may be a typo. Flagged in [[interpreter/command-semantics]] §`add.to.pic`.

**Scope decision: focused page over comprehensive prose dump.** Re-transcribing 4-4 in full would duplicate the chapter. [[interpreter/command-semantics]] takes the inverse approach: surface only what is non-obvious from [[interpreter/commands]]'s opcode signatures, leaving the chapter as the authoritative full-prose source. This matches the wiki's pattern of crystallizing high-value structure (tables, procedures, conflicts) and pointing at AGI_Specifications for full detail.

**Authorship snapshot updated.**

- 4-1: Lance Ewing, IA 20 Aug 1997.
- 4-2: Peter Kelly, IA 27 Jan 1998.
- 4-3: Peter Kelly, IA 3 Mar 1998.
- 4-4: AGDS manual translated by Vassili Bykov + annotations by Lance Ewing, IA 4 Dec 1997.

4-4 is the **third AGDS-Bykov-translated chapter** in the corpus (alongside 2-6 and possibly others). Three of four Group-3 chapters now ingested have non-Peter-Kelly primary authorship, reinforcing that "Peter Kelly's AGI Specifications" is more accurately "Peter Kelly's curated specifications corpus, multi-author".
