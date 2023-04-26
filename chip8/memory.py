from chip8.parser import ParsedInstruction

class Memory(list):
    def __init__(self, size) -> None:
        super(Memory, self).__init__()
        self.size = size
        # Append 0s up to size
        for i in range(0, size):
            self.append(0)

    def read_byte_unaligned(self, k: int) -> int:
        '''Reads a byte from a 2-byte unaligned (odd) address.
        If the provided address k is unaligned and self[k] == 0,
        this method will check self[k-1] for a ParsedInstruction.
        If it finds one, it will return the lower byte corresponding
        to self[k].'''
        p = self[k]
        if isinstance(p, ParsedInstruction):
            return p.bytes >> 8
        elif k - 1 >= 0 and isinstance(p, int) and isinstance(self[k - 1], ParsedInstruction):
            return self[k - 1].bytes & 0x00ff
        elif isinstance(p, int):
            return p


    def __setitem__(self, __i, __o) -> None:
        if __i < 0 or __i > self.size-1:
            # Do not allow out of bound writes
            # 0 <= __i <= self.size-1
            raise IndexError
        if type(__o) == type(int()):
            # clip __o to range
            # __o to 0 <= __o <= 255
            __o = max(min(__o, 255), 0)

        super(Memory, self).__setitem__(__i, __o)
    