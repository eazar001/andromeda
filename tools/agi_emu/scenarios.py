"""Runtime scenarios for the wiki audit. Each returns a dict of observations.

Run all, or some by name:  uv run --with unicorn python tools/agi_emu/scenarios.py [name ...]
"""
import json
import struct
import sys

from logic import act, cond, if_, not_, program, said
from resources import picture, priority_line, view
from session import FIRST_RUN_FLAG, boot
from video import cga_mode4, hercules, pcjr_mode9, vga_mode13

DATA = 0x19F5
ENTRY = 0x2B
V_PIC, V_A, V_B, V_CYCLE = 200, 201, 202, 203
SETUP_FLAG = FIRST_RUN_FLAG - 1
SCENARIOS = {}


def scenario(fn):
    SCENARIOS[fn.__name__] = fn
    return fn


# ----- bytecode building blocks
def once(*parts):
    """Enter room 0 on the first cycle, as games do, then run `parts` on the second.

    `new.room` is what gives every object its step and cycle times of 1.
    """
    return (if_(not_(cond("isset", FIRST_RUN_FLAG)), act("set", FIRST_RUN_FLAG) + act("new.room", 0))
            + if_(not_(cond("isset", SETUP_FLAG)), act("set", SETUP_FLAG) + b"".join(parts)))


def show_picture(pic=1):
    return (act("assignn", V_PIC, pic) + act("load.pic", V_PIC) + act("draw.pic", V_PIC)
            + act("show.pic"))


def place(n, view, x, y, loop=0):
    return (act("load.view", view) + act("animate.obj", n) + act("set.view", n, view)
            + act("set.loop", n, loop) + act("position", n, x, y))


def every_cycle(*parts):
    return program(*parts, act("increment", V_CYCLE))


# ----- machine readers
def obj(m, n):
    """Selected fields of object n's table entry."""
    base = m.word(DATA, 0x0963) + ENTRY * n
    e = m.read(DATA, base, ENTRY)
    x, y = struct.unpack_from("<HH", e, 3)
    return {"x": x, "y": y, "view": e[7], "loop": e[0x0A], "loops": e[0x0B], "cel": e[0x0E],
            "cels": e[0x0F], "dir": e[0x21], "motion": e[0x22], "pri": e[0x24],
            "flags": struct.unpack_from("<H", e, 0x25)[0], "p1": e[0x27], "step_time": e[0],
            "step_count": e[1], "loop_ptr": struct.unpack_from("<H", e, 0x0C)[0]}


def slots(m):
    return (m.word(DATA, 0x0965) - m.word(DATA, 0x0963)) // ENTRY


def error(m):
    return {"var17": m.var(17), "var18": m.var(18)}


def at_cycle(m, n, read):
    """Call read(m) once, as LOGIC 0 starts with the cycle counter at n; returns the result list."""
    got = []
    m.probe(0x01BD, lambda m: not got and m.var(V_CYCLE) == n and got.append(read(m)))
    return got


