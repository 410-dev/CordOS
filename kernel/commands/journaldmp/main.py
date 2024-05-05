import kernel.io as IO
import kernel.journaling as Journaling
import kernel.registry as Registry

import traceback

def main(args: list):
    try:
        Journaling.JournalingContainer.dump()
        IO.println("Journal dumped.")
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error in dumping journal. e: {e}")
