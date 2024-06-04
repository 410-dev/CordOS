import kernel.launchcmd as Launcher
import kernel.registry as Registry
import kernel.journaling as Journaling

import kernel.services.DiscordUIService.asynclauncher as AsyncLauncher
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation

import traceback

async def mainAsync(message):
    try:
        prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
        msgContent: str = message.content[len(prefix):]
        args: list = Launcher.splitArguments(msgContent)
        cmd: str = Launcher.getCommand(args)
        # paths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.DiscordPaths", default="kernel/services/DiscordUIService/subsystem/commands", writeDefault=True).replace(", ", ",").split(",")
        Journaling.record("INFO", f"Command '{cmd}' executed by {message.author.name}#{message.author.discriminator}.")
        if not Isolation.getIsolationAvailable(message):
            Journaling.record("INFO", f"Isolation not available for guild {message.guild.id}.")
            runnablePath: str = Launcher.getRunnableModule(args, "discordui")
        else:
            paths = [
                Isolation.getContainerPath(message, "commands"),
            ]
            Journaling.record("INFO", f"Command will be searched under path: {paths}")
            runnablePath: str = Launcher.getRunnableModule(args, "discordui", pathList=paths)
        Journaling.record("INFO", f"Command '{cmd}' found at '{runnablePath}'.")
    except Exception as e:
        Journaling.record("ERROR", f"Failed looking up for command. The issue is highly likely from Launcher.getRunnableModule. e: {e}")
        await message.reply(f"Failed looking up for command. This should not occur. {e}", mention_author=True)
        return

    if runnablePath == "" or runnablePath is None:
        Journaling.record("WARNING", f"Command '{cmd}' not found.")
        await message.reply(f"Command {cmd} not found.", mention_author=True)
        return

    try:
        Journaling.record("INFO", f"Executing command - Passing to AsyncLauncher.runRunnableModule: '{cmd}'.")
        await AsyncLauncher.runRunnableModule(runnablePath, args, message)
    except Exception as e:
        Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error executing command '{cmd}': {e}", mention_author=True)
