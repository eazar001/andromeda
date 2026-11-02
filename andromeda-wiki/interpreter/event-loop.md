# Event Loop

The interpreter repeats one cycle forever. This page gives the order read from AGI 2.917 [AGI 2.917 1000:0150], then records where the spec's eleven-step version [2-2-Interpreter.html §Interpreter work cycle] differs. Other versions are unchecked.

## The cycle in 2.917

1. **Wait for the timer** until a tick counter reaches `var(10)`, then reset the counter [AGI 2.917 1000:7EB1]. The counter runs throughout the cycle, so time spent working counts toward the delay. With `var(10) = 0` there is no wait. Each unit is 1/20 second; see "Timer" below.
2. **Clear the 50-entry controller table** [AGI 2.917 1000:4C23].
3. **Clear `flag(2)` and `flag(4)`.**
4. **Read the joystick**, if one is present (`DS:15BD`), at most once every 9 timer ticks. It maps the axes to a direction from 0 to 8 and queues a direction event when the direction changes [AGI 2.917 1000:612B, 1000:62F7, 1000:6278]. A waiting keypress cancels the read.
5. **Drain queued input events**, first clearing `var(19)` and `var(9)`. If `menu.input` set its request in an earlier cycle, the menu runs here first and blocks the cycle, and its controller event is then drained like any other [AGI 2.917 1000:357C, 1000:358B]. See "Input events" below and [[interpreter/command-semantics]] §"Menus".
6. **Sync EGO's direction.** Under program control `var(6)` takes EGO's direction. Under player control EGO's direction takes `var(6)`.
7. **Update object motion.** Each object with all of flag bits `0x51` set, whose byte at offset 1 equals 1, gets its direction recalculated from its motion type (offset `0x22`, values 1–3), then a block check [AGI 2.917 1000:0644, 1000:067A].
8. **Snapshot the score and `flag(9)`**, and record a return point that the error routine jumps back to [AGI 2.917 1000:7E19, 1000:3FE8].
9. **Run LOGIC 0.** It returns 0 after `new.room`, a successful `restore.game`, or a confirmed `restart.game` [AGI 2.917 1000:24FE, 1000:268D, 1000:02FF]. In that case, clear `var(9)`, `var(5)`, `var(4)` and `flag(2)`, re-snapshot the score, and run LOGIC 0 again at once. Steps 1–8 are not repeated and objects are not updated in between.
10. **Set EGO's direction from `var(6)`**, regardless of control mode.
11. **Redraw the status line** if the score or `flag(9)` differs from its snapshot [AGI 2.917 1000:34BD].
12. **Clear `var(4)`, `var(5)`, `flag(5)`, `flag(6)` and `flag(12)`.**
13. **Update objects on screen** unless `DS:174D` is set, which `text.screen` sets [AGI 2.917 1000:0563, 1000:7603]. If any object is active, this pass also clears `var(2)`, `var(4)` and `var(5)` and EGO's on-water and on-land bits [AGI 2.917 1000:0610, 1000:150A, 1000:0639]. See [[interpreter/view-objects]] §"What happens each cycle".

## Timer

The interpreter reprograms the PC timer to 60 Hz (divisor `0x4DAE`) [AGI 2.917 1000:8380]. Each 60 Hz interrupt advances sound if one is playing. Every third interrupt also passes through to the BIOS, which triggers the interpreter's 20 Hz routine [AGI 2.917 1000:845A, 1000:8485, 1000:7E35].

The 20 Hz routine does the following:

- Advances an always-running tick count, which the joystick timing uses.
- Polls the keyboard and joystick buttons and queues what it finds [AGI 2.917 1000:449A, 1000:467F, 1000:6192].
- Unless paused, advances the `var(10)` counter and the clock: 20 ticks make one `var(11)` second, rolling over at 60 seconds, 60 minutes and 24 hours into `var(14)`.
- Checks a guard value at the bottom of the stack. If it was overwritten, the interpreter shows a message, waits for Esc and exits [AGI 2.917 1000:849E].

`pause`, `save.game` and `restore.game` set the paused state, so the clock and `var(10)` counter stop during those commands [AGI 2.917 1000:025C, 1000:275C, 1000:251B]. Menu, `status` and `print` waits don't set it, so the clock runs during them.

## Input events

Input arrives through a 20-entry ring queue of events, each with a type and a value. Events are added by the timer, not by the cycle. When the queue is full, the newest event is dropped [AGI 2.917 1000:44A9].

The keyboard poll sends each key through a direction lookup first: a direction key becomes a type 2 event, and anything else becomes type 1 [AGI 2.917 1000:467F]. The lookup itself (`46B6`) is unread.