def trace(m, ticks, every, read):
    """Run `ticks`, sampling `read(m)` every `every` ticks."""
    out = []
    for _ in range(ticks // every):
        m.run(every)
        out.append(read(m))
        if m.exit_code is not None:
            break
    return out


# ----- objects
@scenario
def end_of_loop_shares_parameter_1():
    """end.of.loop(1, 100) then move.obj(1, 80, ...): which flag does the loop end set?"""
    code = every_cycle(once(show_picture(), place(1, 9, 40, 120), act("draw", 1),
                            act("end.of.loop", 1, 100), act("move.obj", 1, 80, 120, 1, 101)))
    m = boot({0: code})
    m.run(30)
    after_setup = obj(m, 1)
    m.run(900)
    return {"p1_after_setup": after_setup["p1"], "flag100": m.flag(100), "flag80": m.flag(80),
            "flag101": m.flag(101), "final": obj(m, 1)}


@scenario
def set_loop_equal_to_count():
    """set.view(1, 89) then set.loop(1, 3), where VIEW 89 has 3 loops, then draw it."""
    code = every_cycle(once(show_picture(), place(1, 89, 60, 120), act("set.loop", 1, 3),
                            act("draw", 1)))
    m = boot({0: code})
    m.run(60)
    return {"object": obj(m, 1), **error(m), "cycles": m.var(V_CYCLE), "exit": m.exit_code}


@scenario
def draw_and_erase_one_past_table():
    """draw(n) and erase(n) where n is the slot count, compared with animate.obj(n)."""
    n = slots(boot().run(5))
    results = {"slots": n}
    for name in ("animate.obj", "draw", "erase"):
        m = boot({0: every_cycle(once(show_picture(), act(name, n)))})
        seen = trace(m, 120, 1, lambda m: (m.var(V_CYCLE), m.last_ip))
        results[name] = {**error(m), "cycles": [c for c, _ in seen[::20]],
                          "interrupted_at": sorted({f"{c:04X}:{i:04X}" for _, (c, i) in seen[-30:]})}
    return results


@scenario
def placement_with_no_legal_position():
    """Horizon at 167 leaves no legal row, so draw's position fixer has nowhere to stop."""
    code = every_cycle(once(show_picture(), place(1, 9, 60, 100), act("set.horizon", 167),
                            act("draw", 1)))
    m = boot({0: code})
    seen = trace(m, 300, 1, lambda m: m.last_ip)
    return {"cycles": m.var(V_CYCLE), "interrupted_at": sorted({f"{c:04X}:{i:04X}" for c, i in seen})}


@scenario
def step_time_zero():
    """EGO-free object with step time 0 and step time 1, moving east from loop 2."""
    def run(step_time, motion):
        code = every_cycle(once(show_picture(), place(1, 0, 40, 120, loop=2), act("draw", 1),
                                act("assignn", V_B, step_time), act("step.time", 1, V_B), motion))
        m = boot({0: code})
        return trace(m, 240, 40, lambda m: {k: obj(m, 1)[k] for k in ("x", "loop", "dir", "step_count")})
    east = act("assignn", V_A, 3) + act("set.dir", 1, V_A) + act("start.motion", 1)
    to_point = act("move.obj", 1, 70, 120, 1, 101)
    return {"east_t0": run(0, east), "east_t1": run(1, east), "move_t0": run(0, to_point),
            "move_t1": run(1, to_point)}


# ----- drawing
TEST_PIC, TEST_VIEW = 250, 250
CONTROL_ROWS = {100: 0, 101: 1, 102: 2, 103: 3}


def control_picture():
    """White, priority 4 everywhere, with full-width rows of priority 0 to 3 at y 100-103."""
    return picture(*(priority_line(p, 0, y, 159, y) for y, p in CONTROL_ROWS.items()))


def block_view(w, h, color=1, alpha=0):
    return view([([[color] * w for _ in range(h)], alpha)])


def pixels(m, x0, x1, y0, y1):
    buf = m.screen()
    return {y: [f"{buf[y * 160 + x]:02X}" for x in range(x0, x1)] for y in range(y0, y1)}


@scenario
def cel_over_control_rows():
    """A 10x10 blue cel at fixed priority 15 and 5, bottom row 106, over rows of priority 0-3."""
    out = {}
    for pri in (15, 5):
        code = every_cycle(once(show_picture(TEST_PIC), place(1, TEST_VIEW, 50, 106),
                                act("set.priority", 1, pri), act("draw", 1)))
        m = boot({0: code}, pictures={TEST_PIC: control_picture()}, views={TEST_VIEW: block_view(10, 10)})
        snap = at_cycle(m, 3, lambda m: pixels(m, 50, 53, 96, 108))
        m.run(60)
        out[f"priority_{pri}"] = {"object": {k: obj(m, 1)[k] for k in ("x", "y", "pri")}, "rows": snap}
    return out


@scenario
def add_to_pic_rewrites_ego_flags():
    """Set flags 0, 1, 3, then add.to.pic a cel on plain ground and on the priority 3 row."""
    out = {}
    cases = (("ground", 120, 15, True), ("water_row_pri15", 103, 15, True), ("water_row_pri9", 103, 9, True),
             ("no_add_to_pic", 120, 15, False))
    for label, y, pri, add in cases:
        call = act("add.to.pic", TEST_VIEW, 0, 0, 50, y, pri, 4) if add else b""
        code = every_cycle(once(show_picture(TEST_PIC), act("load.view", TEST_VIEW),
                                act("set", 0), act("set", 1), act("set", 3), call))
        m = boot({0: code}, pictures={TEST_PIC: control_picture()}, views={TEST_VIEW: block_view(10, 4)})
        tests, who = [], [None]
        m.probe(0x5663, lambda m: who.__setitem__(0, m.reg("ax") >> 8))
        m.probe(0x5685, lambda m: tests.append((who[0], m.reg("di"), m.flag(0), m.flag(3))))
        snap = at_cycle(m, 2, lambda m: (m.flag(0), m.flag(1), m.flag(3)))
        m.run(40)
        out[label] = {"flags_0_1_3_next_cycle": snap, "baseline_tests_obj_result_f0_f3": tests[:4]}
    return out


@scenario
def narrow_cel_margin_rectangle():
    """add.to.pic with margin 0 for cels 1, 2 and 3 pixels wide, 4 tall, bottom at y: bytes changed."""
    out = {}
    for width, y in ((3, 59), (2, 59), (1, 59), (2, 120)):
        code = every_cycle(once(show_picture(), act("load.view", TEST_VIEW)),
                           if_(cond("equaln", V_CYCLE, 2), act("add.to.pic", TEST_VIEW, 0, 0, 60, y, 9, 0)))
        m = boot({0: code}, views={TEST_VIEW: block_view(width, 4)})
        grab = lambda m: m.read(m.word(DATA, 0x1365), 0, 0x10000)
        old, new = at_cycle(m, 2, grab), []
        m.probe(0x01BD, lambda m: not new and m.var(V_CYCLE) == 4 and new.append(grab(m)))
        m.run(60)
        if not (old and new):
            out[f"width_{width}_y{y}"] = {"cycles": m.var(V_CYCLE), **error(m), "exit": m.exit_code,
                                          "last_ip": f"{m.last_ip[0]:04X}:{m.last_ip[1]:04X}"}
            continue
        changed = [i for i in range(0x10000) if old[0][i] != new[0][i]]
        rows = {r: new[0][r * 160 + 58:r * 160 + 64].hex(" ") for r in range(y - 5, y + 1)}
        out[f"width_{width}_y{y}"] = {"changed": len(changed), "outside_buffer": sum(i >= 26880 for i in changed),
                                      "first_last": [hex(changed[0]), hex(changed[-1])] if changed else None,
                                      "cycles": m.var(V_CYCLE), "rows_x58_63": rows}
    return out


def ego_scan_picture():
    """Row 110: priority 3 at x 50-52, priority 0 at 53-62; elsewhere priority 4."""
    return picture(priority_line(3, 50, 110, 52, 110), priority_line(0, 53, 110, 62, 110))


@scenario
def ego_flag0_after_black_stop():
    """EGO at y 109 steps south onto row 110, whose scan is cyan then black. flag(0) per test."""
    code = every_cycle(once(show_picture(TEST_PIC), place(0, TEST_VIEW, 50, 109), act("draw", 0),
                            act("assignn", 6, 5)),
                       if_(cond("isset", 0), act("increment", V_B)))
    m = boot({0: code}, pictures={TEST_PIC: ego_scan_picture()}, views={TEST_VIEW: block_view(10, 5)})
    tests, who = [], [0]
    m.probe(0x5663, lambda m: who.__setitem__(0, m.reg("ax") >> 8))
    m.probe(0x5685, lambda m: who[0] == 0 and tests.append((m.reg("di"), m.flag(0), m.flag(3))))
    m.run(120)
    return {"tests_result_flag0_flag3": tests[:12], "cycles_logic0_saw_flag0": m.var(V_B),
            "ego": {k: obj(m, 0)[k] for k in ("x", "y")}}


@scenario
def get_priority_after_position():
    """Object at y 60, then position(1, 50, 150) and get.priority at once and a cycle later."""
    code = every_cycle(once(show_picture(), place(1, 9, 50, 60), act("draw", 1),
                            act("assignn", V_B, 1)),
                       if_(cond("equaln", V_B, 3), act("get.priority", 1, 210)
                           + act("position", 1, 50, 150) + act("get.priority", 1, 211)),
                       if_(cond("equaln", V_B, 5), act("get.priority", 1, 212)),
                       if_(cond("greatern", V_B, 0), act("increment", V_B)))
    m = boot({0: code})
    m.run(60)
    return {"before": m.var(210), "straight_after": m.var(211), "two_cycles_later": m.var(212),
            "object": {k: obj(m, 1)[k] for k in ("y", "pri")}}


# ----- save and restore
ENTER, ESC = 0x1C0D, 0x011B


def key(ch):
    return ord(ch)


def drip(m, word, every, ticks):
    """Queue `word` every `every` ticks for the next `ticks` ticks."""
    m.type_keys(m.tick, [])
    for i in range(1, ticks // every + 1):
        m.type_keys(m.tick + every * i, [word])


def type_on_reach(m, off, words, gap=15):
    """When execution first reaches 1000:off, queue `words` one every `gap` ticks."""
    done = []
    def go(m):
        if not done:
            done.append(1)
            for i, w in enumerate(words):
                m.type_keys(m.tick + gap * (i + 1), [w])
    m.probe(off, go)


def save_program(extra=b""):
    """Set an ID and some state on setup; save on cycle 3; scramble and restore on cycle 6."""
    return every_cycle(
        once(act("set.game.id", 1), act("assignn", 220, 42), act("set", 220), extra),
        if_(cond("equaln", V_CYCLE, 3), act("save.game")),
        if_(cond("equaln", V_CYCLE, 6), act("assignn", 220, 99) + act("reset", 220) + act("restore.game")),
    )


SAVE_KEYS = [ENTER, ENTER, key("T"), ENTER, ENTER, ENTER]


@scenario
def save_file_bytes():
    """A real save of a one-LOGIC session: size, game ID offset, block lengths; then restore it."""
    m = boot({0: save_program()}, messages={0: ["SQ"]})
    type_on_reach(m, 0x2753, SAVE_KEYS)
    type_on_reach(m, 0x2512, [ENTER, ENTER, ENTER, ENTER])
    states = []
    m.probe(0x01BD, lambda m: states.append((m.var(V_CYCLE), m.var(220), m.flag(220), m.flag(12))))
    m.run(800)
    saved = {n: v for n, v in m.files.items() if "SG." in n}
    name, data = next(iter(saved.items())) if saved else (None, b"")
    blocks, pos = [], 31
    while pos + 2 <= len(data):
        n = struct.unpack_from("<H", data, pos)[0]
        blocks.append(n)
        pos += 2 + n
    return {"files": sorted(saved), "size": len(data), "description": data[:31].split(b"\0")[0].decode(),
            "id_at_33": data[33:40].split(b"\0")[0].decode(), "block_lengths": blocks,
            "block5": data[-blocks[-1]:].hex(" ") if blocks else None,
            "logic0_runs_cycle_var220_flag220_flag12": dedupe(states), "text": text_rows(m), **error(m)}


@scenario
def restore_keeps_logic0_scan_start():
    """LOGIC 0 sets its scan start, saves, resets the scan start, then restores.

    Before the scan start, var 231 counts cycles; after it, only var 232 counts. If the restore
    brings back the saved scan start, var 231 stops counting again afterwards.
    """
    code = program(
        if_(not_(cond("isset", 250)), act("set", 250) + act("set.game.id", 1) + act("new.room", 1)),
        act("increment", 231),
        if_(cond("equaln", 231, 2), act("set.scan.start")),
        act("increment", 232),
        if_(cond("equaln", 232, 4), act("save.game")),
        if_(cond("equaln", 232, 6), act("reset.scan.start")),
        if_(cond("equaln", 232, 9), act("restore.game")),
    )
    m = boot({0: code, 1: program()}, messages={0: ["SQ"]})
    type_on_reach(m, 0x2753, SAVE_KEYS)
    type_on_reach(m, 0x2512, [ENTER, ENTER, ENTER, ENTER])
    states = []
    m.probe(0x01BD, lambda m: states.append((m.var(231), m.var(232), m.flag(12))))
    applied = []
    m.probe(0x13BA, lambda m: applied.append(m.ds(m.word(m.reg("ss"), m.reg("bp") + 8) + 2)[0]))
    m.run(900)
    return {"logic0_runs_var231_var232_flag12": dedupe(states)[:20], "scan_table_applied_to": applied[:6],
            "table": m.ds(0x97D, 16).hex(" ")}


# ----- debug
@scenario
def trace_on_twice():
    """flag(10) set, trace.on, trace.on, then assignn(240, 7). Does the second skip a byte?"""
    code = every_cycle(once(act("set", 10), act("trace.info", 0, 2, 12), act("trace.on"), act("trace.on"),
                            act("assignn", 240, 7), act("assignn", 241, 9)))
    m = boot({0: code})
    drip(m, ENTER, 6, 600)
    m.run(600)
    return {"var240": m.var(240), "var241": m.var(241), **error(m), "cycles": m.var(V_CYCLE),
            "trace_state": m.word(DATA, 0x1D06), "text": text_rows(m)}


@scenario
def trace_window_output():
    """The trace window's text for a few traced commands, one trace.on."""
    code = every_cycle(once(act("set", 10), act("trace.info", 0, 2, 12), act("trace.on"),
                            act("assignn", 240, 7), act("increment", 240), act("set", 99)))
    m = boot({0: code})
    drip(m, ENTER, 6, 400)
    seen = []
    m.probe(0x8D44, lambda m: seen.append(text_rows(m).get(14)))
    m.run(400)
    return {"row14_at_each_trace_entry": dedupe(seen)[:12]}


def logic_list(m):
    out, p = [], m.word(DATA, 0x096F)
    while p and len(out) < 32:
        out.append(m.ds(p + 2)[0])
        p = m.word(DATA, p)
    return out


def play_to_room(m, room, ticks=12000):
    """Drive the real game with Enter every 2 seconds until var(0) reaches `room`."""
    drip(m, ENTER, 120, ticks)
    while m.var(0) != room and m.tick < ticks:
        m.run(60)
    m.keys.clear()
    m.run(240)
    return m


@scenario
def alt_d_in_sq1():
    """Real SQ1 in room 2: press ALT-D and see what the scripts do."""
    m = play_to_room(boot(), 2)
    before = {"flag10": m.flag(10), "flag190": m.flag(190), "logics": logic_list(m)}
    m.text.clear()
    m.type_keys(m.tick + 5, [0x2000])
    m.run(300)
    first = {"flag10": m.flag(10), "flag190": m.flag(190), "logics": logic_list(m), "text": text_rows(m)}
    m.text.clear()
    for i in range(3):
        m.type_keys(m.tick + 30, [ENTER])
        m.run(120)
    return {"room": m.var(0), "before": before, "after_alt_d": first,
            "after_enters": {"flag10": m.flag(10), "flag190": m.flag(190), "logics": logic_list(m),
                             "text": text_rows(m)}}


# ----- misc
@scenario
def quit_zero_confirmation():
    """quit(0) with no keys queued: plain, with flag(15) set, and with var(21) = 5."""
    out = {}
    for label, pre in (("plain", b""), ("flag15", act("set", 15)), ("var21", act("assignn", 21, 5))):
        m = boot({0: every_cycle(once(pre, act("quit", 0)))})
        m.run(300)
        out[label] = {"exit": m.exit_code, "text": text_rows(m)}
    return out


MENU_MSGS = ["Game", "Quit item", "Save item", "Info"]


def menu_program():
    """Menu 'Game' with two items (controller 5, and 6 disabled), opened from LOGIC 0 on cycle 3."""
    return every_cycle(
        once(act("set.menu", 1), act("set.menu.item", 2, 5), act("set.menu.item", 3, 6),
             act("set.menu", 4), act("set.menu.item", 2, 7), act("submit.menu"), act("disable.item", 6),
             act("set", 14)),
        if_(cond("equaln", V_CYCLE, 3), act("menu.input")),
        if_(cond("controller", 5), act("assignv", 241, V_CYCLE) + act("increment", 242)),
    )


@scenario
def menu_delivery_and_look():
    """menu.input on cycle 3; Down then Enter picks... the first item after a wrap. Which cycle sees it?"""
    m = boot({0: menu_program()}, messages={0: MENU_MSGS})
    m.write(0xF000, 0xFA6E, bytes([0xFF]) * (8 * 128))           # a solid ROM font: inverse 00, dither 55/AA
    glyphs = []
    m.probe(0x2AD1, lambda m: glyphs.append((m.bios.cursor, m.ds(0x0E9E, 8).hex()
                                             if m.reg("ax") & 0xFF == 0x80 else "char")))
    opened = []
    m.probe(0x930A, lambda m: opened.append(m.var(V_CYCLE)))
    type_on_reach(m, 0x930A, [ENTER], gap=20)
    m.run(400)
    by_pattern = {}
    for pos, g in glyphs:
        by_pattern.setdefault(g, set()).add(pos)
    return {"menu_opened_at_cycle": opened[:1], "controller5_seen_at_cycle": m.var(241),
            "cycles_it_was_seen": m.var(242), "text": text_rows(m),
            "glyph_rows_by_pattern": {g: sorted({r for r, _ in v}) for g, v in by_pattern.items()}}


@scenario
def hold_key_release_stops_ego():
    """EGO walking south on a held Down key; the key is released after 1 second."""
    out = {}
    for label, extra in (("without_hold_key", b""), ("with_hold_key", act("hold.key"))):
        code = every_cycle(once(show_picture(), place(0, 0, 60, 100), act("draw", 0), extra))
        m = boot({0: code})
        m.run(30)
        t0 = m.tick
        m.type_keys(t0, [0x5000])                             # BIOS word for Down
        m.press(t0, 0x50, 60)
        samples = trace(m, 180, 20, lambda m: (m.tick - t0, m.var(6), obj(m, 0)["y"]))
        out[label] = samples
    return out


# ----- displays
def display_program(pic=1, with_object=True):
    obj_part = (place(1, 9, 60, 120) + act("draw", 1)) if with_object else b""
    return every_cycle(once(show_picture(pic), obj_part))


def screen_vs_buffer(m, screen, colour_of, top=0):
    """Compare each AGI pixel of the buffer with the two display pixels it maps to."""
    buf, pairs, bad = m.screen(), {}, 0
    for y in range(168):
        for x in range(160):
            want = buf[y * 160 + x] & 0x0F
            got = tuple(colour_of(screen, 2 * x + i, y + top) for i in (0, 1))
            pairs.setdefault(want, set()).add(got)
            bad += got != (want, want)
    return bad, {k: sorted(v) for k, v in sorted(pairs.items())}


@scenario
def ega_display_matches_buffer():
    """EGA driver: after a full update, does every display pixel equal its buffer pixel?"""
    m = boot({0: display_program()})
    m.run(120)
    screen = m.ega.mode0d()
    bad, pairs = screen_vs_buffer(m, screen, lambda s, x, y: s[y][x])
    return {"mode": m.bios.mode, "mismatched_agi_pixels": bad, "colours_seen": sorted(pairs),
            "buffer_segment": hex(m.word(DATA, 0x1365)), "display_segment": hex(m.word(DATA, 0x1367))}


def compare(buf, screen, top=0):
    """Pixel pairs of a decoded screen against the buffer's visual nibbles."""
    pairs, bad = {}, 0
    for y in range(168):
        for x in range(160):
            want = buf[y * 160 + x] & 0x0F
            got = (screen[y + top][2 * x], screen[y + top][2 * x + 1])
            pairs.setdefault(want, set()).add(got)
            bad += got != (want, want)
    return bad, {k: sorted(v) for k, v in sorted(pairs.items())}


def hercules_check(m, buf, vram):
    """Rebuild the Hercules image from the buffer with the documented rule and compare."""
    patterns = m.ds(0x1D9E, 16 * 8)
    expect_bad = 0
    for y in range(168):
        for xb in range(80):
            a, b = buf[y * 160 + 2 * xb] & 0x0F, buf[y * 160 + 2 * xb + 1] & 0x0F
            for line in (0, 1):
                pa, pb = patterns[a * 8 + (y & 3) * 2 + line], patterns[b * 8 + (y & 3) * 2 + line]
                want = pa if a == b else (pa & 0xF0) | (pb & 0x0F)
                ly = 2 * y + line
                got = vram[(ly & 3) * 0x2000 + (ly >> 2) * 90 + 5 + xb]
                expect_bad += got != want
    return {"bytes_checked": 168 * 80 * 2, "mismatched": expect_bad}


@scenario
def other_display_paths():
    """Each other driver: BIOS mode, palette programming, and the display value per buffer colour."""
    cases = {
        "cga_composite_-c": dict(switches="-c", ega_present=False),
        "cga_rgb_-r": dict(switches="-r", ega_present=False),
        "vga_-v_type0": dict(switches="-v"),
        "vga_type8_-s_-v": dict(switches="-s -v"),
        "hercules_-h": dict(switches="-h", ega_present=False),
        "pcjr_model_FD": dict(model=0xFD, ega_present=False),
        "tandy_-t": dict(switches="-t", ega_present=False),
    }
    out = {}
    for label, kw in cases.items():
        m = boot({0: display_program()}, log_ports=True, **kw)
        frozen = at_cycle(m, 5, lambda m: (m.bios.mode, m.word(DATA, 0x1367), m.screen(),
                                           m.read(m.word(DATA, 0x1367), 0, 0x10000)))
        m.run(150)
        seg = m.word(DATA, 0x1367)
        r = {"var20": m.var(20), "var26": m.var(26), "bios_modes": sorted({v[2] for v in m.video_log if v[1] == 0}),
             "palette_calls": sorted({(v[1], v[2], v[3]) for v in m.video_log if v[1] in (0x0B, 0x10)})[:8],
             "ports_written": sorted({hex(p) for _, p, _ in m.port_log})[:16], "display_segment": hex(seg),
             **error(m), "exit": m.exit_code, "cycles": m.var(V_CYCLE)}
        if frozen:
            mode, seg, buf, vram = frozen[0]
            decode = {4: cga_mode4, 0x13: vga_mode13, 9: pcjr_mode9}.get(mode & 0x7F)
            if decode:
                r["mismatch"], r["pairs"] = compare(buf, decode(vram))
            elif kw.get("switches") == "-h":
                r["hercules"] = hercules_check(m, buf, vram)
        out[label] = r
    return out


# ----- memory
HEAP_NEXT, HEAP_BASE, HEAP_TOP = 0x0A4D, 0x0A4F, 0x0A53


def heap(m):
    w = lambda off: m.word(DATA, off)
    return {"base": hex(w(HEAP_BASE)), "next": hex(w(HEAP_NEXT)), "top": hex(w(HEAP_TOP)),
            "free": (w(HEAP_TOP) - w(HEAP_NEXT)) & 0xFFFF}


@scenario
def heap_base_and_top_wrap():
    """Where the heap lands; then VIEWs sized to end exactly at the 16-bit top, and one byte past it."""
    code = every_cycle(once(act("assignn", V_A, 1)), if_(cond("equaln", V_CYCLE, 3), act("load.view", TEST_VIEW)))
    probe = boot({0: code}, views={TEST_VIEW: bytes(16)})
    free = at_cycle(probe, 3, heap)
    probe.run(60)
    record = 5
    out = {"heap_at_load": free[0]}
    for label, size in (("exact_fit", free[0]["free"] - record), ("one_byte_more", free[0]["free"] - record + 1)):
        m = boot({0: code}, views={TEST_VIEW: (bytes([1, 1, 1, 0, 0, 7, 0]) + bytes(size))[:size]})
        m.run(200)
        out[label] = {"view_size": size, "heap_after": heap(m), "ds0": m.ds(0, 16).hex(" "),
                      "cycles": m.var(V_CYCLE), "text": text_rows(m)}
    return out


@scenario
def stale_record_after_mixed_discard():
    """load.view(a); load.pic(b); discard.view(a); load.view(c) reuses b's memory; draw.pic(b)."""
    code = every_cycle(
        once(act("load.view", 9), act("assignn", V_PIC, 1), act("load.pic", V_PIC), act("discard.view", 9),
             act("load.view", 0), act("load.pic", V_PIC), act("draw.pic", V_PIC), act("show.pic")))
    m = boot({0: code})
    m.run(60)
    clean = boot({0: every_cycle(once(show_picture(1)))}).run(60)
    lists = lambda m, head: [m.ds(p + 2)[0] for p in iter_list(m, head)]
    return {"picture_list": lists(m, 0x1206), "view_list": lists(m, 0x0FF2), **error(m),
            "screen_differs_from_clean_pic1": sum(a != b for a, b in zip(m.screen(), clean.screen())),
            "cycles": m.var(V_CYCLE)}


def iter_list(m, head):
    p, n = m.word(DATA, head), 0
    while p and n < 64:
        yield p
        p, n = m.word(DATA, p), n + 1


@scenario
def new_room_inside_temporary_call():
    """LOGIC 0 calls LOGIC 5 (not loaded), which does new.room(6); later cycles call LOGIC 6."""
    code = every_cycle(once(act("assignn", V_A, 1)),
                       if_(cond("equaln", V_CYCLE, 3) + not_(cond("isset", 246)), act("set", 246) + act("call", 5)),
                       if_(cond("greatern", V_CYCLE, 3), act("call", 6)))
    room6 = program(act("increment", 245))
    m = boot({0: code, 5: program(act("new.room", 6)), 6: room6})
    seen = []
    m.probe(0x01BD, lambda m: seen.append((m.var(V_CYCLE), m.var(0), [m.ds(p + 2)[0] for p in iter_list(m, 0x096F)],
                                           heap(m)["next"])))
    m.run(200)
    return {"cycle_room_logics_next": dedupe(seen)[:8], **error(m), "exit": m.exit_code, "crash": m.crash,
            "var245": m.var(245), "last_ip": f"{m.last_ip[0]:04X}:{m.last_ip[1]:04X}"}


@scenario
def set_menu_over_save_areas():
    """An object on screen, then set.menu, then a load that releases and rebuilds the save areas."""
    code = every_cycle(once(show_picture(), place(1, 9, 60, 120), act("draw", 1)),
                       if_(cond("equaln", V_CYCLE, 3), act("set.menu", 1) + act("set.menu.item", 2, 5)
                           + act("submit.menu")),
                       if_(cond("equaln", V_CYCLE, 5), act("load.view", 0)),
                       if_(cond("equaln", V_CYCLE, 7), act("set", 14) + act("menu.input")))
    m = boot({0: code}, messages={0: ["Game", "Quit item"]})
    type_on_reach(m, 0x930A, [ESC], gap=30)
    menu_text = at_cycle(m, 3, lambda m: None)
    heads = []
    m.probe(0x930A, lambda m: heads.append(m.word(DATA, 0x1D22)))
    m.run(400)
    return {"text": text_rows(m), **error(m), "exit": m.exit_code, "cycles": m.var(V_CYCLE), "crash": m.crash,
            "last_ip": f"{m.last_ip[0]:04X}:{m.last_ip[1]:04X}", "menu_opened": len(heads)}


@scenario
def fill_blows_the_stack():
    """A noisy fill picture known to need more than 2,560 bytes of stack, drawn by the whole interpreter."""
    import random
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "picture_emu"))
    from checks import noisy_fills
    from emulator import PictureEmu
    from session import DEFAULT_GAME
    emu, rng = PictureEmu(DEFAULT_GAME), random.Random(7)
    deepest = max(((emu.run(p) and emu.stack_used(), p) for p in noisy_fills(rng, 40)), key=lambda t: t[0])
    m = boot({0: every_cycle(once(show_picture(TEST_PIC)))}, pictures={TEST_PIC: bytes(deepest[1])})
    blown, low = [], []
    m.probe(0x84C1, lambda m: blown.append(m.tick))
    m.probe(0x5273, lambda m: low.append(m.reg("sp")))
    m.run(600)
    stack_base = m.word(DATA, 0x0000)
    return {"routine_stack_bytes": deepest[0], "exit": m.exit_code, "crash": m.crash,
            "stack_blown_reached_at_tick": blown[:1], "stack_base": hex(stack_base),
            "guard_word_now": hex(m.word(DATA, stack_base)),
            "stdout": bytes(m.stdout).decode("ascii", "replace"), "text": text_rows(m), "cycles": m.var(V_CYCLE)}


