import chip8.display as display
import chip8.memory as memory
import chip8.parser as parser
import chip8.registers as registers
import chip8.stack as stack
from chip8.parser import ParsedInstruction
from random import randint
from time import perf_counter_ns as timer
from typing import Dict, Callable


class CPU(object):
    """Contains machine state, handles control flow, and implements opcode behavior"""

    def __init__(self):
        # 4096*1-byte (0, 2^8) addressable memory
        self.mem = memory.Memory(0xFFF)
        # 16*1-byte (0, 2^8) registers
        self.reg = registers.Registers()
        # 64x32 1-bit (0, 1) display memory
        self.display = display.Display()
        # 16x2-byte (0, 2^16) stack
        self.stack = stack.Stack()
        # Instruction pointer (0, 2^16-1)
        self.ip: int = 0x200
        # Stack pointer (0, 2^8-1)
        self.sp: int = 0x0
        # Address pointer (0, 2^16-1)
        self.i: int = 0x0
        # Delay timer
        self.dt = 0
        # Sound timer
        self.st = 0
        # Drawing flag
        self.df: bool = False

    def reset(self) -> None:
        """Reset mutable components of the CPU to startup values"""
        # 16*1-byte (0, 2^8) registers
        self.reg = registers.Registers()
        # 64x32 1-bit (0, 1) display memory
        self.display = display.Display()
        # 16x2-byte (0, 2^16) stack
        self.stack = stack.Stack()
        # Instruction pointer (0, 2^16-1)
        self.ip: int = 0x200
        # Stack pointer (0, 2^8-1)
        self.sp: int = 0x0
        # Address pointer (0, 2^16-1)
        self.i: int = 0x0
        # Delay timer
        self.dt = 0
        # Sound timer
        self.st = 0
        # Drawing flag
        self.df: bool = False

    def set_ip(self, addr: int) -> None:
        """Overwrites the instruction pointer with a 12-bit address"""
        self.ip = addr

    def step(self, n_cycles: int = 1) -> None:
        """Step the CPU n cycles.
        All values in memory are 2-byte aligned, so
        IP is incremented by 2 each cycle."""
        for _ in range(0, n_cycles):
            # alias ParsedInstruction object at IP
            inst: ParsedInstruction = self.mem[self.ip]
            # update old_ip
            old_ip = self.ip
            # reset draw flag
            self.df = False
            # execute opcode
            self._method_lookup_table[inst.opcode](self, inst)
            # Decrement timers
            if self.st > 0:
                self.st -= 1
            if self.dt > 0:
                self.dt -= 1
            # if IP did not change, increment it
            if old_ip == self.ip:
                self.ip += 2

    def _push(self, v: int) -> None:
        """Pushes a value onto the stack and increments SP."""
        self.stack.push(v)
        self.sp += 1

    def _pop(self) -> int:
        """Pops a value off the stack and decrements SP."""
        self.sp -= 1
        return self.stack.pop()

    def _0nnn(self, inst: ParsedInstruction) -> int:
        """Jump to a machine code routine at NNN.
        No effects.
        1 cycle."""
        return 1

    def _00E0(self, inst: ParsedInstruction) -> int:
        """Clear the display.
        Overwrites all values in self.display with 0.
        1 cycle."""
        self.display.reset()
        return 1

    def _00EE(self, inst: ParsedInstruction) -> int:
        """Return from a subroutine (function).
        Overwrites IP with 12-bit address popped off stack plus a 2 byte offset.
        1 cycle."""
        self.ip = self.stack.pop()
        return 1

    def _1nnn(self, inst: ParsedInstruction) -> int:
        """Performs an immediate jump.
        Overwrites IP with a 12-bit immediate address
        1 cycle."""
        if inst.nnn % 2 != 0:
            # "nudge" IP if not 2-byte unaligned
            self.set_ip(inst.nnn + 0x1)
        else:
            self.set_ip(inst.nnn)

        return 1

    def _2nnn(self, inst: ParsedInstruction) -> int:
        """Call subroutine (function).
        Pushes return address (plus 2) onto the stack,
        then jumps to nnn.
        1 cycle."""
        self._push(self.ip + 0x2)
        self.set_ip(inst.nnn)
        return 1

    def _3xkk(self, inst: ParsedInstruction) -> int:
        """Skip next instruction if Vx == kk
        1 cycle."""
        if self.reg.get(inst.x) == inst.kk:
            # Relative jump
            self.ip += 4
        return 1

    def _4xkk(self, inst: ParsedInstruction) -> int:
        """Skip next instruction if Vx != kk
        1 cycle."""
        if self.reg.get(inst.x) != inst.kk:
            # Relative jump
            self.ip += 4
        return 1

    def _5xy0(self, inst: ParsedInstruction) -> int:
        """Skip next instruction if Vx == Vy
        1 cycle."""
        if self.reg.get(inst.x) == self.reg.get(inst.y):
            # Relative jump
            self.ip += 4
        return 1

    def _6xkk(self, inst: ParsedInstruction) -> int:
        """Set Vx = kk
        1 cycle."""
        self.reg.set(inst.x, inst.kk)
        return 1

    def _7xkk(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx + kk
        1 cycle."""
        self.reg.set(inst.x, self.reg.get(inst.x) + inst.kk)
        return 1

    def _8xy0(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vy
        1 cycle."""
        self.reg.set(inst.x, self.reg.get(inst.y))
        return 1

    def _8xy1(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx OR Vy
        Quirks:
        COSMAC: Resets VF
        1 cycle."""
        self.reg.set(inst.x, self.reg.get(inst.x) | self.reg.get(inst.y))
        return 1

    def _8xy2(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx OR Vy
        Quirks:
        COSMAC: Resets VF
        1 cycle."""
        self.reg.set(inst.x, self.reg.get(inst.x) & self.reg.get(inst.y))
        return 1

    def _8xy3(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx XOR Vy
        Quirks:
        COSMAC: Resets VF
        1 cycle."""
        self.reg.set(inst.x, self.reg.get(inst.x) ^ self.reg.get(inst.y))
        return 1

    def _8xy4(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx + Vy, set VF = carry
        1 cycle."""
        result = self.reg.get(inst.x) + self.reg.get(inst.y)
        self.reg.set(inst.x, result & 0x00FF)
        if result % 255 > 0:
            self.reg.set(0xF, 1)
        else:
            self.reg.set(0xF, 0)
        return 1

    def _8xy5(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vx - Vy
        If Vx > Vy, set VF = 1 else VF = 0
        1 cycle."""
        vx, vy = self.reg.get(inst.x), self.reg.get(inst.y)
        self.reg.set(inst.x, vx - vy)
        if vx > vy:
            self.reg.set(0xF, 1)
        else:
            self.reg.set(0xF, 0)
        return 1

    def _8xy6(self, inst: ParsedInstruction) -> int:
        """If Vx LSB == 1 set VF = 1 else VF = 0. Then Vx = Vx >> 1 (divide by 2)."""
        self.reg.set(inst.x, self.reg.get(inst.x) >> 1)
        if self.reg.get(inst.x) & 0b0000_0001:
            self.reg.set(0xF, 1)
        else:
            self.reg.set(0xF, 0)
        return 1

    def _8xy7(self, inst: ParsedInstruction) -> int:
        """Set Vx = Vy - Vx
        If Vy > Vx, set VF = 1 else VF = 0
        1 cycle."""
        vx, vy = self.reg.get(inst.x), self.reg.get(inst.y)
        self.reg.set(inst.x, vy - vx)
        if vy > vx:
            self.reg.set(0xF, 1)
        else:
            self.reg.set(0xF, 0)
        return 1

    def _8xyE(self, inst: ParsedInstruction) -> int:
        """If Vx MSB == 1 set VF = 1 else VF = 0. Then Vx = Vx << 1 (multiply by 2)."""
        self.reg.set(inst.x, self.reg.get(inst.x) << 1)
        if self.reg.get(inst.x) & 0b1000_0000:
            self.reg.set(0xF, 1)
        else:
            self.reg.set(0xF, 0)
        return 1

    def _9xy0(self, inst: ParsedInstruction) -> int:
        ...

    def _Annn(self, inst: ParsedInstruction) -> int:
        """Overwrites the value in register I with nnn.
        1 cycle."""
        self.i = inst.nnn
        return 1

    def _Bnnn(self, inst: ParsedInstruction) -> int:
        """Jump to location nnn + V0"""
        self.set_ip(self.reg.get(0x0) + inst.nnn)
        return 1

    def _Cxkk(self, inst: ParsedInstruction) -> int:
        """Set Vx = random byte AND kk
        1 cycle."""
        self.reg.set(inst.x, randint(0, 255) & inst.kk)
        return 1

    def _Dxyn(self, inst: ParsedInstruction) -> int:
        """Draw n-byte sprite starting at I at (Vx, Vy), setting VF on collision"""
        # NOTE:
        # Sprites may be up to 15 bytes, or 8x15 pixels
        # Sprites are always 8 pixels wide

        # Set draw flag
        self.df = True

        # Unset VF
        self.reg.set(0xF, 0)

        # xx = x + (0, 7)
        # yy = y + (0, 14)
        x = self.reg.get(inst.x) & self.display.SCR_W - 1
        y = self.reg.get(inst.y) & self.display.SCR_H - 1

        # Read n (up to 15) bytes starting at I unaligned
        bitmap: list[int] = self.mem.read_byte_range(self.i, self.i + inst.n)

        y_offset = 0
        for byte in bitmap:
            for x_offset in range(8):
                # Extract bitmask:
                # Shift right up to 7 times and mask off MSB
                if (byte >> 7 - x_offset) & 0b0000_0001 == 0b1:
                    xx, yy = x + x_offset, y + y_offset
                    if self.display.get_pixel(xx, yy) == 1:
                        # This pixel was on
                        # Set VF
                        self.reg.set(0xF, 1)
                        # 1 xor 1 = 0
                        # Turn it off
                        self.display.set_pixel(xx, yy, 0)
                    else:
                        # This pixel was off
                        # 0 xor 1 = 1
                        # Turn it on
                        self.display.set_pixel(xx, yy, 1)

            y_offset += 1
        return 1

    def _Ex9E(self, inst: ParsedInstruction) -> int:
        raise NotImplementedError

    def _ExA1(self, inst: ParsedInstruction) -> int:
        raise NotImplementedError

    def _Fx07(self, inst: ParsedInstruction) -> int:
        """Set Vx = DT
        The value of the delay timer is stored in Vx
        1 cycle."""
        self.reg.set(inst.x, self.dt)
        return 1

    def _Fx0A(self, inst: ParsedInstruction) -> int:
        raise NotImplementedError

    def _Fx15(self, inst: ParsedInstruction) -> int:
        """Set DT = Vx
        The value in Vx is stored in the delay timer
        1 cycle."""
        self.dt = self.reg.get(inst.x)
        return 1

    def _Fx18(self, inst: ParsedInstruction) -> int:
        """Set ST = Vx
        The value in Vx is stored in the sound timer
        1 cycle."""
        self.st = self.reg.get(inst.x)
        return 1

    def _Fx1E(self, inst: ParsedInstruction) -> int:
        """ADD I, Vx
        Set I = I + Vx
        1 cycle."""
        self.i = self.i + self.reg.get(inst.x)
        return 1

    def _Fx29(self, inst: ParsedInstruction) -> int:
        raise NotImplementedError

    def _Fx33(self, inst: ParsedInstruction) -> int:
        """LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, I+2
        1 cycle."""
        raise NotImplementedError

    def _Fx55(self, inst: ParsedInstruction) -> int:
        """LD [I], Vx
        Stores registers V0-Vx inclusive in memory starting at I
        1 cycle."""
        for off in range(0, inst.x + 1):
            self.mem[self.i + off] = self.reg.get(off)
        return 1

    def _Fx65(self, inst: ParsedInstruction) -> None:
        """LD Vx, [I]
        Read registers V0-Vx inclusive from memory starting at I"""
        # Plus one because range is exclusive
        for k in range(0, inst.x + 1):
            self.reg.set(k, self.mem.read_any_potentially_unaligned(self.i + k))

    # Opcode to class instance method lookup table
    _method_lookup_table: Dict[int, Callable] = {
        0x0000: _0nnn,
        0x00E0: _00E0,
        0x00EE: _00EE,
        0x1000: _1nnn,
        0x2000: _2nnn,
        0x3000: _3xkk,
        0x4000: _4xkk,
        0x5000: _5xy0,
        0x6000: _6xkk,
        0x7000: _7xkk,
        0x8000: _8xy0,
        0x8001: _8xy1,
        0x8002: _8xy2,
        0x8003: _8xy3,
        0x8004: _8xy4,
        0x8005: _8xy5,
        0x8006: _8xy6,
        0x8007: _8xy7,
        0x800E: _8xyE,
        0x9000: _9xy0,
        0xA000: _Annn,
        0xB000: _Bnnn,
        0xC000: _Cxkk,
        0xD000: _Dxyn,
        0xE09E: _Ex9E,
        0xE0A1: _ExA1,
        0xF007: _Fx07,
        0xF00A: _Fx0A,
        0xF015: _Fx15,
        0xF018: _Fx18,
        0xF01E: _Fx1E,
        0xF029: _Fx29,
        0xF033: _Fx33,
        0xF055: _Fx55,
        0xF065: _Fx65,
    }
