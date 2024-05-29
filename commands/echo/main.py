import kernel.registry as Registry
import kernel.io as IO

import traceback

def main(args: list) -> None:
    try:
        args.pop(0)
        IO.println(" ".join(args))
    except Exception as e:
        if Registry.read("SOFTWARE.NanoPyOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error while executing command: {e}")

