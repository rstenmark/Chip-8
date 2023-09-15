import sys
from math import floor
from time import time_ns

from chip8 import vm
import pygame

import psutil

if __name__ == "__main__":
    # Pin process to core 2 thread 1 (on HT/SMT CPU)
    psutil.Process().cpu_affinity(
        [
            2,
        ]
    )
    # Init CHIP-8 object
    c8 = vm.VM()

    # CHIP-8 program filepath passed as argument
    filepath = sys.argv[1]

    # Load CHIP-8 program from disk
    c8.load(filepath)

    # Init pygame
    pygame.init()
    # Init pygame clock
    clock = pygame.time.Clock()
    # Configure pygame window
    screen = pygame.display.set_mode((384, 384))
    pygame.display.set_caption("CHIP-8")

    # Timing
    one_frame_ns = 166_666_666
    last_frame_ns = 0

    # State
    game_running = True
    crash_exception = None
    interpreter_cycle = 0

    # Main loop
    while game_running:
        try:
            # Close on any key press
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    game_running = False

            # Simulate CPU cycle
            c8.step(n_cycles=1)
            interpreter_cycle += 1

            # Interpreter exit signal
            if c8.cpu.ip == 0x10:
                game_running = False
                print(f"Program exit")
                break

            # Interpreter draw call
            if c8.is_drawing() is True:
                # Blank
                screen.fill("black")

                # Redraw
                for x in range(0, 64):
                    for y in range(0, 32):
                        if c8.cpu.display.get_pixel(x, y) > 0:
                            # Pixel doubling
                            screen.set_at((2 * x + 132, 2 * y + 148), (255,) * 3)
                            screen.set_at((2 * x + 132, 2 * y + 148 + 1), (255,) * 3)
                            screen.set_at((2 * x + 132 + 1, 2 * y + 148), (255,) * 3)
                            screen.set_at(
                                (2 * x + 132 + 1, 2 * y + 148 + 1), (255,) * 3
                            )
                        else:
                            pass

                # Flip
                pygame.display.flip()

                # Force tick
                # time_now = time_ns()
                # last_frame_ns = time_now
                # clock.tick()

            # Tick engine clock every 16.6 ms
            time_now = time_ns()
            if time_now - last_frame_ns > one_frame_ns:
                last_frame_ns = time_now
                clock.tick()
                # Update window title
                pygame.display.set_caption(
                    f"CHIP-8: cycle: {interpreter_cycle}, ROM: {filepath}"
                )

        except KeyboardInterrupt:
            game_running = False
            raise crash_exception