@scenario
def script_size_resize_and_zero():
    """script.size(10), one load, script.size(100), then 23 more loads; and script.size(0) then one load."""
    loads = b"".join(act("load.view", v) for v in (2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                                     20, 21, 22, 23, 24, 25))
    first = if_(not_(cond("isset", 248)), act("set", 248) + act("script.size", 10))
    m = boot({0: every_cycle(first, once(act("load.view", 0), act("script.size", 100), loads))})
    m.run(60)
    buf, used = m.word(DATA, 0x16FD), m.word(DATA, 0x0143)
    views = [p for p in iter_list(m, 0x0FF2)]
    first_view = min(views) if views else None
    z = boot({0: every_cycle(once(act("script.size", 0), act("load.view", 0)))})
    z.run(60)
    return {"buffer": hex(buf), "size": m.word(DATA, 0x0141), "used": used, "buffer_end_at_10": hex(buf + 20),
            "lowest_view_record": hex(first_view) if first_view else None,
            "entries_overlap_heap": used > 10 and first_view is not None and buf + 2 * used > first_view,
            "view_list_numbers": [m.ds(p + 2)[0] for p in views], **error(m),
            "size_zero": {**error(z), "used": z.word(DATA, 0x0143)}}


@scenario
def null_message_reads():
    """set.string, set.cursor.char and print with a message number past the count; word.to.string past the words."""
    s = lambda n: m.ds(0x020D + 40 * n, 40).split(b"\0")[0]
    code = every_cycle(once(act("set.game.id", 1), act("set.string", 1, 9), act("word.to.string", 2, 5),
                            act("set.cursor.char", 9), act("print", 9)))
    m = boot({0: code}, messages={0: ["SQ"]})
    drip(m, ENTER, 30, 300)
    m.run(200)
    return {"ds0000": m.ds(0, 10).hex(" "), "set_string": s(1).hex(" "), "word_to_string": s(2).hex(" "),
            "cursor_char": hex(m.ds(0x05D7)[0]), "print_text": text_rows(m), **error(m)}


