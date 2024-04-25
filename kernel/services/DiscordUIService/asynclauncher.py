import kernel.registry as Registry


async def runRunnableModule(module: str, args: list, message):
    import importlib
    module = importlib.import_module(module)

    if Registry.read("SOFTWARE.CordOS.Kernel.ReloadOnCall") == "1":
        importlib.reload(module)

    # Try with class structure
    try:
        commandClass = getattr(module, args[0].capitalize())
        command = commandClass(args, message)
        await command.mainAsync()

    except Exception as ignored:
        # Try with function structure
        # Call the function where signature is async def mainAsync(lineArgs: list, message) -> None:
        try:
            await module.mainAsync(args, message)
        except Exception as e:
            await message.reply(f"Error while running executive. e: {e}", mention_author=True)
            return
