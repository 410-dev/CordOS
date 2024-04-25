
import traceback
from typing import List
import kernel.registry as Registry

import json
import os

async def mainAsync(args: list, message) -> None:
    try:
        commandPaths: List[str] = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")

        # Find executable bundle
        cmdList: str = "Available Commands:\n"
        for commandPath in commandPaths:
            try:
                dirList = os.listdir(commandPath)
                # For each directory in the command path, check if it is a directory and contains main.py.
                for directory in dirList:
                    if os.path.isdir(os.path.join(commandPath, directory)) and os.path.exists(os.path.join(commandPath, directory, "main.py")):
                        with open(os.path.join(commandPath, directory, "main.py"), 'r') as f:
                            content = f.read()
                            if "async def mainAsync(" in content:
                                cmdList += f"{directory}\n"
                            else:
                                cmdList += f"{directory} (incompatible)\n"
            except:
                pass

        # If not found, return command not found.

        await message.reply(cmdList, mention_author=True)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error in settings. e: {e}", mention_author=True)


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

