
import traceback
from typing import List

import kernel.registry as Registry
import kernel.io as IO

import os

def main(args: list, message) -> None:
    try:
        commandPaths: List[str] = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")

        if len(args) < 2:
            # Print current manual
            with open("kernel/commands/help/manual.txt", 'r') as f:
                IO.println(f.read())
                return

        # Find executable bundle
        helpString: str = ""
        for commandPath in commandPaths:
            try:
                with open(os.path.join(commandPath, args[1], "manual.txt"), 'r') as f:
                    helpString = f.read()
                    break
            except:
                pass

        # If not found, return command not found.
        if helpString == "":
            return Registry.read("SOFTWARE.CordOS.Kernel.Proc.CommandNotFound")

        IO.println(helpString)

    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error in settings. e: {e}")

