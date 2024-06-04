import time

import discord

from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper

import kernel.services.PrivateVoiceChannels.main as PrivateVoiceChannels
import kernel.journaling as Journaling
import kernel.ipc as IPC
import kernel.registry as Registry

async def mainAsync(args: list, message: DiscordMessageWrapper):
    args.pop(0)
    if len(args) == 0:
        await message.reply("Please provide a title for the voice channel and at least one member.")
        return

    # title = args.pop(0)
    #
    # if len(args) == 0:
    #     await message.reply("Please provide at least one member.")
    #     return

    title = args[0]
    if args[0].startswith("<@"):
        title = "<auto>"
    else:
        args.pop(0)

    members = []
    for member in args:
        idFromMention = member.replace("<@", "").replace(">", "")
        members.append(idFromMention)

    success, returnedmessage = await create(title, members, message)
    messageLiveTime = int(Registry.read("SOFTWARE.CordOS.Events.User.DiscordUI.PrivateVoiceChannelLiveTime", default="5", writeDefault=True))
    returnedmessage += f" Both this message and the original message will be deleted in {messageLiveTime} seconds."
    await message.reply(returnedmessage, delete_after=0)
    time.sleep(messageLiveTime)
    await message.delete()


async def create(title: str, memberIDs: list, message: DiscordMessageWrapper) -> (bool, str): # Success
    try:
        guildID = message.guild.id
        client: discord.Client = IPC.read("discord.client", None)
        if client is None:
            Journaling.record("ERROR", "The Discord client is not available: IPC read \"discord.client\" returned None.")
            return False, "The Discord client is not available."
        guild = client.get_guild(guildID)
        if guild is None:
            Journaling.record("ERROR", f"The guild {guildID} is not available.")
            return False, f"The guild {guildID} is not available."

        # Create a private (invisible) voice channel
        Journaling.record("INFO", f"Creating private voice channel {title} with {len(memberIDs)} members.")

        members = []
        for member in memberIDs:
            Journaling.record("INFO", f"Processing member {member}.")
            memberObject = guild.get_member(int(member))
            if memberObject is None:
                Journaling.record("ERROR", f"Member {member} not found.")
                continue
            members.append(memberObject)

        if title == "<auto>":
            title = ""
            Journaling.record("INFO", "Auto-generating title.")
            for member in members:
                title += f"{member.name}, "
            Journaling.record("INFO", f"Title: {title}")
            title = title[:-2]
            Journaling.record("INFO", f"Title updated: {title}")

        if len(title) > 100:
            title = title[:97] + "..."

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            guild.me: discord.PermissionOverwrite(connect=True)
        }
        vc = await guild.create_voice_channel(title, overwrites=overwrites, position=0, user_limit=len(memberIDs))
        if vc is None:
            Journaling.record("ERROR", "The voice channel could not be created.")
            return False, "The voice channel could not be created."

        for member in members:
            if member.voice is not None:
                Journaling.record("INFO", f"(Member already in voice channel) Moving {member.name} to channel '{vc.name}'.")
                await member.move_to(vc)
            else:
                Journaling.record("INFO", f"Setting permissions for {member.name} in channel '{vc.name}'.")
                await vc.set_permissions(member, connect=True, view_channel=True, speak=True, stream=True, move_members=True, use_voice_activation=True, priority_speaker=True)

        Journaling.record("INFO", f"Private voice channel '{title}' created.")
        PrivateVoiceChannels.PrivateVoiceChannelMemory.add(vc.id, guildID, members)

    except Exception as e:
        return False, f"An error occurred while creating the private voice channel: {e}"
    return True, f"Private voice channel '{title}' created."