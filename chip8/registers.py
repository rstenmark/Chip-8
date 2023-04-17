class Registers(object):
    def __init__(self) -> None:
        self._num_registers = 16
        self.reg = []
        # Append sixteen 0s
        for i in range(0, self._num_registers):
            self.reg.append(int(0))

    def __repr__(self) -> str:
        return self.reg.__repr__()

    def set(self, k: int, v: int) -> None: 
        self.reg[k] = v
    
    def get(self, k: int) -> int: 
        return self.reg[k]

    def reset(self) -> None:
        '''Sets all register values to 0.'''
        for i in range(0, self._num_registers):
            self[i] = int(0)