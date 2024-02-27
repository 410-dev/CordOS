
import traceback
from typing import List
import kernel.registry as Registry

import json
import os



class Fasthelp:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message

    async def exec(self):
        try: 
            commandPaths: List[str] = json.loads(Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths"))['data']
            
            
            # Find executable bundle
            cmdList: str = "Available Commands:\n"
            for commandPath in commandPaths:
                try:
                    dirList = os.listdir(commandPath)
                    # For each directory in the command path, check if it is a directory and contains main.py.
                    for directory in dirList:
                        if os.path.isdir(os.path.join(commandPath, directory)) and os.path.exists(os.path.join(commandPath, directory, "main.py")):
                            cmdList += f"{directory}\n"
                except:
                    pass
            
            # If not found, return command not found.

            await self.message.reply(cmdList, mention_author=True)
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error in settings. e: {e}", mention_author=True)