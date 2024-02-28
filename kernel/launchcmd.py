import os

import kernel.registry as Registry

def getRunnableModule(args: list):
    commandsPaths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths")['data']
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
    
    return os.path.join(appropriateCommandPath, args[0], "main").replace("/", ".")

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

async def runRunnableModule(module: str, args: list, message):
    import importlib
    module = importlib.import_module(module)

    if Registry.read("SOFTWARE.CordOS.Kernel.ReloadOnCall") == "1":
        importlib.reload(module)

    commandClass = getattr(module, args[0].capitalize())
    command = commandClass(args, message)
    await command.exec()
