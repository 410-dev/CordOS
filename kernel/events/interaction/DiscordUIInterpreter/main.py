import kernel.launchcmd as Launcher
import kernel.registry as Registry

import kernel.services.DiscordUIService.asynclauncher as AsyncLauncher

import traceback

async def mainAsync(message):
    try:
        prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
        msgContent: str = message.content[len(prefix):]
        args: list = Launcher.splitArguments(msgContent)
        cmd: str = Launcher.getCommand(args)
        runnablePath: str = Launcher.getRunnableModule(args)
        runnablePath = runnablePath[:-(len(".main"))] + ".discordui"
    except Exception as e:
        await message.reply(f"Failed looking up for command. This should not occur. {e}", mention_author=True)
        return

    if runnablePath == "" or runnablePath is None:
        await message.reply(f"Command {cmd} not found.", mention_author=True)
        return

    try:
        await AsyncLauncher.runRunnableModule(runnablePath, args, message)
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error executing command '{cmd}': {e}", mention_author=True)
