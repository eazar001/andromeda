from enum import Enum
from dataclasses import dataclass


class PicOp:
    pass


class OpType(Enum):
    NULLARY = 0
    UNARY = 1
    VARIABLE = 2


@dataclass(frozen=True)
class SetVisualColor(PicOp):
    color: int

@dataclass(frozen=True)
class DisableVisualDraw(PicOp):
    pass

@dataclass(frozen=True)
class SetPriorityColor(PicOp):
    color: int

@dataclass(frozen=True)
class DisablePriorityDraw(PicOp):
    pass

@dataclass(frozen=True)
class YCorner(PicOp):
    coord: list[int]

@dataclass(frozen=True)
class XCorner(PicOp):
    coord: list[int]

@dataclass(frozen=True)
class AbsoluteLine(PicOp):
    coord: list[tuple[int, int]]

@dataclass(frozen=True)
class RelativeLine(PicOp):
    coord: list[int]

@dataclass(frozen=True)
class FloodFill(PicOp):
    coord: list[tuple[int, int]]

@dataclass(frozen=True)
class SetPenStyle(PicOp):
    style: int

@dataclass(frozen=True)
class PlotWithPen(PicOp):
    coord: list[int]

@dataclass(frozen=True)
class NoOp(PicOp):
    pass

@dataclass(frozen=True)
class EndOfPicture(PicOp):
    pass


def decode_pic(payload: bytes) -> list[PicOp]:
    return [decode_bytes(op) for op in preprocess_pic_stream(payload)]


def decode_bytes(bs: bytes) -> PicOp:
    op = bs[0]

    match op:
        case 0xF0:
            return SetVisualColor(color=bs[1])
        case 0xF1:
            return DisableVisualDraw()
        case 0xF2:
            return SetPriorityColor(color=bs[1])
        case 0xF3:
            return DisablePriorityDraw()
        case 0xF4:
            args = bs[1:]
            return YCorner(coord=list(args))
        case 0xF5:
            args = bs[1:]
            return XCorner(coord=list(args))
        case 0xF6 | 0xF8:
            args = bs[1:]
            x_clamp, y_clamp = 0x9F, 0xA7
            pairs = list(map(lambda p: (min(x_clamp, p[0]), min(y_clamp, p[1])), zip(args[::2], args[1::2])))
            return AbsoluteLine(coord=list(pairs)) if op == 0xF6 else FloodFill(coord=list(pairs))
        case 0xF7:
            args = bs[1:]
            return RelativeLine(coord=list(args))
        case 0xF9:
            return SetPenStyle(style=bs[1])
        case 0xFA:
            args = bs[1:]
            return PlotWithPen(coord=list(args))
        case 0xFB | 0xFC | 0xFD | 0xFE:
            return NoOp()
        case 0xFF:
            return EndOfPicture()
        case _:
            return NoOp()


def preprocess_pic_stream(payload: bytes) -> list[bytes]:
    nullary, unary = {0xF1, 0xF3, 0xFF, 0xFB, 0xFC, 0xFD, 0xFE}, {0xF0, 0xF2, 0xF9}
    rest = payload[:]
    bs = []

    while rest:
        b = rest[0]

        if b in nullary:
            op_type = OpType.NULLARY
            if b == 0xFF:
                bs.append(bytes([0xFF]))
                break
        elif b in unary:
            op_type = OpType.UNARY
        elif b >= 0xF0:
            op_type = OpType.VARIABLE
        else:
            op_type = OpType.NULLARY

        command, rest = parse(rest, op_type)
        bs.append(command)

    return bs


# returns a tuple with a bytes array for the full command and a bytes array for the remainder
# of the stream
def parse(bs: bytes, op_type: OpType) -> tuple[bytes, bytes]:
    if op_type == OpType.NULLARY:
        return bytes([bs[0]]), bs[1:]

    if op_type == OpType.UNARY:
        return bs[:2], bs[2:]

    command = [bs[0]]

    for b in bs[1:]:
        if b >= 0xF0:
            break

        command.append(b)

    return bytes(command), bs[len(command):]
