import kernel.ipc as IPC
import kernel.registry as Registry

async def mainAsync(args: list, message):

    if len(args) < 1:
        await message.reply("Usage: power off")
        return

    if args[0] == "off":
        IPC.set("power.off", True)
        IPC.set("power.off.state", "OFF")
        await message.reply(f"Shutdown signal published. System will shutdown after all services have stopped.")

    elif args[0] == "reboot":
        IPC.set("power.off", True)
        IPC.set("power.off.state", "REBOOT")
        await message.reply(f"Reboot signal published. System will reboot after all services have stopped.")

    elif args[0] == "halt":
        haltKey = f"KernelHaltSignal.{message.author.id}"
        haltValue = IPC.read(haltKey, default="0")
        if haltValue != "1" and (len(args) < 2 or args[1] != "--no-warning"):
            IPC.set(haltKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system force halt. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power halt-cancel`.")

        else:
            await message.reply(f"System will now be force terminated. Goodbye.")
            exit(0)

    elif args[0] == "reset":
        resetKey = f"KernelResetSignal.{message.author.id}"
        resetValue = IPC.read(resetKey)
        if resetValue != "1" and (len(args) < 2 or args[1] != "--no-warning"):
            IPC.set(resetKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system reset. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power reset-cancel`.")

        else:
            # with open("restart", 'w') as f:
            #     f.write("")
            await message.reply(f"System will now be reset.")
            exit(1)

    elif args[0] == "halt-cancel":
        haltKey = f"KernelHaltSignal.{message.author.id}"
        IPC.delete(haltKey)
        await message.reply("Force-halt cancelled.")

    elif args[0] == "reset-cancel":
        resetKey = f"KernelResetSignal.{message.author.id}"
        IPC.delete(resetKey)
        await message.reply("Reset cancelled.")

    else:
        await message.reply("Usage: power off")
        return



