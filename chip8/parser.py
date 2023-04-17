from typing import List

# A "syntax tree" (for lack of a better name) of the Chip8 opcode language.
# Pure opcodes with arguments stripped are obtained by traversing the tree
# in maximally 4 steps, 1 step for each 4-bit nibble of the 2-byte instruction
# from MSB to LSB.
# Steps where a nibble may be any value are keyed "any".
_syntax = {
    0x0: {
        0x0: {
            0xE: {
                0x0: 0x00E0,
                0xE: 0x00EE
            },
            "any": {
                "any": 0x0000
            }
        },
        "any": 0x0000
    },
    0x1: 0x1000,
    0x2: 0x2000,
    0x3: 0x3000,
    0x4: 0x4000,
    0x5: 0x5000,
    0x6: 0x6000,
    0x7: 0x7000,
    0x8: {
        "any": {
            "any": {
                0x0: 0x8000,
                0x1: 0x8001,
                0x2: 0x8002,
                0x3: 0x8003,
                0x4: 0x8004,
                0x5: 0x8005,
                0x6: 0x8006,
                0x7: 0x8007,
                0xE: 0x800E
            }
        }
    },
    0x9: 0x9000,
    0xA: 0xA000,
    0xB: 0xB000,
    0xC: 0xC000,
    0xD: 0xD000,
    0xE: {
        "any": {
            0x9: 0xE09E,
            0xA: 0xE0A1
        }
    },
    0xF: {
        "any": {
            0x0: {
                0x7: 0xF007,
                0xA: 0xF00A
            },
            0x1: {
                0x5: 0xF015,
                0x8: 0xF018,
                0xE: 0xF01E
            },
            0x2: 0xF029,
            0x3: 0xF033,
            0x5: 0xF055,
            0x6: 0xF065
        }
    }
}

def _search_opcode(instruction: int) -> int:
    '''Search for an opcode matching this raw instruction'''
    # Pointer to our spot in the search tree
    p = _syntax

    # For each 4-bit "nibble" of the 2 byte instruction
    for idx in range(0, 4):
        
        # Mask off four bits in a "sliding window" fashion
        # from MSB to LSB:
        mask: int = 0xf000 >> 4 * idx
        nibble: int = (instruction & mask) >> 12 - (4 * idx)

        try:
            # Try to use this nibble as a key at the current depth
            p = p[nibble]
            if type(p) == type(int()):
                # Found an opcode, break/return
                break
            elif type(p) == type(dict()):
                # Tree has more depth, descend
                continue
        except(KeyError):
            if "any" in p.keys():
                # Nibble in this position can be any value
                # Tree has more depth, descend
                p = p["any"]
                if type(p) == type(int()):
                    # Break if pointer resolved to int
                    break
            else:
                # Word is program data or malformed, do nothing
                p = instruction
                break

    return p

class ParsedInstruction(object):
    '''Contains the raw bytes, extracted opcode, and argument bitmasks for
    a parsed instruction.'''
    def __init__(self, bytes: int):
        self.bytes = bytes
        self.opcode: int = _search_opcode(bytes)
        self.nnn = bytes & 0b0000_1111_1111_1111
        self.n =   bytes & 0b0000_0000_0000_1111
        self.x =   (bytes & 0b0000_1111_0000_0000) >> 8
        self.y =   (bytes & 0b0000_0000_1111_0000) >> 4
        self.kk =  bytes & 0b0000_0000_1111_1111

    def __repr__(self) -> str:
        return \
        f"Opcode: {hex(self.opcode)}, "\
        + f"Instruction: {hex(self.bytes)}, "\
        + f"NNN: {hex(self.nnn)}, "\
        + f"N: {hex(self.n)}, "\
        + f"X: {hex(self.x)}, "\
        + f"Y: {hex(self.y)}, "\
        + f"KK: {hex(self.kk)}"

def parse(filename: str) -> List[ParsedInstruction]:
    ret = []

    # Read program file into memory
    with open(filename, 'rb') as f:
        bytes_in: bytes = f.read()

    # For each 2-pair of bytes
    # Assemble instruction from pair
    for idx in range(0, len(bytes_in)-1, 2):
        instruction = (bytes_in[idx] << 8) | bytes_in[idx+1]
        ret.append(ParsedInstruction(instruction))

    return ret


        