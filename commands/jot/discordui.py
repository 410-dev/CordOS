import discord
import os

import kernel.partitionmgr as Partition

from objects.discordmessage import DiscordMessageWrapper


def hasFlag(flagFile, flag):
    if not os.path.exists(flagFile):
        return False

    with open(flagFile, 'r') as f:
        return flag in f.read().split("\n")


async def createNote(args, messageWrapper: DiscordMessageWrapper):
    # If args has "get" or "list", list all notes

    message = messageWrapper.getMessageObject()

    # Check if message.reference is None
    if message.reference is None:
        await message.reply("Please reply a message to jot.", mention_author=True)
        return

    # Convert args to string except for those start with --
    flags: list = [arg for arg in args if arg.startswith("--")]
    title: str = " ".join([arg for arg in args if not arg in flags])

    # Fetch the message
    fetchedMessage = await message.channel.fetch_message(message.reference.message_id)

    # Write the note
    bundle = Partition.files() + f"/jot-notes/{title}.jnote"
    flagsFile = bundle + "/flags"
    contentFile = bundle + "/content"

    if not os.path.exists(bundle):
        os.mkdir(bundle)

    # Check if existing flags have protected flag
    if hasFlag(flagsFile, "--protected"):
        await messageWrapper.reply("This note is protected. Cannot be modified.", mention_author=True)
        return

    # Check if already existed
    fileExists = os.path.exists(contentFile)

    with open(contentFile, 'w') as f:
        f.write(fetchedMessage.content)

    with open(flagsFile, 'w') as f:
        f.write("\n".join(flags))

    await messageWrapper.reply(f"Note {'overwritten' if fileExists else 'added'}. Title: {title}", mention_author=True)


async def mainAsync(args, message: discord.Message):
    try:

        # Drop first argument
        args = args[1:]

        # Create base directory
        if not os.path.exists(Partition.files() + "/jot-notes"):
            os.mkdir(Partition.files() + "/jot-notes")

        if len(args) < 1:
            await message.reply("Usage: jot <note title> or jot get <note title> or jot list", mention_author=True)
            return

        if args[0] == "get":
            if len(args) < 2:
                await message.reply("Usage: jot get <note title>", mention_author=True)
                return

            # Fetch the note
            title = " ".join(args[1:])
            bundle = Partition.files() + f"/jot-notes/{title}.jnote"
            flagsFile = bundle + "/flags"
            contentFile = bundle + "/content"

            if not os.path.exists(bundle) or not os.path.exists(contentFile):
                await message.reply("Note not found.", mention_author=True)
                return

            # Check if existing flags have protected flag
            if hasFlag(flagsFile, "--unreadable"):
                await message.reply("This note is in unreadable mode. Cannot be fetched.", mention_author=True)
                return

            with open(contentFile, 'r') as f:
                content = f.read()

            content = f"Title: {title}\n\nContent:```{content} ```"
            await message.reply(content, mention_author=True)
            return

        if args[0] == "list":
            notes = os.listdir(Partition.files() + "/jot-notes")
            await message.reply(f"Notes:\n```{'\n'.join([note.split('.')[0] for note in notes])} ```", mention_author=True)
            return

        await createNote(args, message)

    except Exception as e:
        await message.reply(f"Error in fetching note. e: {e}", mention_author=True)
