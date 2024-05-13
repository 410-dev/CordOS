import traceback
import kernel.registry as Registry
import kernel.servers as Servers

import kernel.commands.packager.database as Database
import kernel.commands.packager.install as Install
import kernel.commands.packager.uninstall as Uninstall
import kernel.commands.packager.sources as Sources


from kernel.objects.discordmessage import DiscordMessageWrapper


async def chkPermission(message: DiscordMessageWrapper):
    if not Servers.getUserAtServer(message.getMessageObject().guild.id, message.getMessageObject().author.id).hasPermission(Registry.read("SOFTWARE.CordOS.Security.Install")):
        await message.reply(f"You do not have permission to use this command. (Requires {Registry.read("SOFTWARE.CordOS.Security.Install")})", mention_author=True)
        return False
    return True


async def mainAsync(args, message: DiscordMessageWrapper):
    try:
        # Check if user has permission to use this command
        if not await chkPermission(message):
            return

        if Registry.read("SOFTWARE.CordOS.Experimental.Packager", default="0") == "0":
            await message.reply("This feature is experimental and disabled at this time.", mention_author=True)
            return
        else:
            await message.reply("This feature is experimental and may not work as expected.", mention_author=True)

        # Check arguments:
        # install: packager install <package-name> <package-name> <package-name> ...
        # remove: packager remove <package-name> <package-name> <package-name> ...
        # update: packager update <package-name> <package-name> <package-name> ...
        # addsource: packager addsource <index.json url>
        # removesource: packager removesource <index.json url>
        # sync: packager sync

        if len(args) < 2:
            await message.reply("Invalid arguments. Usage: packager <install/remove/update> <package-name> <package-name> ...", mention_author=True)
            return

        # Check if the package is installed
        targetPackages = args[1:]
        unavailablePackages = []
        if args[0] == "install":
            for package in targetPackages:
                if Database.isInstalled(package):
                    unavailablePackages.append(package)
            await message.reply(f"Installing packages: {', '.join(targetPackages)}, Installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "remove":
            for package in targetPackages:
                if not Database.isInstalled(package):
                    unavailablePackages.append(package)
            await message.reply(f"Removing packages: {', '.join(targetPackages)}, Not installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "update":
            if len(targetPackages) == 0:
                targetPackages = Database.getPackagesInstalled()
                await message.reply(f"Checking for updates...",mention_author=True)
            else:
                for package in targetPackages:
                    if not Database.isInstalled(package):
                        unavailablePackages.append(package)
                await message.reply(f"Updating packages: {', '.join(targetPackages)}, Not installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "addsource":
            Sources.add(args[1])
        elif args[0] == "removesource":
            Sources.remove(args[1])
        elif args[0] == "sync":
            Sources.sync()
        else:
            await message.reply("Invalid arguments. Usage: packager <install/remove/update> <package-name> <package-name> ...", mention_author=True)
            return

        if args[0] == "install":
            Install.install(targetPackages, "install")

        elif args[0] == "remove":
            Uninstall.uninstall(targetPackages)

        elif args[0] == "update":
            Install.install(targetPackages, "update")


    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error while running install command. e: {e}", mention_author=True)

