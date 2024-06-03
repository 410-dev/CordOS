import kernel.clock as Clock
import kernel.io as IO


def main(args: list):
    IO.println(f"Uptime: {Clock.getUptime()}")
