import os
import traceback

import kernel.registry as Registry
import kernel.journaling as Journaling

def getRunnableModule(args: list, targetExecutive: str = "main"):
    commandsPaths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")
    appropriateCommandPath: str = ""
    Journaling.record("INFO", f"Path: {commandsPaths}")

    for commandPath in commandsPaths:
        try:
            Journaling.record("INFO", f"Checking for command {args[0]} in {commandPath}")
            if not os.path.isfile(os.path.join(commandPath, args[0], f"{targetExecutive}.py")):
                continue
            appropriateCommandPath = commandPath
            Journaling.record("INFO", f"Command {args[0]} found in {commandPath}")
            break
        except:
            pass
    
    if appropriateCommandPath == "":
        return None
    
    val = os.path.join(appropriateCommandPath, args[0], targetExecutive).replace("/", ".").replace("\\", ".")
    Journaling.record("INFO", f"Command {args[0]} path generated as '{val}'")
    return val

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
            Journaling.record("ERROR", f"Error while running executive: {module} with args: {args}.")
            tracebackstr = traceback.format_exc()
            Journaling.record("ERROR", f"Traceback: {tracebackstr}")
            print(f"Error while running executive. e: {e}")
            return
