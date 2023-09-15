from chip8.vm import VM
import cProfile, pstats, io, psutil


if __name__ == "__main__":
    # Pin process
    psutil.Process().cpu_affinity(
        [
            2,
        ]
    )

    # Init CHIP-8
    c8 = VM()

    # CHIP-8 program filepath
    filepath = """../ROM/trip8.bin"""

    # Load CHIP-8 program from disk
    c8.load(filepath)

    def hotLoop():
        # for _ in range(0, 1_000_000):
        c8.step(5_000_000)

    with cProfile.Profile() as profile:
        hotLoop()

        s = io.StringIO()
        stats = pstats.Stats(profile, stream=s).strip_dirs().sort_stats("cumtime")
        stats.print_stats(1.0)
        print(s.getvalue())