The keyboard interrupt handler also filters keys before the BIOS sees them [AGI 2.917 1000:5F6E, 1000:5FF8]. Auto-repeats of the eight direction keys (scan codes `47h` to `51h` except `4Ah`, `4Ch`, `4Eh`) are discarded. Numeric-pad 5 with no Shift, Ctrl or Alt queues a type 2 event with value 0, which stops EGO. Ctrl-Alt with the left or right arrow calls driver entry `9749` to shift the screen. With `hold.key` on, releasing a direction key also queues that stop event.

The pump reads events until the queue is empty. On the way out, each type 1 key is checked against the `set.key` table, and a match turns it into a type 3 event. A key bound to a controller therefore never reaches `var(19)` or the input line [AGI 2.917 1000:4566]. On a Tandy, detected or forced with the `-t` switch, a second table can turn keys into directions [AGI 2.917 1000:46E8, 1000:40E5].

The pump then handles each event [AGI 2.917 1000:357C]:

- **Type 1, key:** the value goes to `var(19)`, and to the input line if input is enabled (`DS:05D3`). In Hercules mode any key except Enter goes through a separate prompt first.
- **Type 2, direction:** `var(6)` takes the value, or 0 if EGO is already moving that way, so pressing the same direction again stops EGO. Under player control, EGO's motion type also resets to 0.
- **Type 3, controller:** the value indexes the controller table entry to set.

## Input line

The input line handles keys as follows [AGI 2.917 1000:3652]:

- **Backspace (8):** removes the last character.
- **Line feed (10) and key 0:** ignored.
- **Enter (13):** if the line isn't empty, saves it as the previous line, parses it, then clears it. An empty line does nothing.
- **Anything else:** appended if the line is under its limit.

The limit is the smaller of `var(24)` and 40 minus the prompt's length, or the smaller of `var(24)` and 36 while `DS:0D07` is set, which `print` and `open.dialogue` both do. It's one less while a cursor character is set (`DS:05D7`) [AGI 2.917 1000:1F1F, 1000:38B4].

## Where the spec differs

> [!conflict] Spec cycle vs. AGI 2.917
> [2-2-Interpreter.html §Interpreter work cycle] differs from the binary as follows. None of these were caught before the audit.
>
> - **Contradicted, step 2:** the spec clears the keyboard buffer. 2.917 clears the controller table here, and queued key events survive to step 5.
> - **Contradicted, step 4:** the spec polls input once per cycle. 2.917 polls the keyboard in the 20 Hz timer routine and queues it, and the cycle only drains the queue. Only the joystick axes are read from the cycle.
> - **Contradicted, step 5:** the spec has program control read from `var(6)` and player control write into it. 2.917 does the reverse.
> - **Contradicted, step 7:** the spec checks the status line before LOGIC 0. 2.917 checks once, after it.
> - **Contradicted, step 11:** the spec tests for a room change at the end of the cycle, after the object update. 2.917 acts on it straight after LOGIC 0, before the update.
> - **Refined, step 1:** this is a wait for an elapsed count, not a fixed sleep. The 50 ms unit is confirmed.
> - **Refined, step 10:** the object update is skipped while `DS:174D` is set.

## When `new.room` takes effect

Immediately. The `new.room` core returns 0 [AGI 2.917 1000:1792]. A zero return stops the action loop, then the bytecode loop, then every calling LOGIC, so commands after `new.room` in the same LOGIC never run. This resolves the earlier conflict between 2-2 and 4-4 in favor of 4-4 for 2.917. See [[interpreter/command-semantics]] §"`new.room`" for the procedure itself.

## Transient-state discipline

- **`flag(2)`, `flag(4)`:** valid only from input handling in the same cycle.
- **`var(4)`, `var(5)`:** cleared after LOGIC 0 and on a room change.
- **`var(9)`, `var(19)`:** cleared every cycle before input is read. The spec implies `var(9)` only clears on a room change; that is contradicted for 2.917.
- **`var(2)`:** cleared by the room change and at the start of each screen pass's step phase, whenever an object is active, then set again if EGO touches a border [AGI 2.917 1000:151E, 1000:1646]. So a border touch reaches LOGIC in the next cycle and is replaced at the end of that cycle.
- **`flag(5)`:** set by the room change and cleared at step 12, so room setup sees it during the repeat LOGIC 0 run.

## See also

- [[interpreter/variables-and-flags]] — every reserved variable and flag used by the cycle
- [[interpreter/commands]] — command catalogue
- [[interpreter/view-objects]] — object state used by steps 7 and 13
- [[sources/agi-2917-binary]] — the binary source and routine map
