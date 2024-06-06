import json
from kernel.services.DiscordUIService.objects.server import Server
from kernel.services.DiscordUIService.objects.user import User
import kernel.services.DiscordUIService.object as Objects
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation


def getContainer(message = None) -> str:
    container = Isolation.getCallerContainerPath()
    if container is None:
        if message is not None:
            return Isolation.getContainerPath(message, "server.json")
        return None
    container += "servers.json"
    return container


def load() -> Server:
    path = getContainer()
    if path is None:
        return None

    with open(path) as f:
        servers = json.load(f)
        if servers is None:
            return None
        return Objects.parseServer(servers)


def save(server: Server, message):
    with open(getContainer(message=message), 'w') as f:
        json.dump(server.toJson(), f, indent=4)


def getUserAtServer(message) -> User:
    server = load()
    if server is None:
        return None
    return server.getUser(message.author.id)