@scenario
def shake_screen_by_monitor():
    """shake.screen(1) on each adapter: ticks it takes and the registers it writes."""
    cases = {"ega": {}, "cga_-c": dict(switches="-c", ega_present=False), "vga_-s_-v": dict(switches="-s -v"),
             "hercules_-h": dict(switches="-h", ega_present=False), "tandy_-t": dict(switches="-t", ega_present=False)}
    out = {}
    for label, kw in cases.items():
        code = every_cycle(once(show_picture()), if_(cond("equaln", V_CYCLE, 3), act("shake.screen", 1)))
        m = boot({0: code}, log_ports=True, **kw)
        span = []
        m.probe(0x7939, lambda m: span.append(m.tick))
        at_cycle(m, 4, lambda m: span.append(m.tick))
        m.run(300)
        if len(span) < 2:
            out[label] = {"span": span, "crash": m.crash}
            continue
        t0, t1 = span[0], span[1]
        writes = [(p, v) for t, p, v in m.port_log if t0 <= t <= t1]
        crtc = [v for p, v in writes if p in (0x3D5, 0x3B5)]
        idx = [v for p, v in writes if p in (0x3D4, 0x3B4)]
        out[label] = {"ticks_60hz": t1 - t0, "port_counts": {hex(p): sum(1 for q, _ in writes if q == p)
                                                             for p in sorted({p for p, _ in writes})},
                      "crtc_indexes": sorted(set(idx)), "crtc_values_first": crtc[:12],
                      "dac_writes": sum(1 for p, _ in writes if p == 0x3C9),
                      "bios_palette_calls": sum(1 for v in m.video_log if t0 <= v[0] <= t1 and v[1] == 0x10)}
    return out


