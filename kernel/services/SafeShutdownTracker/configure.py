import kernel.registry as Registry
import kernel.io as IO

async def mainAsync(args: list, message):
    if len(args) < 1:
        await message.reply("Usage: SafeShutdownTracker <enabled|disabled>")
        return

    if args[0] == "enabled":
        Registry.write("SOFTWARE.CordOS.Kernel.Services.kernel.services.SafeShutdownTracker.Enabled", "1")
        await message.reply("SafeShutdownTracker enabled.")
    elif args[0] == "disabled":
        Registry.write("SOFTWARE.CordOS.Kernel.Services.kernel.services.SafeShutdownTracker.Enabled", "0")
        await message.reply("SafeShutdownTracker disabled.")
    else:
        await message.reply("Invalid argument. Expected enabled or disabled.")


def main(args: list):
    if len(args) < 1:
        IO.println("Usage: SafeShutdownTracker <enabled|disabled>")
        return

    if args[0] == "enabled":
        Registry.write("SOFTWARE.CordOS.Kernel.Services.kernel.services.SafeShutdownTracker.Enabled", "1")
        IO.println("SafeShutdownTracker enabled.")
    elif args[0] == "disabled":
        Registry.write("SOFTWARE.CordOS.Kernel.Services.kernel.services.SafeShutdownTracker.Enabled", "0")
        IO.println("SafeShutdownTracker disabled.")
    else:
        IO.println("Invalid argument. Expected enabled or disabled.")


