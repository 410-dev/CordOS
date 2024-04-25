import os
import json

import kernel.registry as Registry

def getRunnableModule(args: list):
    commandsPaths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")
    appropriateCommandPath: str = ""
    for commandPath in commandsPaths:
        try:
            with open(os.path.join(commandPath, args[0], "main.py"), 'r') as f:
                appropriateCommandPath = commandPath
                break
        except:
            pass
    
    if appropriateCommandPath == "":
        return None
    
    return os.path.join(appropriateCommandPath, args[0], "main").replace("/", ".").replace("\\", ".")

def getCommand(args: list):
    return args[0]

def splitArguments(string: str) -> list:
    words = []
    in_quotes = False
    current_word = ""
    for char in string:
        if char == " " and not in_quotes:
            if current_word:
                words.append(current_word)
                current_word = ""
        elif char == '"':
            in_quotes = not in_quotes
        else:
            current_word += char
    if current_word:
        words.append(current_word)
    return words


def launchRunnable(module: str, args: list):
    import importlib
    module = importlib.import_module(module)

    if Registry.read("SOFTWARE.CordOS.Kernel.ReloadOnCall") == "1":
        importlib.reload(module)

    # Try with class structure
    try:
        commandClass = getattr(module, args[0].capitalize())
        command = commandClass(args)
        command.main()

    except Exception as ignored:
        # Try with function structure
        # Call the function where signature is async def main(lineArgs: list, message) -> None:
        try:
            module.main(args)
        except Exception as e:
            print(f"Error while running executive. e: {e}")
            return
