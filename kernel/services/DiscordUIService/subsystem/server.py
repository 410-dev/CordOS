import json
from kernel.services.DiscordUIService.objects.server import Server
from kernel.services.DiscordUIService.objects.user import User
import kernel.services.DiscordUIService.object as Objects
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation

import kernel.journaling as Journaling


def getContainer(message = None) -> str:
    container = Isolation.getCallerContainerPath()
    if container is None:
        if message is not None:
            Journaling.record("INFO", f"Using generated container path since container is None for {message.guild.id}.")
            return Isolation.getContainerPath(message, "server.json")
        Journaling.record("WARNING", "Container path is None while message object is also none.")
        return None
    if not container.endswith("/"):
        container += "/"
    container += "server.json"
    Journaling.record("INFO", f"Server container path: {container}")
    return container


def load(message = None) -> Server:
    path = getContainer(message = message)
    if path is None:
        return None

    with open(path) as f:
        servers = json.load(f)
        if servers is None:
            return None
        return Objects.parseServer(servers)


def save(server: Server, message):
    with open(getContainer(message=message), 'w') as f:
        if server is None:
            json.dump({
                "name": message.guild.name,
                "id": message.guild.id,
                "tags": [],
                "roles": [],
                "users": []
            }, f, indent=4)
            return
        json.dump(server.toJson(), f, indent=4)


def getUserAtServer(message) -> User:
    server = load(message=message)
    if server is None:
        Journaling.record("ERROR", "Server object is None.")
        return None
    return server.getUser(message.author.id)


def updateUserAtServer(user: User, message):
    server = load(message=message)
    if server is None:
        Journaling.record("ERROR", "Server object is None.")
        return
    server.updateUserObject(user, overwrite=True)
    Journaling.record("INFO", f"User {user.getName()} updated in server cache.")
    save(server, message)
