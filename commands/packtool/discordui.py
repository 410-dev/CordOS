import kernel.registry as Registry
import kernel.services.DiscordUIService.servers as Servers


async def checkPermission(message):
    permission = Registry.read("SOFTWARE.CordOS.Security.Services")
    user = Servers.getUserAtServer(message.guild.id, message.author.id)

    if user.hasPermission(permission) == False:
        await message.reply(f"You do not have permission to use this command. (Requires {permission})", mention_author=True)
        return False
    return True


async def mainAsync(args: list, message):
    try:
        if not await checkPermission(message):
            return

        if len(args) < 2:
            await message.reply("Usage: packtool <install|remove|list> <url|name>...")
            return

        if args[1] == "install" or args[1] == "patch":
            if len(args) < 3:
                await message.reply("Usage: packtool install|patch <url>...")
                return
            ignoreDependencies = False
            ignoreConflicts = False
            reinstall = False
            if len(args) > 3 and '--ignore-dependencies' in args:
                ignoreDependencies = True
            if len(args) > 3 and '--ignore-conflicts' in args:
                ignoreConflicts = True
            if len(args) > 3 and '--reinstall' in args:
                reinstall = True
            result = install.install(args[2:], args[1], ignoreDependencies, ignoreConflicts, reinstall)
            if not result:
                await message.reply("Failed to install package(s). Check logs for more information.")
                return
            else:
                await message.reply("Package(s) installed successfully.")
                return

        elif args[1] == "remove":
            if len(args) < 3:
                await message.reply("Usage: packtool remove <name>...")
                return
            ignoreDependencies = False
            removeAsChain = False
            if len(args) > 3 and '--ignore-dependencies' in args:
                ignoreDependencies = True
            if len(args) > 3 and '--chain' in args:
                removeAsChain = True
            result = remove.remove(args[2:], ignoreDependencies, removeAsChain)
            if not result:
                await message.reply("Failed to remove package(s). Check logs for more information.")
                return
            else:
                await message.reply("Package(s) removed successfully.")
                return

        elif args[1] == "list":
            output = list.listPackages()
            await message.reply(output)

    except Exception as e:
        await message.reply(f"Error while running executive. e: {e}", mention_author=True)
        return
