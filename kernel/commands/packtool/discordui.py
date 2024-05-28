import kernel.registry as Registry
import kernel.servers as Servers
import kernel.commands.packtool.install as Install
import kernel.commands.packtool.remove as Remove

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

        if args[1] == "install":
            if len(args) < 3:
                await message.reply("Usage: packtool install <url>...")
                return
            Install.install(args[2:])

        elif args[1] == "remove":
            if len(args) < 3:
                await message.reply("Usage: packtool remove <name>...")
                return
            Remove.remove(args[2:])

        elif args[1] == "list":
            pass

    except Exception as e:
        await message.reply(f"Error while running executive. e: {e}", mention_author=True)
        return
