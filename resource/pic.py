from enum import Enum


class PicOp:
    pass


class OpType(Enum):
    NULLARY = 0
    UNARY = 1
    VARIABLE = 2


def decode_pic(payload: bytes) -> list[PicOp]:
    pass


def preprocess_pic_stream(payload: bytes) -> list[bytes]:
    nullary, unary = {0xF1, 0xF3, 0xFF, 0xFB, 0xFC, 0xFD, 0xFE}, {0xF0, 0xF2, 0xF9}
    rest = payload[:]
    bs = []

    while rest:
        b = rest[0]

        if b == 0xFF:
            break

        if b in nullary:
            op_type = OpType.NULLARY
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
