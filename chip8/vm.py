from parser import parse_file, ParsedInstruction
from cpu import CPU


class VM(object):
    def __init__(self):
        self.cpu = CPU()

    def reset(self) -> None:
        self.cpu.reset()

    def is_drawing(self) -> bool:
        """Returns the state of the draw flag on the CPU.

        The draw flag is set to True when the CPU is executing an instruction
        that modifies the display."""
        return self.cpu.df

    def get_current_instruction(self) -> ParsedInstruction:
        return self.cpu.mem[self.cpu.ip]

    def step(self, n_cycles: int = 1) -> None:
        self.cpu.step(n_cycles=n_cycles)

    def load(self, filename: str, offset=0x200):
        """Parses and loads a Chip8 program into memory at 0x200"""
        for idx, parsed_instruction in enumerate(parse_file(filename)):
            # Store ParsedInstruction objects at 2-byte alignments
            assert isinstance(parsed_instruction, ParsedInstruction) is True
            self.cpu.mem[2 * idx + offset] = parsed_instruction