@scenario
def show_pri_screen_on_ega():
    """While show.pri.screen waits, does the display show the priority nibbles as colours?"""
    code = every_cycle(once(show_picture(), place(1, 9, 60, 120), act("draw", 1)),
                       if_(cond("equaln", V_CYCLE, 4), act("show.pri.screen")))
    m = boot({0: code})
    before = at_cycle(m, 4, lambda m: m.screen())
    m.run(200)
    shown = m.ega.mode0d()
    pri = bytes(b >> 4 for b in before[0])
    bad, pairs = compare(bytes(pri), shown)
    m.type_keys(m.tick + 5, [ENTER])
    m.run(60)
    back, _ = compare(bytes(b & 0x0F for b in m.screen()), m.ega.mode0d())
    return {"mismatch_vs_priority_while_waiting": bad, "priorities_seen": sorted(pairs),
            "mismatch_vs_visual_after_key": back, "buffer_restored": m.screen() == before[0]}


@scenario
def toggle_monitor_on_cga():
    """CGA composite (-c) in room 1: toggle.monitor, then what changes on the adapter."""
    code = every_cycle(
        if_(not_(cond("isset", 250)), act("set", 250) + act("new.room", 1)),
        if_(cond("equaln", V_CYCLE, 1), show_picture()),
        if_(cond("equaln", V_CYCLE, 4), act("toggle.monitor")))
    m = boot({0: code, 1: program()}, switches="-c", ega_present=False, log_ports=True)
    before = at_cycle(m, 3, lambda m: (m.word(DATA, 0x1128), m.read(0xB800, 0, 0x4000), m.screen()))
    after = at_cycle(m, 6, lambda m: (m.word(DATA, 0x1128), m.read(0xB800, 0, 0x4000), m.screen()))
    m.run(300)
    regs = lambda port: [v for _, p, v in m.port_log if p == port]
    (mon0, vram0, buf0), (mon1, vram1, buf1) = before[0], after[0]
    _, pairs0 = compare(buf0, cga_mode4(vram0))
    _, pairs1 = compare(buf1, cga_mode4(vram1))
    return {"monitor_word": [mon0, mon1], "var26": m.var(26), "port_3d8": [hex(v) for v in regs(0x3D8)][:6],
            "port_3d9": [hex(v) for v in regs(0x3D9)][:6],
            "bios_palette_calls": [(v[1], hex(v[3])) for v in m.video_log if v[1] == 0x0B],
            "buffer_values_before": sorted(pairs0), "buffer_values_after": sorted(pairs1),
            "same_buffer": buf0 == buf1}


