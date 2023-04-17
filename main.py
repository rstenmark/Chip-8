#!/usr/bin/python3
import multiprocessing as mp
from bench import f
from os import cpu_count

if __name__ == "__main__":
    cpus = 6
    p = mp.Pool(processes=cpus)
    p.map(f, [i for i in range(0, cpus)])