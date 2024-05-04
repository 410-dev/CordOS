import traceback

import kernel.registry as Registry


async def mainAsync(args: list, message) -> None:
    try:
        args.pop(0)
        await message.reply(" ".join(args), mention_author=True)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error while executing command: {e}", mention_author=True)
