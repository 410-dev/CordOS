import kernel.registry as Registry
import kernel.journaling as Journaling

import traceback


async def mainAsync(args: list, message) -> None:
    try:
        Journaling.JournalingContainer.dump()
        await message.reply("Journal dumped.", mention_author=True)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error in dumping journal. e: {e}", mention_author=True)
