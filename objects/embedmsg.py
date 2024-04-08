import discord
import datetime


class EmbeddedMessage:

    def __init__(self, message, title="", description="", color=0x00ff00, footer="", timestamp=datetime.datetime.now(), expireAfterSeconds=None):
        self.title = title
        self.description = description
        self.color = color
        self.footer = footer
        self.timestamp = timestamp
        self.message = message
        self.expire = expireAfterSeconds

    async def send(self):
        embed = self.getEmbed()
        await self.message.channel.send(embed=embed, delete_after=self.expire)

    async def sendAsReply(self, mention_author=True):
        embed = self.getEmbed()
        await self.message.reply(embed=embed, mention_author=mention_author, delete_after=self.expire)

    def getEmbed(self):
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)
        embed.set_footer(text=self.footer)
        embed.timestamp = self.timestamp
        return embed
