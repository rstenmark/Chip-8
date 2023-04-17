import sys
import chip8.cpu as cpu
from chip8.parser import ParsedInstruction
from time import time, time_ns
from pathlib import PosixPath
from statistics import median
from math import ceil

def f(pid: int):
    c8 = cpu.Chip8()
    c8.load(sys.argv[1])
    n_cycles = 8
    samples = 100
    with open(PosixPath(f"/home/rs/pychip8/scratch/pid{pid}.out"), 'w') as f:
        l = list()
        while n_cycles < 65536*2:
            for _ in range(0, samples):
                start_ns = time_ns()
                c8.step(n_cycles=n_cycles, debug=False)
                l.append(time_ns() - start_ns)
            f.write(f"{n_cycles},{ceil(median(l))}\n")
            l.clear()
            n_cycles *= 2
        