class Stack(list):
    def __init__(self) -> None:
        '''A 16 element stack implementing push/pop operations.'''
        super(Stack, self).__init__()
        self._size = 16

    def reset(self) -> None:
        '''Destructively resets the stack.'''
        del self[:]

    def pop(self) -> int:
        '''Pops a value off the stack and returns it.'''
        try:
            return super().pop()
        except IndexError:
            raise IndexError("The stack is empty.")

    def push(self, value: int) -> None:
        '''Pushes a value onto the stack, up to size (default 16) elements.'''
        if len(self) < self._size:
            super().append(value)
        else:
            raise IndexError("The stack is full.")
