from typing import (
    SupportsInt, 
    TypeVar as _T
)

class Stack(list):
    def __init__(self, size=16) -> None:
        '''A 16 element stack implementing push/pop operations.'''
        super(Stack, self).__init__()
        self.size = size

    def reset(self) -> None:
        '''Destructively resets the stack.'''
        del self[:]

    def pop(self) -> _T:
        '''Pops a value off the stack and returns it.'''
        return super().pop()

    def push(self, __object: SupportsInt) -> None:
        '''Pushes a value onto the stack, up to size (default 16) elements.'''
        if len(self) < self.size:
            super().append(__object)
        else:
            raise IndexError("The stack is full.")

