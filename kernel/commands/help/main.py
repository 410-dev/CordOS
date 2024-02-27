
import traceback
from typing import List
import kernel.registry as Registry

import json
import os



class Help:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message

    async def exec(self):
        try: 
            commandPaths: List[str] = json.loads(Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths"))['data']
            
            if len(self.args) == 0:
                # Print current manual
                with open("kernel/commands/help/manual.txt", 'r') as f:
                    await self.message.reply(f.read(), mention_author=True)
                    return
            
            # Find executable bundle
            helpString: str = ""
            for commandPath in commandPaths:
                try:
                    with open(os.path.join(commandPath, self.args[0], "manual.txt"), 'r') as f:
                        helpString = f.read()
                        break
                except:
                    pass
            
            # If not found, return command not found.
            if helpString == "":
                return Registry.read("SOFTWARE.CordOS.Kernel.Proc.CommandNotFound")
            
            await self.message.reply(helpString, mention_author=True)
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error in settings. e: {e}", mention_author=True)