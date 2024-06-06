import discord

import kernel.services.DiscordUIService.subsystem.server as Server
from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper

from typing import List

def hasPermission(message: DiscordMessageWrapper, permission: str) -> bool:
    user = Server.getUserAtServer(message.getMessageObject())
    return user.hasPermission(permission)


def hasDiscordRoleByName(message: DiscordMessageWrapper, role: str) -> bool:
    msgObject: discord.Message = message.getMessageObject()
    roles: List[discord.Role] = msgObject.author.roles
    for r in roles:
        if r.name == role:
            return True
    return False


def hasDiscordRoleById(message: DiscordMessageWrapper, role: int) -> bool:
    msgObject: discord.Message = message.getMessageObject()
    roles: List[discord.Role] = msgObject.author.roles
    for r in roles:
        if r.id == role:
            return True
    return False


def hasDiscordRoleInList(message: DiscordMessageWrapper, roles: List[str]) -> bool:
    msgObject: discord.Message = message.getMessageObject()
    roleNames: List[str] = [r.name for r in msgObject.author.roles]
    for r in roles:
        if r in roleNames:
            return True
    return False