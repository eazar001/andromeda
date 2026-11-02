# Event Loop

The interpreter repeats one cycle forever. This page gives the order read from AGI 2.917 [AGI 2.917 1000:0150], then records where the spec's eleven-step version [2-2-Interpreter.html §Interpreter work cycle] differs. Other versions are unchecked.

## The cycle in 2.917

1. **Wait for the timer** until a tick counter reaches `var(10)`, then reset the counter [AGI 2.917 1000:7EB1]. The counter runs throughout the cycle, so time spent working counts toward the delay. With `var(10) = 0` there is no wait. The tick length is unread; the spec says 50 ms per unit.
2. **Clear the 50-entry controller table** [AGI 2.917 1000:4C23].
3. **Clear `flag(2)` and `flag(4)`.**
4. **Check the joystick**, apparently: a routine active only when `DS:15BD` is set, which posts a direction event when the reading changes [AGI 2.917 1000:612B]. Unread in detail.
5. **Drain queued input events**, first clearing `var(19)` and `var(9)` [AGI 2.917 1000:357C]. See "Input events" below.
6. **Sync EGO's direction.** Under program control `var(6)` takes EGO's direction. Under player control EGO's direction takes `var(6)`.
7. **Update object motion.** Each object with all of flag bits `0x51` set, whose byte at offset 1 equals 1, gets its direction recalculated from its motion type (offset `0x22`, values 1–3), then a block check [AGI 2.917 1000:0644, 1000:067A].
8. **Snapshot the score and `flag(9)`**, and record a return point that the error routine jumps back to [AGI 2.917 1000:7E19, 1000:3FE8].
9. **Run LOGIC 0.** If it returns 0, a room changed: clear `var(9)`, `var(5)`, `var(4)` and `flag(2)`, re-snapshot the score, and run LOGIC 0 again at once. Steps 1–8 are not repeated and objects are not updated in between.
10. **Set EGO's direction from `var(6)`**, regardless of control mode.
11. **Redraw the status line** if the score or `flag(9)` differs from its snapshot [AGI 2.917 1000:34BD].
12. **Clear `var(4)`, `var(5)`, `flag(5)`, `flag(6)` and `flag(12)`.**
13. **Update objects on screen** unless `DS:174D` is set, which `text.screen` sets [AGI 2.917 1000:0563, 1000:7603].

## Input events

The pump reads events until the queue is empty. Events have a type and a value [AGI 2.917 1000:357C]:

- **Type 1, key:** the value goes to `var(19)`, and to line input if input is enabled (`DS:05D3`).
- **Type 2, direction:** `var(6)` takes the value, or 0 if EGO is already moving that way, so pressing the same direction again stops EGO. Under player control, EGO's motion type also resets to 0.
- **Type 3, controller:** the value indexes the controller table entry to set.

## Where the spec differs

> [!conflict] Spec cycle vs. AGI 2.917
> [2-2-Interpreter.html §Interpreter work cycle] differs from the binary as follows. None of these were caught before the audit.
>
> - **Contradicted, step 2:** the spec clears the keyboard buffer. 2.917 clears the controller table here, and queued key events survive to step 5.
> - **Contradicted, step 5:** the spec has program control read from `var(6)` and player control write into it. 2.917 does the reverse.
> - **Contradicted, step 7:** the spec checks the status line before LOGIC 0. 2.917 checks once, after it.
> - **Contradicted, step 11:** the spec tests for a room change at the end of the cycle, after the object update. 2.917 acts on it straight after LOGIC 0, before the update.
> - **Refined, step 1:** this is a wait for an elapsed count, not a fixed sleep.
> - **Refined, step 10:** the object update is skipped while `DS:174D` is set.

## When `new.room` takes effect

Immediately. The `new.room` core returns 0 [AGI 2.917 1000:1792]. A zero return stops the action loop, then the bytecode loop, then every calling LOGIC, so commands after `new.room` in the same LOGIC never run. This resolves the earlier conflict between 2-2 and 4-4 in favor of 4-4 for 2.917. See [[interpreter/command-semantics]] §"`new.room`" for the procedure itself.

## Transient-state discipline

- **`flag(2)`, `flag(4)`:** valid only from input handling in the same cycle.
- **`var(4)`, `var(5)`:** cleared after LOGIC 0 and on a room change.
- **`var(9)`, `var(19)`:** cleared every cycle before input is read. The spec implies `var(9)` only clears on a room change; that is contradicted for 2.917.
- **`var(2)`:** cleared by the room change; no per-cycle reset is present in the main loop.
- **`flag(5)`:** set by the room change and cleared at step 12, so room setup sees it during the repeat LOGIC 0 run.

## See also

- [[interpreter/variables-and-flags]] — every reserved variable and flag used by the cycle
- [[interpreter/commands]] — command catalogue
- [[interpreter/view-objects]] — object state used by steps 7 and 13
- [[sources/agi-2917-binary]] — the binary source and routine map