@scenario
def pen_picture_through_interpreter():
    """A picture using solid and splatter pens: the whole interpreter's buffer vs the routine alone."""
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "picture_emu"))
    from emulator import PictureEmu
    from session import DEFAULT_GAME
    pic = bytes([0xF0, 1, 0xF9, 0x07, 0xFA, 40, 40, 60, 60, 0xF0, 4, 0xF2, 9, 0xF9, 0x23, 0xFA, 0x41, 90, 90,
                 0x13, 120, 50, 0xF6, 0, 167, 159, 0, 0xFF])
    emu = PictureEmu(DEFAULT_GAME)
    alone = emu.run(pic)
    m = boot({0: every_cycle(once(show_picture(TEST_PIC)))}, pictures={TEST_PIC: pic})
    whole = at_cycle(m, 3, lambda m: m.screen())
    m.run(60)
    return {"differing_bytes": sum(a != b for a, b in zip(alone, whole[0])),
            "changed_from_blank": sum(b != 0x4F for b in alone)}


@scenario
def status_selection():
    """Three items carried, flag(13) set, var(25) = 2: Down then Enter, and Esc on its own."""
    out = {}
    for label, keys in (("down_enter", [0x5000, ENTER]), ("esc", [ESC])):
        code = every_cycle(once(act("get", 1), act("get", 2), act("get", 3), act("set", 13),
                                act("assignn", 25, 2)),
                           if_(cond("equaln", V_CYCLE, 3), act("status")))
        m = boot({0: code})
        type_on_reach(m, 0x3203, keys, gap=20)
        m.run(300)
        rows = {}
        for (r, c), (ch, _) in sorted(m.text.items()):
            rows.setdefault(r, []).append((c, chr(ch)))
        layout = {r: (cs[0][0], "".join(ch for _, ch in cs)) for r, cs in rows.items()}
        out[label] = {"var25": m.var(25), "rows_first_col_text": layout, "cycles": m.var(V_CYCLE)}
    return out


