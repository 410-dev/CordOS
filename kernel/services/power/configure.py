import kernel.ipc as IPC
import kernel.registry as Registry

async def main(args: list, message):

    if len(args) < 1:
        await message.reply("Usage: power off")
        return

    stateName = Registry.read("SOFTWARE.CordOS.Kernel.Services.CoreServices.IPC.LabelKernelState")

    if args[0] == "off":
        IPC.set(stateName, Registry.read("SOFTWARE.CordOS.Kernel.Signals.Shutdown"))
        await message.reply(f"Shutdown signal published. System will shutdown after all services have stopped.")

    elif args[0] == "halt":
        # Read the registry - SOFTWARE.CordOS.Kernel.Signals.Halt.<userid>
        # If it is not set, set it to 1 and send warning message.
        # If it is set to 1, delete the registry and halt.

        haltKey = f"SOFTWARE.CordOS.Kernel.Signals.Halt.{message.author.id}"
        haltValue = Registry.read(haltKey)
        if haltValue != "1":
            Registry.write(haltKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system force halt. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power halt-cancel`.")

        else:
            Registry.delete(haltKey)
            await message.reply(f"System will now be force terminated. Goodbye.")
            exit(0)

    elif args[0] == "reset":
        resetKey = f"SOFTWARE.CordOS.Kernel.Signals.Reset.{message.author.id}"
        resetValue = Registry.read(resetKey)
        if resetValue != "1":
            Registry.write(resetKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system reset. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power reset-cancel`.")

        else:
            Registry.delete(resetKey)
            with open("restart", 'w') as f:
                f.write("")
            await message.reply(f"System will now be reset.")
            exit(1)

    elif args[0] == "halt-cancel":
        haltKey = f"SOFTWARE.CordOS.Kernel.Signals.Halt.{message.author.id}"
        Registry.delete(haltKey)
        await message.reply("Force-halt cancelled.")

    elif args[0] == "reset-cancel":
        resetKey = f"SOFTWARE.CordOS.Kernel.Signals.Reset.{message.author.id}"
        Registry.delete(resetKey)
        await message.reply("Reset cancelled.")

    else:
        await message.reply("Usage: power off")
        return



