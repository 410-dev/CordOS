import traceback

import kernel.registry as Registry


async def mainAsync(args: list, message) -> None:
    try:
        args.pop(0)
        if "--snippet" in args:
            args.remove("--snippet")
            await message.reply(f"```{" ".join(args)}```", mention_author=True)
            return
        await message.reply(" ".join(args), mention_author=True)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error while executing command: {e}", mention_author=True)