@scenario
def stale_record_after_temporary_call():
    """LOGIC 0 calls LOGIC 7 (not loaded), which loads VIEW 9; then LOGIC 0 loads VIEW 0."""
    code = every_cycle(once(act("call", 7), act("load.view", 0)))
    m = boot({0: code, 7: program(act("load.view", 9))})
    m.run(60)
    views = list(iter_list(m, 0x0FF2))
    return {"view_list": [(hex(p), m.ds(p + 2)[0]) for p in views], "logic_list": logic_list(m),
            "heap_next": heap(m)["next"], "var8": m.var(8), **error(m)}


@scenario
def priority_table_and_cycle_delay():
    """The y-to-priority table the interpreter builds, and cycles per second for var(10) = 0, 1, 2, 5."""
    m = boot({0: every_cycle(once(show_picture()))})
    m.run(60)
    table = m.ds(0x1270, 168)
    bands = {}
    for y, p in enumerate(table):
        bands.setdefault(p, [y, y])[1] = y
    rates = {}
    for delay in (0, 1, 2, 5):
        m = boot({0: every_cycle(once(show_picture(), act("assignn", 10, delay)))})
        first = at_cycle(m, 3, lambda m: m.tick)
        m.run(3 * 60 + 60)
        cycles = m.var(V_CYCLE)
        rates[delay] = {"cycles_in_run": cycles, "ticks": m.tick - first[0] if first else None}
    return {"bands_first_last_row": {p: tuple(r) for p, r in sorted(bands.items())}, "var10_rates": rates}


