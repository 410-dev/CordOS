import traceback
import kernel.config as Config
import kernel.registry as Registry
import kernel.servers as Servers

from objects.discordmessage import DiscordMessageWrapper


async def chkPermission(message: DiscordMessageWrapper):
    if not Servers.getUserAtServer(message.getMessageObject().guild.id, message.getMessageObject().author.id).hasPermission(Registry.read("SOFTWARE.CordOS.Security.Install")):
        await message.reply(f"You do not have permission to use this command. (Requires {Registry.read("SOFTWARE.CordOS.Security.Install")})", mention_author=True)
        return False
    return True


async def main(args, message: DiscordMessageWrapper):
    try:
        # Check if user has permission to use this command
        if not await chkPermission(message):
            return

        await message.reply("This command is not implemented yet.", mention_author=True)

    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error while running install command. e: {e}", mention_author=True)

