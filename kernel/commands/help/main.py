
import traceback
from typing import List
from objects.embedmsg import EmbeddedMessage

import kernel.registry as Registry

import json
import os

async def main(args: list, message) -> None:
    try:
        commandPaths: List[str] = json.loads(Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths"))['data']

        if len(args) < 2:
            # Print current manual
            with open("kernel/commands/help/manual.txt", 'r') as f:
                await message.reply(f.read(), mention_author=True)
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

        msg = EmbeddedMessage(message, title=args[1], description=helpString, footer="CordOS")
        await msg.sendAsReply()

        # await message.reply(helpString, mention_author=True)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error in settings. e: {e}", mention_author=True)

