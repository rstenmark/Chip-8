from unittest import TestCase

from chip8.registers import Registers

sixteen = 16


class TestRegisters(TestCase):
    def setUp(self):
        self.registers = Registers()

    def tearDown(self):
        del self.registers

    def test_size(self):
        """The register "file" size is 16 elements"""
        self.assertEqual(self.registers._size, sixteen)

    def test_set(self):
        """All 16 registers are modifiable"""
        pass_sequence = [i for i in range(0, sixteen)]
        # Write to each index
        for idx in range(0, sixteen):
            self.registers.set(idx, idx)
        # Read directly back from each index
        for idx in range(0, sixteen):
            self.assertEqual(self.registers[idx], idx)

    def test_set_overflow(self):
        """Registers overflow to 0 when a value greater than one byte is written"""
        tgt_register = 0
        test_input = 0x101
        pass_value = 1
        # Set register 0 equal to 0x101 (a two byte value)
        self.registers.set(tgt_register, test_input)
        # It should overflow and become equal to 0x01
        self.assertEqual(self.registers[tgt_register], pass_value)

    def test_set_underflow(self):
        """Registers underflow to 255 when a value less than 0 is written"""
        tgt_register = 0
        test_input = -1
        pass_value = 0xFF
        # Set register 0 equal to -1
        self.registers.set(tgt_register, test_input)
        # It should underflow and become equal to 0xFF
        self.assertEqual(self.registers[tgt_register], pass_value)

    def test_get(self):
        """Registers read back their contents"""
        pass_sequence = [i for i in range(0, sixteen)]
        # Write to each index
        for idx in range(0, sixteen):
            self.registers.set(idx, idx)
        # Read back from each index using the method
        for idx in range(0, sixteen):
            self.assertEqual(self.registers.get(idx), idx)

    def test_reset(self):
        """All registers = 0 when reset is called"""
        pass_value = 0
        # Write any value to each index
        for idx in range(0, sixteen):
            self.registers.set(idx, 42)
        # Call reset method
        self.registers.reset()
        # Each register should contain 0 after reset
        for value in self.registers:
            self.assertEqual(value, pass_value)
