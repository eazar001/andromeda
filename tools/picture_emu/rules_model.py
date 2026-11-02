"""The PICTURE rules as andromeda-wiki states them for AGI 2.917, as a pure Python renderer.

`render` returns a 160x168 buffer of (priority << 4) | color. The flood fill is a plain
4-connected search, because the interpreter's span fill order can't be observed in its output.
"""
from collections import deque

W, H = 160, 168
BLANK = 0x4F
OP_MIN, END = 0xF0, 0xFF
MAX_X, MAX_Y = 0x9F, 0xA7
PEN_RECT, PEN_SPLATTER = 0x10, 0x20


class RulesModel:
    """One picture's drawing state. Each `_op_*` method returns the next stream byte."""

    def __init__(self, data, pens, buf=None, wrap_line=True):
        self.data, self.pos, self.pens = data, 0, pens
        self.buf = bytearray([BLANK]) * (W * H) if buf is None else bytearray(buf)
        self.mask, self.write = 0, 0xFF
        self.color, self.priority = 0, 0
        self.pen, self.texture = 0, 0
        self.x, self.y = 0, 0
        self.wrap_line = wrap_line

    def run(self):
        byte = self._next()
        while byte != END:
            byte = OPS[byte](self) if byte in OPS else self._next()
        return bytes(self.buf)

    def _next(self):
        byte = self.data[self.pos] if self.pos < len(self.data) else END
        self.pos += 1
        return byte

    def pset(self, x, y):
        i = y * W + x
        if i < len(self.buf):
            self.buf[i] = (self.buf[i] | self.mask) & self.write

    def _read_x(self):
        byte = self._next()
        return (None if byte >= OP_MIN else min(byte, MAX_X)), byte

    def _read_y(self):
        byte = self._next()
        return (None if byte >= OP_MIN else min(byte, MAX_Y)), byte

    def _read_xy(self):
        x, byte = self._read_x()
        if x is None:
            return None, None, byte
        y, byte = self._read_y()
        return (None, None, byte) if y is None else (x, y, byte)

    def line(self, x2, y2):
        x, y = self.x, self.y
        if y == y2 or x == x2:
            self._straight_line(x2, y2)
            return
        dx, dy = abs(x2 - x), abs(y2 - y)
        step_x, step_y = (1 if x2 > x else -1), (1 if y2 > y else -1)
        major = max(dx, dy)
        error_x = 0 if dx >= dy else dy // 2
        error_y = dx // 2 if dx >= dy else 0
        limit = 0xFF if self.wrap_line else 0xFFFF
        for _ in range(major):
            error_y = (error_y + dy) & limit
            if error_y >= major:
                error_y -= major
                y = (y + step_y) & 0xFF
            error_x = (error_x + dx) & limit
            if error_x >= major:
                error_x -= major
                x = (x + step_x) & 0xFF
            self.pset(x, y)
        self.x, self.y = x, y

    def _straight_line(self, x2, y2):
        x, y = self.x, self.y
        step_x, step_y = (x2 > x) - (x2 < x), (y2 > y) - (y2 < y)
        self.pset(x, y)
        while (x, y) != (x2, y2):
            x, y = x + step_x, y + step_y
            self.pset(x, y)
        self.x, self.y = x2, y2

    def _fill_test(self):
        """Return (mask, wanted value) for fillable pixels, or None if the fill does nothing."""
        if self.mask & 0x0F:
            return None if self.color == 0x0F else (0x0F, 0x0F)
        if self.mask & 0xF0:
            return None if self.priority == 0x40 else (0xF0, 0x40)
        return None

    def fill(self, start_x, start_y):
        test = self._fill_test()
        if test is None:
            return
        mask, wanted = test
        queue = deque([(start_x, start_y)])
        while queue:
            x, y = queue.popleft()
            if self.buf[y * W + x] & mask == wanted:
                self.pset(x, y)
                queue.extend(_neighbors(x, y))

    def plot(self, x, y):
        size = self.pen & 7
        left = min(max(2 * x - size, 0), 320 - 2 * size) >> 1
        top = min(max(y - size, 0), MAX_Y - 2 * size)
        register = self.texture | 1
        for row in range(2 * size + 1):
            for column in range(size + 1):
                if self.pen & PEN_RECT or self.pens[size][row] & (0x8000 >> (2 * column)):
                    drawn = True
                    if self.pen & PEN_SPLATTER:
                        register, drawn = splatter_step(register)
                    if drawn:
                        self.pset(left + column, top + row)

    def _op_set_color(self):
        self.color = self._next()
        self.mask |= 0x0F
        self.write = (self.write & 0xF0) | self.color
        return self._next()

    def _op_color_off(self):
        self.mask &= 0xF0
        self.write |= 0x0F
        return self._next()

    def _op_set_priority(self):
        self.priority = (self._next() << 4) & 0xFF
        self.mask |= 0xF0
        self.write = (self.write & 0x0F) | self.priority
        return self._next()

    def _op_priority_off(self):
        self.mask &= 0x0F
        self.write |= 0xF0
        return self._next()

    def _start_point(self):
        """Read and plot a segment's first point. Returns the byte that ended it, or None."""
        x, y, byte = self._read_xy()
        if x is None:
            return byte
        self.x, self.y = x, y
        self.pset(x, y)
        return None

    def _corner(self, vertical):
        stop = self._start_point()
        if stop is not None:
            return stop
        while True:
            value, byte = self._read_y() if vertical else self._read_x()
            if value is None:
                return byte
            self.line(self.x, value) if vertical else self.line(value, self.y)
            vertical = not vertical

    def _op_absolute(self):
        stop = self._start_point()
        if stop is not None:
            return stop
        while True:
            x, y, byte = self._read_xy()
            if x is None:
                return byte
            self.line(x, y)

    def _op_relative(self):
        stop = self._start_point()
        if stop is not None:
            return stop
        while True:
            byte = self._next()
            if byte >= OP_MIN:
                return byte
            delta_x, delta_y = (byte >> 4) & 7, byte & 7
            x = (self.x - delta_x if byte & 0x80 else self.x + delta_x) & 0xFF
            y = (self.y - delta_y if byte & 0x08 else self.y + delta_y) & 0xFF
            self.line(min(x, MAX_X), min(y, MAX_Y))

    def _op_fill(self):
        while True:
            x, y, byte = self._read_xy()
            if x is None:
                return byte
            self.fill(x, y)

    def _op_set_pen(self):
        self.pen = self._next()
        return self._next()

    def _op_plot(self):
        while True:
            if self.pen & PEN_SPLATTER:
                byte = self._next()
                if byte >= OP_MIN:
                    return byte
                self.texture = byte
            x, y, byte = self._read_xy()
            if x is None:
                return byte
            self.plot(x, y)


OPS = {
    0xF0: RulesModel._op_set_color,
    0xF1: RulesModel._op_color_off,
    0xF2: RulesModel._op_set_priority,
    0xF3: RulesModel._op_priority_off,
    0xF4: lambda model: model._corner(vertical=True),
    0xF5: lambda model: model._corner(vertical=False),
    0xF6: RulesModel._op_absolute,
    0xF7: RulesModel._op_relative,
    0xF8: RulesModel._op_fill,
    0xF9: RulesModel._op_set_pen,
    0xFA: RulesModel._op_plot,
}


def _neighbors(x, y):
    if x > 0:
        yield x - 1, y
    if x < W - 1:
        yield x + 1, y
    if y > 0:
        yield x, y - 1
    if y < H - 1:
        yield x, y + 1


def splatter_step(register):
    """Advance the shift register once. Returns (new register, whether the cell draws)."""
    carry = register & 1
    register >>= 1
    if carry:
        register ^= 0xB8
    return register, not register & 1 and bool(register & 2)


def render(data, pens, buf=None, wrap_line=True):
    return RulesModel(data, pens, buf, wrap_line).run()