SAID_INPUTS = ["look", "look the", "look the rock", "look at the rock", "look rock", "the look"]
SAID_PATTERNS = {"look anyword": (2, 1), "look rol": (2, 9999), "look anyword rol": (2, 1, 9999),
                 "look rock": (2, 37), "anyword": (1,), "rol": (9999,)}


@scenario
def said_with_filler_words():
    """parse() of lines mixing group-0 fillers, against said() patterns using anyword (1) and rol (9999)."""
    out = {}
    for line in SAID_INPUTS:
        row = {}
        for name, words in SAID_PATTERNS.items():
            code = every_cycle(once(act("set.string", 1, 1), act("parse", 1),
                                    if_(said(*words), act("set", 240)), act("assignn", 241, 1)))
            m = boot({0: code}, messages={0: [line]})
            m.run(40)
            row[name] = m.flag(240) if m.var(241) else None
        out[line] = {**row, "flag2": m.flag(2), "var9": m.var(9)}
    return out


# ----- sound
def sound_program(n):
    return every_cycle(once(act("load.sound", n), act("sound", n, 230)))


def game_sound(n):
    """Voice 1 notes of SOUND n from the game files: (duration, divisor, attenuation)."""
    from session import game_files
    f = game_files()
    d = f["SNDDIR"]
    a, b, c = d[3 * n:3 * n + 3]
    vol, off = a >> 4, ((a & 0xF) << 16) | (b << 8) | c
    body = f[f"VOL.{vol}"][off + 5:]
    pos, notes = struct.unpack_from("<H", body, 0)[0], []
    while body[pos:pos + 2] != b"\xff\xff":
        dur, t3, t4, att = struct.unpack_from("<HBBB", body, pos)
        notes.append((dur, (t3 & 0x3F) << 4 | (t4 & 0x0F), att & 0x0F))
        pos += 5
    return notes


@scenario
def sound_chip_timing_on_tandy():
    """SOUND 1 on a Tandy: when each voice 1 tone write happens, against the note durations."""
    m = boot({0: sound_program(1)}, switches="-t", ega_present=False, log_ports=True)
    m.run(1200)
    writes = [(t, v) for t, p, v in m.port_log if p == 0xC0]
    tones = []
    for i, (t, v) in enumerate(writes):
        if v & 0xF0 == 0x80 and i + 1 < len(writes):          # voice 1 tone latch, then its data byte
            tones.append((t, (writes[i + 1][1] & 0x3F) << 4 | (v & 0x0F)))
    notes = game_sound(1)
    starts = [t for t, _ in tones]
    deltas = [b - a for a, b in zip(starts, starts[1:])]
    atts = [v & 0x0F for t, v in writes if v & 0xF0 == 0x90][:20]
    return {"notes": len(notes), "first_durations": [d for d, _, _ in notes[:12]], "tone_write_deltas": deltas[:12],
            "divisors_match": [d for _, d in tones[:12]] == [d for _, d, _ in notes[:12]],
            "voice1_attenuation_writes": atts, "flag230": m.flag(230)}


@scenario
def speaker_divisor_on_pc():
    """SOUND 1 on machine type 0: the PIT channel 2 divisor written for each note, against 12 x divisor."""
    m = boot({0: sound_program(1)}, switches="-p", log_ports=True)
    m.run(600)
    w = [v for t, p, v in m.port_log if p == 0x42]
    pit = [w[i] | w[i + 1] << 8 for i in range(0, len(w) - 1, 2)]
    notes = game_sound(1)
    return {"pit_divisors": pit[:8], "note_divisors_x12": [d * 12 for _, d, a in notes if a != 15][:8],
            "port_43": sorted({hex(v) for t, p, v in m.port_log if p == 0x43})}


def one_note_sound(duration, divisor, att):
    voice1 = struct.pack("<HBBB", duration, divisor >> 4, 0x80 | divisor & 0x0F, 0x90 | att) + b"\xff\xff"
    empty = b"\xff\xff"
    head = 8
    return struct.pack("<HHHH", head, head + len(voice1), head + len(voice1) + 2, head + len(voice1) + 4)         + voice1 + empty * 3


@scenario
def speaker_long_note_cutoff():
    """Type 0: one 150-tick note at attenuation 4. Does the speaker gate turn off part way through?"""
    m = boot({0: sound_program(TEST_SOUND)}, sounds={TEST_SOUND: one_note_sound(150, 0x100, 4)},
             switches="-p", log_ports=True)
    m.run(400)
    gate = [(t, v & 3) for t, p, v in m.port_log if p == 0x61]
    on = next((t for t, v in gate if v == 3), None)
    return {"gate_changes": dedupe_by(gate, 1)[:8], "on_at": on,
            "off_after_ticks": next((t - on for t, v in gate if on and t > on and v != 3), None),
            "flag230_done": m.flag(230)}


def dedupe_by(seq, i):
    out = []
    for s in seq:
        if not out or out[-1][i] != s[i]:
            out.append(s)
    return out


TEST_SOUND = 250


def dedupe(seq):
    out = []
    for s in seq:
        if not out or out[-1] != s:
            out.append(s)
    return out


def text_rows(m):
    rows = {}
    for (r, c), (ch, _) in sorted(m.text.items()):
        rows.setdefault(r, {})[c] = chr(ch)
    return {r: "".join(cols.get(c, " ") for c in range(40)).rstrip() for r, cols in rows.items()}


def main(names):
    for name in names or SCENARIOS:
        print(f"== {name}\n{json.dumps(SCENARIOS[name](), indent=1, default=str)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
