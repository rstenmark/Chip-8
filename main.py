import chip8.cpu as cpu
from pathlib import Path
import sys
import pygame

if __name__ == "__main__":
    c8 = cpu.Chip8()
    filepath = sys.argv[1]
    c8.load(filepath)
    
    pygame.init()
    screen = pygame.display.set_mode((384, 384))
    pygame.display.set_caption("Chip-8")
    
    clock = pygame.time.Clock()
    game_running = True
    cpu_running = True
    crash_exception = None


    while game_running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    game_running = False

            if cpu_running:
                # Blank screen each frame
                screen.fill("black")
                
                # Simulate CPU cycle
                c8.step(n_cycles=1, debug=True, profile=False)
                #try:
                #    c8.step(n_cycles=1, debug=False, profile=False)
                #except Exception as e:
                #    cpu_running = False
                #    screen.fill("darkred")
                #    print(f'panic!')
                #    e = crash_exception

                # Redraw
                for x in range(0, 64):
                    for y in range(0, 32):
                        if c8.cpu.display.get_pixel(x, y) > 0:
                            screen.set_at((2*x+132, 2*y+148), "white")
                        else:
                            pass

                # Flip display
                pygame.display.flip()

                # Interpreter exit
                if c8.cpu.ip == 0x10:
                    cpu_running = False
                    print(f'Program exit')

            pygame.display.set_caption(f"Chip-8: FPS: {round(clock.get_fps(), 2)}, ROM: {filepath}")
            clock.tick(240*4)

        except(KeyboardInterrupt):
            running = False
            raise crash_exception