
import traceback
from typing import List
from objects.embedmsg import EmbeddedMessage

import kernel.registry as Registry
import os

async def mainAsync(args: list, message) -> None:
    try:
        commandPaths: List[str] = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")

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

        if Registry.read("SOFTWARE.CordOS.Experimental.EmbeddedMessage", default="0") == "0":
            await message.reply(helpString, mention_author=True)
            return

        else:
            msg = EmbeddedMessage(message, title=args[1], description=helpString, footer="CordOS")
            await msg.sendAsReply()

    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error in settings. e: {e}", mention_author=True)
