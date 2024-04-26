from typing import List
import traceback
import os

import kernel.registry as Registry
import kernel.io as IO

def main(args: list) -> None:
    try:
        commandPaths: List[str] = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")
        cmdList: str = "Available Commands:\n"
        for commandPath in commandPaths:
            try:
                dirList = os.listdir(commandPath)
                for directory in dirList:
                    if os.path.isdir(os.path.join(commandPath, directory)) and os.path.exists(os.path.join(commandPath, directory, "main.py")):
                        with open(os.path.join(commandPath, directory, "main.py"), 'r') as f:
                            content = f.read()
                            if "def main(" in content:
                                cmdList += f"{directory}\n"
                            else:
                                cmdList += f"{directory} (incompatible)\n"
            except:
                pass

        IO.println(cmdList)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error in settings. e: {e}")

