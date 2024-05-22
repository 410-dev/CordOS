import discord
import datetime

import kernel.ipc as IPC
import kernel.io as IO

from kernel.objects.discordmessage import DiscordMessageWrapper


class EmbeddedMessage:

    def __init__(self, message: DiscordMessageWrapper, title="", description="", color=0x00ff00, footer="", timestamp=datetime.datetime.now(), expireAfterSeconds=None):
        self.title = title
        self.description = description
        self.color = color
        self.footer = footer
        self.timestamp = timestamp
        self.messageWrapper: DiscordMessageWrapper = message
        if message is not None:
            self.message: discord.Message = message.getMessageObject()
        self.expire = expireAfterSeconds

    async def send(self):
        embed = self.getEmbed()
        await self.messageWrapper.sendEvent()
        await self.messageWrapper.send(embed=embed, delete_after=self.expire, embeddedMessageWrapper=self)

    async def sendAsReply(self, mention_author=True):
        embed = self.getEmbed()
        await self.messageWrapper.replyEvent()
        await self.messageWrapper.reply(embed=embed, mention_author=mention_author, delete_after=self.expire, embeddedMessageWrapper=self)

    def getEmbed(self):
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)
        embed.set_footer(text=self.footer)
        embed.timestamp = self.timestamp
        return embed

    def stringify(self):
        return f"[Color: {self.color}, Time: {self.timestamp}] {self.title}: {self.description} ({self.footer})"

    def stringifySimpler(self):
        return f"{self.title}: {self.description}"

    def stringifySimplest(self):
        return self.description

    def toDict(self):
        return {
            "title": self.title,
            "description": self.description,
            "color": self.color,
            "footer": self.footer,
            "timestamp": self.timestamp,
            "expire": self.expire,
            "webhookURL": self.webhookURL
        }

    def get(self, key):
        return self.toDict()[key]