import traceback
import kernel.registry as Registry
import kernel.servers as Servers
import kernel.journaling as Journaling

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

        Journaling.record("INFO", f"Running packager command with args: {args}")

        if len(args) < 2:
            await message.reply("Invalid arguments (Too few). Usage: packager <install/remove/update> <package-name> <package-name> ...", mention_author=True)
            return

        # Check if the package is installed
        args = args[1:]
        targetPackages = args[1:]
        unavailablePackages = []
        if args[0] == "install":
            for package in targetPackages:
                if database.isInstalled(package):
                    unavailablePackages.append(package)
            await message.reply(f"Installing packages: {', '.join(targetPackages)}, Installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "installurl":
            await message.reply(f"Installing packages from URL: {', '.join(targetPackages)}", mention_author=True)
        elif args[0] == "remove":
            for package in targetPackages:
                if not database.isInstalled(package):
                    unavailablePackages.append(package)
            await message.reply(f"Removing packages: {', '.join(targetPackages)}, Not installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "update":
            if len(targetPackages) == 0:
                targetPackages = database.getPackagesInstalled()
                await message.reply(f"Checking for updates...",mention_author=True)
            else:
                for package in targetPackages:
                    if not database.isInstalled(package):
                        unavailablePackages.append(package)
                await message.reply(f"Updating packages: {', '.join(targetPackages)}, Not installed packages: {', '.join(unavailablePackages)}", mention_author=True)
        elif args[0] == "addsource":
            sources.add(args[1])
        elif args[0] == "removesource":
            sources.remove(args[1])
        elif args[0] == "sync":
            sources.sync()
        else:
            await message.reply(f"Invalid arguments (Unknown action: {args[0]}). Usage: packager <install/remove/update> <package-name> <package-name> ...", mention_author=True)
            return

        if args[0] == "install":
            result = install.install(targetPackages, "install")
            await message.reply(f"{result[1]}", mention_author=True)

        if args[0] == "installurl":
            result = install.install(targetPackages, "install", url=True)
            await message.reply(f"{result[1]}", mention_author=True)

        elif args[0] == "remove":
            uninstall.uninstall(targetPackages)

        elif args[0] == "update":
            result = install.install(targetPackages, "update")
            await message.reply(f"{result[1]}", mention_author=True)


    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error while running install command. e: {e}", mention_author=True)

