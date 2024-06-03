import time
import traceback
import discord

import kernel.journaling as Journaling
import kernel.ipc as IPC
import kernel.registry as Registry

import kernel.services.DiscordUIService.main as DiscordUIService


class PrivateVoiceChannelMemory:

    channels = {}

    @staticmethod
    def add(channelID: int, guildID: int, members: list):
        PrivateVoiceChannelMemory.channels[channelID] = {
            "id": channelID,
            "guild": guildID,
            "members": members,
            "time": time.time()
        }

    @staticmethod
    def remove(channelID: int):
        PrivateVoiceChannelMemory.channels.pop(channelID)

    @staticmethod
    def get(channelID: int) -> dict:
        return PrivateVoiceChannelMemory.channels.get(channelID)



async def destroy(channelID: int) -> (bool, str): # Success
    channel: dict = PrivateVoiceChannelMemory.get(channelID)
    if channel is None:
        Journaling.record("ERROR", f"Voice channel {channelID} not found in memory.")
        return False
    try:
        Journaling.record("INFO", f"Getting Discord client.")
        client: discord.Client = IPC.read("discord.client", None)
        if client is None:
            Journaling.record("ERROR", "The Discord client is not available: IPC read \"discord.client\" returned None.")
            return False, "The Discord client is not available."
        Journaling.record("INFO", f"Getting guild {channel['guild']} from client.")
        guild = client.get_guild(channel['guild'])
        if guild is None:
            Journaling.record("ERROR", f"The guild {channel['guild']} is not available.")
            return False, f"The guild {channel['guild']} is not available."

        Journaling.record("INFO", f"Getting channel {channelID} from guild {guild.id}.")
        vc = guild.get_channel(channelID)
        if vc is None:
            Journaling.record("ERROR", f"The voice channel {channelID} is not available.")
            return False, f"The voice channel {channelID} is not available."

        Journaling.record("INFO", f"Destroying voice channel {channelID}.")
        await vc.delete()

        Journaling.record("INFO", f"Removing channel {channelID} from memory.")
        PrivateVoiceChannelMemory.remove(channelID)

        Journaling.record("INFO", f"Voice channel {channelID} destroyed.")
        return True, f"Voice channel {channelID} destroyed."
    except Exception as e:
        traceback.print_exc()
        Journaling.record("ERROR", f"An error occurred while destroying the private voice channel: {e}")
        return False, f"An error occurred while destroying the private voice channel: {e}"


def main():
    while IPC.canRepeatUntilShutdown():
        time.sleep(1)
        try:
            client: discord.Client = IPC.read("discord.client", None)
            if client is None:
                continue

            for guild in client.guilds:
                for channel in guild.voice_channels:
                    if channel is None:
                        continue
                    if channel.id not in PrivateVoiceChannelMemory.channels:
                        continue
                    Journaling.record("INFO", f"Checking voice channel {channel.id}. Time: {time.time() - PrivateVoiceChannelMemory.channels[channel.id]['time']}. Members: {len(channel.members)}.")
                    timeout = int(Registry.read("SOFTWARE.CordOS.Kernel.Services.PrivateVoiceChannels.Timeout", default="300", writeDefault=True))
                    if time.time() - PrivateVoiceChannelMemory.channels[channel.id]["time"] > timeout and len(channel.members) == 0:
                        Journaling.record("INFO", f"Destroying voice channel {channel.id}.")
                        DiscordUIService.coroutineResolve(destroy, {"channelID": channel.id}, "PrivateVoiceChannels.destroy")

        except Exception as e:
            traceback.print_exc()
            errortrace = traceback.format_exc()
            print(errortrace)
            Journaling.record("ERROR", f"An error occurred in the Private Voice Channels service: {errortrace}")
            continue
