# Shows the current environment is either isolation or global
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation

async def mainAsync(args: list, message):
    if Isolation.getIsolationAvailable(message):
        await message.reply("Environment: Isolation", mention_author=True)
    else:
        await message.reply("Environment: Global", mention_author=True)
