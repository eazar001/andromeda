class Screen:
    default = 0x00

    def __init__(self, width, height):
        self.screen = [[self.default for _ in range(width)] for _ in range(height)]

    def store(self, x, y, value):
        self.screen[y][x] = value

class VisualScreen(Screen):
    def __init__(self, width, height):
        self.default = 0x0F
        super().__init__(width, height)

class PriorityScreen(Screen):
    def __init__(self, width, height):
        self.default = 0x04
        super().__init__(width, height)

