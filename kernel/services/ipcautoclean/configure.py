import kernel.registry as Registry

async def main(args: list, message):
    if len(args) < 1:
        await message.reply("Usage: ipcautoclean <enabled|disabled|expire=n>")
        return

    if args[0] == "enabled":
        Registry.write("SOFTWARE.CordOS.Kernel.IPC.EnableAutoCleaner", "1")
        await message.reply("IPC auto cleaner enabled.")
    elif args[0] == "disabled":
        Registry.write("SOFTWARE.CordOS.Kernel.IPC.EnableAutoCleaner", "0")
        await message.reply("IPC auto cleaner disabled.")
    elif args[0].startswith("expire="):
        try:
            time = int(args[0].split("=")[1])
            Registry.write("SOFTWARE.CordOS.Kernel.IPC.MemoryLiveTime", str(time))
            await message.reply(f"IPC memory expire time set to {time} seconds.")
        except ValueError:
            await message.reply("Invalid time. Expected integer.")

