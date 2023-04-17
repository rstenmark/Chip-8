class Memory(list):
    def __init__(self, size) -> None:
        super(Memory, self).__init__()
        self.size = size
        # Append 0s up to size
        for i in range(0, size):
            self.append(0)
        

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
    