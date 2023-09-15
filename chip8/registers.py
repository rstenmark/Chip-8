class Registers(list):
    def __init__(self) -> None:
        self._size = 16
        # Append sixteen 0s
        for i in range(0, self._size):
            self.append(int(0))

    def __repr__(self) -> str:
        s = ""
        for idx in range(0, self._size):
            s += f"{hex(idx)} = {self[idx]}, "
        return s[:-2]

    def __setitem__(self, key: int, value: int) -> None:
        super().__setitem__(key, value % 0x100)

    def __getitem__(self, key: int) -> int:
        return super().__getitem__(key)

    def set(self, k: int, v: int) -> None:
        super().__setitem__(k, v % 0x100)

    def get(self, k: int) -> int:
        return super().__getitem__(k)

    def reset(self) -> None:
        """Sets all register values to 0."""
        for i in range(0, self._size):
            self[i] = int(0)
