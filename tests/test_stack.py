from chip8.stack import Stack
from unittest import TestCase

sixteen = 16


class TestStack(TestCase):
    def setUp(self):
        self.stack = Stack()

    def tearDown(self):
        del self.stack

    def test_size_equals_16(self):
        """The size of the Stack is 16 elements"""
        self.assertEqual(self.stack._size, sixteen)

    def test_reset(self):
        """The Stack should be empty if it was reset while containing an element"""
        # Push any element onto stack
        self.stack.push(42)
        # Call stack reset method
        self.stack.reset()
        # Stack should be empty on reset
        self.assertEqual(len(self.stack), 0)

    def test_pop_occupied(self):
        """Popping from an occupied Stack returns the most recently appended element"""
        # Value expected when popping
        pass_value = 42
        # Push any elements onto stack
        self.stack.push(1)
        self.stack.push(pass_value)
        # Pull element off stack
        test_value = self.stack.pop()
        self.assertEqual(test_value, pass_value)

    def test_pop_empty(self):
        """Popping from an empty Stack causes an IndexError"""
        # Pop off empty stack
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_push(self):
        """Pushing an element positions it at the last (n+1th) index"""
        pass_value = 42
        self.stack.push(1)
        self.stack.push(42)
        self.assertEqual(self.stack[1], pass_value)

    def test_push_full_stack(self):
        """Attempting to push when the Stack is full causes an IndexError"""
        # Push 16 elements
        for i in range(0, sixteen):
            self.stack.push(i)
        # Pushing a 17th element causes an IndexError
        with self.assertRaises(IndexError):
            self.stack.push(42)
