from typing import Dict, Callable
from chip8.parser import ParsedInstruction
from random import randint
import chip8.parser as parser
import chip8.registers as registers
import chip8.stack as stack
import chip8.memory as memory
import chip8.display as display


class CPU(object):
    '''Contains machine state, handles control flow, and implements opcode behavior'''
    def __init__(self):
        # 4096*1-byte (0, 2^8) addressable memory
        self.mem = memory.Memory(0xfff)
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

    def reset(self) -> None:
        '''Reset mutable components of the CPU to startup values'''
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

    def set_ip(self, addr: int) -> None:
        '''Overwrites the instruction pointer with a 12-bit address'''
        self.ip = addr

    def step_ip(self, n_cycles: int = 1) -> None:
        '''Step the CPU n cycles.
        All values in memory are 2-byte aligned, so
        IP is incremented by 2 each cycle.'''
        for _ in range(0, n_cycles):
            # alias ParsedInstruction object at IP
            inst: ParsedInstruction = self.mem[self.ip]
            old_ip = self.ip
            # execute opcode
            self._method_lookup_table[inst.opcode](self, inst)
            # if IP did not change, increment it
            if old_ip == self.ip:
                self.ip += 2

        # Decrement timers
        if(self.st > 0): self.st -= 1
        if(self.dt > 0): self.dt -= 1

    def _push(self, v: int) -> None:
        '''Pushes a value onto the stack and increments SP.'''
        self.stack.push(v)
        self.sp += 1

    def _pop(self) -> int:
        '''Pops a value off the stack and decrements SP.'''
        self.sp -= 1
        return self.stack.pop()

    def _0nnn(self, inst: ParsedInstruction) -> int:
        '''Jump to a machine code routine at NNN.
        No effects.
        1 cycle.'''
        return 1

    def _00E0(self, inst: ParsedInstruction) -> int:
        '''Clear the display.
        Overwrites all values in self.display with 0.
        1 cycle.'''
        self.display.reset()
        return 1

    def _00EE(self, inst: ParsedInstruction) -> int:
        '''Return from a subroutine (function). 
        Overwrites IP with 12-bit address popped off stack.
        1 cycle.'''
        self.ip = self.stack.pop()
        return 1

    def _1nnn(self, inst: ParsedInstruction) -> int:
        '''Performs an immediate jump.
        Overwrites IP with a 12-bit immediate address
        1 cycle.'''
        self.ip = inst.nnn
        return 1

    def _2nnn(self, inst: ParsedInstruction) -> int:
        '''Call subroutine (function).
        Pushes return address onto the stack,
        then jumps to nnn.
        1 cycle.'''
        self._push(self.ip)
        self.set_ip(inst.nnn)
        return 1

    def _3xkk(self, inst: ParsedInstruction) -> int:
        '''Skip next instruction if Vx == kk
        1 cycle.'''
        if self.reg.get(inst.x) == inst.kk:
            # Relative jump
            self.ip += 4
        return 1

    def _4xkk(self, inst: ParsedInstruction) -> int: ...
    def _5xy0(self, inst: ParsedInstruction) -> int: ...
    def _6xkk(self, inst: ParsedInstruction) -> int:
        '''Set Vx = kk
        1 cycle.'''
        self.reg.set(inst.x, inst.kk)
    def _7xkk(self, inst: ParsedInstruction) -> int:
        '''Set Vx = Vx + kk
        1 cycle.'''
        self.reg.set(inst.x, inst.kk)
        return 1

    def _8xy0(self, inst: ParsedInstruction) -> int:
        '''Set Vx = Vy
        1 cycle.'''
        self.reg.set(inst.x, self.reg.get(inst.y))
        return 1

    def _8xy1(self, inst: ParsedInstruction) -> int: ...
    def _8xy2(self, inst: ParsedInstruction) -> int: ...
    def _8xy3(self, inst: ParsedInstruction) -> int: ...
    def _8xy4(self, inst: ParsedInstruction) -> int: ...
    def _8xy5(self, inst: ParsedInstruction) -> int: ...
    def _8xy6(self, inst: ParsedInstruction) -> int: ...
    def _8xy7(self, inst: ParsedInstruction) -> int: ...
    def _8xyE(self, inst: ParsedInstruction) -> int: ...
    def _9xy0(self, inst: ParsedInstruction) -> int: ...
    def _Annn(self, inst: ParsedInstruction) -> int:
        '''Overwrites the value in register I with nnn.
        1 cycle.'''
        self.i = inst.nnn
        return 1
    def _Bnnn(self, inst: ParsedInstruction) -> int: ...
    def _Cxkk(self, inst: ParsedInstruction) -> int:
        '''Set Vx = random byte AND kk
        1 cycle.'''
        self.reg.set(inst.x, randint(0, 255) & inst.kk)

    def _Dxyn(self, inst: ParsedInstruction) -> int:
        '''Draw n-byte sprite starting at I at (Vx, Vy), setting VF on collision
        1 cycle.'''
        # NOTE:
        # Sprites may be up to 15 bytes, or 8x15 pixels
        # Sprites are always 8 pixels wide

        # Read n bytes starting at I at 2-byte alignments
        b: list[int] = list()
        for ii in range(0, inst.n, 2):
            b.append(self.mem[self.i + ii].bytes & 0b1111_1111_0000_0000 >> 8)
            b.append(self.mem[self.i + ii].bytes & 0b0000_0000_1111_1111)

        # xx = x + (0, 7)
        # yy = y + (0, 14)
        xx, yy = 0, 0
        x, y = self.reg.get(inst.x), self.reg.get(inst.y)
        for byte in b:
            for xx in range(8):
                # Extract bit:
                # Shift right up to 7 times and mask off MSBs
                bit = (byte >> 7 - xx) & 0b0000_0001

                if bit == 0b1:
                    if self.display.get_pixel(x + xx,  y + yy) == 1:
                        # Set VF
                        self.reg.set(0xF, 1)
                        # 1 xor 1 = 0
                        self.display.set_pixel(x + xx, y + yy, 0)
                    else:
                        # 0 xor 1 = 1
                        self.display.set_pixel(x + xx, y + yy, 1)

            yy += 1
                



    def _Ex9E(self, inst: ParsedInstruction) -> int: ...
    def _ExA1(self, inst: ParsedInstruction) -> int: ...
    def _Fx07(self, inst: ParsedInstruction) -> int:
        '''Set Vx = DT
        The value of the delay timer is stored in Vx
        1 cycle.'''
        self.reg.set(inst.x, self.dt)

    def _Fx0A(self, inst: ParsedInstruction) -> int: ...
    def _Fx15(self, inst: ParsedInstruction) -> int:
        '''Set DT = Vx
        The value in Vx is stored in the delay timer
        1 cycle.'''
        self.dt = self.reg.get(inst.x)

    def _Fx18(self, inst: ParsedInstruction) -> int: ...
    def _Fx1E(self, inst: ParsedInstruction) -> int: ...
    def _Fx29(self, inst: ParsedInstruction) -> int: ...
    def _Fx33(self, inst: ParsedInstruction) -> int: ...
    def _Fx55(self, inst: ParsedInstruction) -> int: ...
    def _Fx65(self, inst: ParsedInstruction) -> int: ...

    # Opcode to instance method pointer lookup table
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
        0xF065: _Fx65
    }

