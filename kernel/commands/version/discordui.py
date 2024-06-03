import kernel.registry as Registry
import kernel.ipc as IPC
from kernel.objects.embedmsg import EmbeddedMessage


async def mainAsync(args: list, message):
    try:
        foundation = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Foundation")
        version = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
        build = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Build")
        botName = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotName")
        botVer = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotVersion")
        isSafe = "Normal Mode" if not IPC.read("kernel.safemode") else "Safe Mode"

        if Registry.read("SOFTWARE.CordOS.Experimental.EmbeddedMessage", default="0") == "0":
            await message.reply(f"Version Profiling:\n\nCore System: {foundation} {version} (build {build}) {'(TEST VERSION) ' if '.alpha.' in build or '.beta.' in build or '.test.' in build else ''} {isSafe}\nBot: {botName} {botVer}", mention_author=True)

        else:
            msg = EmbeddedMessage(message, title="Version Profiling",
                                  description=f"**Core System**\n{foundation} {version}\nBuild {build}\n\n**Bot**\n{botName} {botVer}\n\n**Boot State**\n{isSafe}",
                                  footer="CordOS")
            await msg.sendAsReply()

    except Exception as e:
        await message.reply(f"Error loading profile: {e}", mention_author=True)
