"""Compare the real PICTURE routine with the models: pure picture generators plus counting."""
import random
from collections import namedtuple

import rules_model
import showpic_model
from emulator import game_pictures

Diff = namedtuple("Diff", "pictures differing_pictures visual_pixels priority_pixels")
BASE = [0xF0, 0x00, 0xF2, 0x01]
W, H = 160, 168


def game_corpus(emu, pens, game_dir):
    """Compare every game picture with each renderer. Returns {renderer name: Diff}."""
    renderers = {
        "rules": lambda d: rules_model.render(d, pens),
        "showpic as shipped": showpic_model.render,
        "showpic, stale check fixed": lambda d: showpic_model.render(d, stale_color=False),
        "showpic fixed, priority only over 4":
            lambda d: showpic_model.render(d, stale_color=False, pri_only_if_4=True),
    }
    truths = [(data, emu.run(data)) for _, data in game_pictures(game_dir)]
    return {name: _diff_all(truths, render) for name, render in renderers.items()}


def _diff_all(truths, render):
    visual = priority = differing = 0
    for data, truth in truths:
        out = render(data)
        v = sum((a ^ b) & 0x0F != 0 for a, b in zip(truth, out))
        p = sum((a ^ b) & 0xF0 != 0 for a, b in zip(truth, out))
        visual, priority, differing = visual + v, priority + p, differing + bool(v or p)
    return Diff(len(truths), differing, visual, priority)


def count_mismatches(emu, pens, pictures):
    return sum(emu.run(p) != rules_model.render(bytes(p), pens) for p in pictures)


def random_lines(rng, count):
    for _ in range(count):
        yield BASE + [0xF6, rng.randrange(W), rng.randrange(H), rng.randrange(W), rng.randrange(H), 0xFF]


def overflow_lines(rng, attempts):
    """Long diagonals whose major and minor lengths sum past the 8-bit error terms."""
    for _ in range(attempts):
        dx, dy = rng.randrange(90, W), rng.randrange(90, H)
        if dx + dy > 255:
            x1, x2 = (0, dx) if rng.random() < .5 else (dx, 0)
            y1, y2 = (0, dy) if rng.random() < .5 else (dy, 0)
            yield BASE + [0xF6, x1, y1, x2, y2, 0xFF]


def solid_plots():
    for size in range(8):
        for rect in (0, 0x10):
            for x in (0, 1, 2, 3, 4, 5, 80, 155, 156, 157, 158, 159):
                for y in (0, 1, 3, 7, 80, 160, 161, 164, 166, 167):
                    yield BASE + [0xF9, size | rect, 0xFA, x, y, 0xFF]


def splatter_plots():
    for texture in range(0xF0):
        for size in (0, 1, 3, 7):
            for rect in (0, 0x10):
                yield BASE + [0xF9, 0x20 | size | rect, 0xFA, texture, 80, 80, 0xFF]


def random_pictures(rng, count, max_ops=40):
    for _ in range(count):
        picture = []
        for _ in range(rng.randrange(3, max_ops)):
            op = rng.choice([0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF8, 0xF9, 0xFA, 0xFB, 0xFE])
            picture += [op] + _random_arguments(rng, op)
        yield picture + [0xFF]


def _random_arguments(rng, op):
    if op == 0xF0:
        return [rng.choice(list(range(16)) + [0x23, 0x45])]
    if op == 0xF2:
        return [rng.choice(list(range(16)) + [0x13, 0x24])]
    if op == 0xF9:
        return [rng.randrange(0, 0x40) | rng.choice([0, 0x40, 0x80])]
    if op in (0xF1, 0xF3):
        return []
    return [rng.randrange(0xF0) if rng.random() < .25 else rng.randrange(H) for _ in range(rng.randrange(14))]


def noisy_fills(rng, count):
    """Fills against scattered single-pixel walls, on each combination of layers."""
    setup = {"visual": ([0xF0, 0, 0xF3], [0xF0, 1]),
             "priority": ([0xF1, 0xF2, 0], [0xF2, 7]),
             "both": ([0xF0, 0, 0xF3], [0xF0, 1, 0xF2, 7])}
    for _ in range(count):
        density = rng.choice([.05, .1, .2, .3, .35, .4])
        width, height = rng.choice([(W, H), (40, 40), (159, 30), (30, 167)])
        walls, fill = setup[rng.choice(list(setup))]
        picture = list(walls)
        for y in range(height):
            for x in range(width):
                if rng.random() < density:
                    picture += [0xF6, x, y]
        picture += fill
        for _ in range(rng.randrange(1, 5)):
            picture += [0xF8, rng.randrange(width), rng.randrange(height)]
        yield picture + [0xFF]


def synthetic_families(seed, scale=1.0):
    """Yield (name, picture iterator) for each family; `scale` shrinks the random ones."""
    def scaled(n):
        return max(1, int(n * scale))

    rng = random.Random(seed)
    return [
        ("random lines", random_lines(rng, scaled(2000))),
        ("overflow-capable lines", overflow_lines(rng, scaled(600))),
        ("solid pen plots", (p for i, p in enumerate(solid_plots()) if i % max(1, round(1 / scale)) == 0)),
        ("splatter plots", (p for i, p in enumerate(splatter_plots()) if i % max(1, round(1 / scale)) == 0)),
        ("random pictures", random_pictures(rng, scaled(1500))),
        ("noisy fills", noisy_fills(rng, scaled(600))),
    ]


def showpic_line_diffs(pens, step=1):
    """Compare both line rules on every shape with lengths summing to at most 255."""
    rules = rules_model.RulesModel(b"", pens)
    port = showpic_model.Showpic(b"")
    total = differing = 0
    for dx in range(0, W, step):
        for dy in range(0, H, step):
            if dx + dy > 255 or (dx, dy) == (0, 0):
                continue
            for sign_x, sign_y in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                x1, y1 = (0 if sign_x > 0 else dx), (0 if sign_y > 0 else dy)
                x2, y2 = x1 + sign_x * dx, y1 + sign_y * dy
                total += 1
                differing += _rules_line(rules, x1, y1, x2, y2) != _port_line(port, x1, y1, x2, y2)
    return total, differing


def _rules_line(model, x1, y1, x2, y2):
    points = {(x1, y1)}
    model.pset = lambda x, y: points.add((x, y))
    model.x, model.y = x1, y1
    model.line(x2, y2)
    return points


def _port_line(port, x1, y1, x2, y2):
    points = {(x1, y1)}
    port.pset = lambda x, y: points.add((x, y))
    port.drawline(x1, y1, x2, y2)
    return points
