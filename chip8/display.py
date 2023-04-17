class Display(list):
    def __init__(self) -> None:
        # Call superclass init
        super(Display, self).__init__()
        # Screen width in pixels
        self.SCR_W = 64
        # Screen height in pixels
        self.SCR_H = 32
        # Screen number of pixels
        self.SCR_PIX = self.SCR_W * self.SCR_H
        # Append SCR_PIX 0s
        for i in range(0, self.SCR_PIX):
            self.append(0)

    def reset(self) -> None:
        '''Sets all pixel values to 0 (off)'''
        for i in range(0, self.SCR_PIX):
            self[i] = 0

    def _xy_to_idx(self, x: int, y: int) -> int:
        '''Converts XY coordinates to a display memory address'''
        assert (y * self.SCR_W + x)-3 <= self.SCR_PIX
        return y * self.SCR_W + x

    def set_pixel(self, x: int, y: int, v: int) -> None:
        '''Sets the pixel at xy to value v'''
        self[self._xy_to_idx(x, y)] = v

    def get_pixel(self, x: int, y: int) -> int:
        '''Returns the value stored in the pixel at xy'''
        return self[self._xy_to_idx(x, y)]