from discord import message as DiscordMessage

import kernel.services.DiscordUIService.asyncioevents as IOEventsMgr
import kernel.registry as Registry


class DiscordMessageWrapper:
    def __init__(self, message: DiscordMessage) -> None:
        self.message = message
        self.content = message.content
        self.author = message.author
        self.guild = message.guild

    async def replyEvent(self):
        await IOEventsMgr.onOutputEvent(self.message)
        await IOEventsMgr.onReplyOutputEvent(self.message)

    async def sendEvent(self):
        await IOEventsMgr.onOutputEvent(self.message)
        await IOEventsMgr.onSendOutputEvent(self.message)

    async def anyOutputEvent(self):
        await IOEventsMgr.onOutputEvent(self.message)

    async def reply(self, content: str, mention_author: bool = True):
        await self.replyEvent()
        await self.message.reply(content, mention_author=mention_author)

    async def send(self, content: str):
        await self.sendEvent()
        await self.message.channel.send(content)

    async def delete(self):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.Delete", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.delete()

    async def edit(self, content: str):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.Edit", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.edit(content=content)

    async def add_reaction(self, emoji: str):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.AddReaction", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.add_reaction(emoji)

    async def remove_reaction(self, emoji: str):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.RemoveReaction", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.remove_reaction(emoji)

    async def clear_reactions(self):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.ClearReactions", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.clear_reactions()

    async def pin(self):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.Pin", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.pin()

    async def unpin(self):
        if Registry.read("SOFTWARE.CordOS.Events.OutboundEventList.Unpin", default="0") == "1":
            await self.anyOutputEvent()
        await self.message.unpin()

    def getMessageObject(self) -> DiscordMessage:
        return self.message
