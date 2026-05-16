class Screen:
    default = 0x00

    def __init__(self, width, height, default=0x00):
        self.default = default
        self.buffer = [[self.default for _ in range(width)] for _ in range(height)]

    def store(self, x, y, value):
        self.buffer[y][x] = value

class VisualScreen(Screen):
    def __init__(self, width, height, default=0x0F):
        super().__init__(width, height, default=default)

class PriorityScreen(Screen):
    def __init__(self, width, height, default=0x04):
        super().__init__(width, height, default=default)

