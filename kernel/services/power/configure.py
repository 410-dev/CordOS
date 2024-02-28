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

    else:
        await message.reply("Usage: power off")
        return
    
    