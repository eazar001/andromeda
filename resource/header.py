from dataclasses import dataclass


@dataclass
class ResourceHeader:
    signature: int
    vol: int
    length: int

    @classmethod
    def parse(cls, f, offset):
        f.seek(offset)
        signature = int.from_bytes(f.read(2), 'big')
        vol = int.from_bytes(f.read(1), 'big')
        length = int.from_bytes(f.read(2), 'little')

        return cls(signature, vol, length)
