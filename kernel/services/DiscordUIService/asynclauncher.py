import kernel.registry as Registry
import kernel.journaling as Journaling

async def runRunnableModule(module: str, args: list, message):
    import importlib
    module = importlib.import_module(module)

    Journaling.record("INFO", f"Running module '{module}' with args '{args}'.")
    if Registry.read("SOFTWARE.CordOS.Kernel.ReloadOnCall") == "1":
        importlib.reload(module)

    # Try with class structure
    try:
        Journaling.record("INFO", f"Class Struct: Running module '{module}' with args '{args}'.")
        commandClass = getattr(module, args[0].capitalize())
        command = commandClass(args, message)
        await command.mainAsync()
        Journaling.record("INFO", f"Class Struct: Module '{module}' executed.")

    except Exception as ignored:
        # Try with function structure
        # Call the function where signature is async def main(lineArgs: list, message) -> None:
        try:
            Journaling.record("INFO", f"Function Struct: Running module '{module}' with args '{args}'.")
            await module.mainAsync(args, message)
            Journaling.record("INFO", f"Function Struct: Module '{module}' executed.")
        except Exception as e:
            Journaling.record("ERROR", f"Error while running module '{module}': {e}")
            await message.reply(f"Error while running executive. e: {e}", mention_author=True)
            return
