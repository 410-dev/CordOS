# from kernel.services.DiscordUIService.main import DiscordUIServiceIPCMemory
# from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper
#
# import discord
# import asyncio
#
# import kernel.partitionmgr as PartitionMgr
#
#
# async def main(args: list, message: DiscordMessageWrapper):
#     # grab the user who sent the command
#     user = message.author
#     voice_channel = user.voice.voice_channel
#     channel = None
#     client = DiscordUIServiceIPCMemory.client
#
#     # only play music if user is in a voice channel
#     if voice_channel != None:
#         # grab user's voice channel
#         channel = voice_channel.name
#         await client.say('User is in channel: ' + channel)
#         # create StreamPlayer
#         vc = await client.join_voice_channel(voice_channel)
#         player = vc.create_ffmpeg_player('vuvuzela.mp3', after=lambda: print('done'))
#         player.start()
#         while not player.is_done():
#             await asyncio.sleep(1)
#         # disconnect after the player has finished
#         player.stop()
#         await vc.disconnect()
#     else:
#         await client.say('User is not in a channel.')