class Chip8(object):
    def __init__(self):
        self.cpu = CPU()

    def reset(self) -> None:
        self.cpu.reset()

    def step(self, n_cycles: int = 1, debug=False) -> None:
        if debug == True:
            lut = self.cpu._method_lookup_table
            ip = self.cpu.ip
            mem = self.cpu.mem
            reg = self.cpu.reg.reg
            stack = self.cpu.stack
            dt = self.cpu.dt
            st = self.cpu.st
            print(f"{'-'*32}\nIP: {hex(ip)}, DT: {dt}, ST: {st}\n{reg}\n{stack}\n{mem[ip]}\n{lut[mem[ip].opcode].__doc__}")
        self.cpu.step_ip(n_cycles=n_cycles)
        if debug == True:
            ip = self.cpu.ip
            reg = self.cpu.reg.reg
            stack = self.cpu.stack
            dt = self.cpu.dt
            st = self.cpu.st
            print(f"IP: {hex(ip)}, DT: {dt}, ST: {st}\n{reg}\n{stack}\n{mem[ip]}\n")

    def load(self, filename: str):
        '''Opens, parses, and loads a Chip8 binary program into memory at 0x200'''
        for idx, parsed_instruction in enumerate(parser.parse(filename)):
            # Store ParsedInstruction objects at 2-byte alignments
            assert type(parsed_instruction) == type(parser.ParsedInstruction(0))
            self.cpu.mem[0x200+(2*idx)] = parsed_instruction