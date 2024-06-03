import discord

import kernel.registry as Registry
import kernel.journaling as Journaling

import traceback

from kernel.objects.discordmessage import DiscordMessageWrapper

def journalIndex() -> str:
    labels: list = Journaling.JournalingContainer.journals.keys()
    index: str = ""
    for label in labels:
        index += f"{label}\n"
    return index

def getLastNLines(target: str, n: int) -> str:
    journal = Journaling.JournalingContainer.journals[target]
    entries = journal["entries"]
    if n > len(entries):
        n = len(entries)
    return "".join(entries[-n:])


async def mainAsync(args: list, message: DiscordMessageWrapper) -> None:
    try:
        # Available: dump, list, get
        if len(args) < 2:
            await message.reply("Not enough arguments.\nUsage: journalctl <dump|list|read> (target)", mention_author=True)
            return
        if args[1] == "dump":
            dumpPath = Journaling.JournalingContainer.dump()

            if Registry.read("SOFTWARE.CordOS.Kernel.DiscordUIService.AllowExposeJournalDumpToEveryone", default="0") == "1":
                await message.getMessageObject().reply(f"Journal dumped. The dump file is attached below.", mention_author=True, file=discord.File(dumpPath))
            else:
                await message.reply("Journal dumped. The dump file is only accessible locally.", mention_author=True)

        elif args[1] == "list":
            await message.reply(journalIndex(), mention_author=True)

        elif args[1] == "read":
            if len(args) < 3:
                await message.reply("Not enough arguments.\nUsage: journalctl read <target>", mention_author=True)
                return
            target = args[2]
            if target not in Journaling.JournalingContainer.journals.keys():
                await message.reply("Target not found.", mention_author=True)
                return
            await message.reply(getLastNLines(target, 10), mention_author=True)

    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error in journalctl. e: {e}", mention_author=True)
