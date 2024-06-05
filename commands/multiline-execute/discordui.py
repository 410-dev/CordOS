import kernel.events.interaction.DiscordUIInterpreter.discordui as DiscordUIInterpreter

import kernel.registry as Registry

from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper

async def mainAsync(args, message: DiscordMessageWrapper):
    prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
    msgContent: str = message.content[len(prefix):]
    args = msgContent.split("\n")
    if args[0] != "multiline-execute":
        await message.reply("This command should not contain other command in caller execution.", mention_author=True)
        return
    args.pop(0)
    for arg in args:
        await DiscordUIInterpreter.execute(arg, message)
