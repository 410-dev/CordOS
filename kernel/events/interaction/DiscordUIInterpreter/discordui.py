import kernel.launchcmd as Launcher
import kernel.registry as Registry
import kernel.journaling as Journaling
from kernel.services.DiscordUIService.objects.user import User
from kernel.services.DiscordUIService.objects.server import Server as ServerO

import kernel.services.DiscordUIService.asynclauncher as AsyncLauncher
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation
import kernel.services.DiscordUIService.subsystem.server as Server

import traceback

async def mainAsync(message):
    prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
    msgContent: str = message.content[len(prefix):]
    await execute(msgContent, message)


async def execute(lineToExecute: str, message):
    try:
        args: list = Launcher.splitArguments(lineToExecute)
        cmd: str = Launcher.getCommand(args)
        Journaling.record("INFO", f"Command '{cmd}' executed by {message.author.name}#{message.author.discriminator}.")
        if not Isolation.getIsolationAvailable(message):
            Journaling.record("INFO", f"Isolation not available for guild {message.guild.id}.")
            runnablePath: str = Launcher.getRunnableModule(args, "discordui")
        else:
            paths = []
            if Isolation.getIsolationPermission(message, "local.commands.execute"):
                paths.append(Isolation.getContainerPath(message, "commands"))
            if Isolation.getIsolationPermission(message, "global.commands.execute"):
                paths.append("commands")
            if Isolation.getIsolationPermission(message, "kernel.commands.execute"):
                paths.append("kernel/commands")
            registryData = ','.join(paths)
            Journaling.record("INFO", "Updating user information in server cache.")
            user: User = Server.getUserAtServer(message)
            if user is None:
                Journaling.record("INFO", "User not found in server cache. Creating new user.")
                user = User(message.author.id, message.author.name, [], [])
            else:
                Journaling.record("INFO", "User found in server cache. Updating user.")
                user.setName(message.author.name)
            Server.updateUserAtServer(user, message)
            Isolation.setRegistry(message, "SOFTWARE.CordOS.Kernel.Programs.Paths", registryData)
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