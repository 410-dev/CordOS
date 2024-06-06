import json
import kernel.registry as Registry
import kernel.io as IO
from kernel.services.DiscordUIService.objects.server import Server
from kernel.services.DiscordUIService.objects.user import User
import kernel.services.DiscordUIService.object as Objects
import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation

from typing import List

def getContainer():
    # container = Isolation.getCallerContainerPath()
    # container += "etc/servers.json"
    # return container
    return "etc/servers.json"

def load() -> List[Server]:
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function load() in servers.py")
    """
    Read the servers file and return a dictionary object.

    Returns:
        List[Server]: A dictionary object representing the servers file.
    """

    with open(getContainer()) as f:
        servers = json.load(f)['servers']
        
        if servers is None:
            return []
        
        if len(servers) == 0:
            return []
        
        serverList: list = []
        for svjsonobj in servers:
            sv = Objects.parseServer(svjsonobj)
            serverList.append(sv)
            
        return serverList

def save(servers: List[Server]):
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function save() in servers.py")
    """
    Save the servers file.

    Parameters:
        servers (list): A dictionary object representing the servers file.
    """
    with open(getContainer(), 'w') as f:
        jsonObject: dict = {}
        jsonObject['servers'] = []
        for sv in servers:
            jsonObject['servers'].append(sv.toJson())
        json.dump(jsonObject, f, indent=4)
        

def addServer(server: Server):
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function addServer() in servers.py")
    """
    Add a server to the server cache.
    
    Parameters:
        serverCache (list): A list of Server objects.
        server (Server): The server to add.
    """
    serverCache = load()
    serverCache.append(server)
    save(serverCache)
    

def updateServerObject(server: Server):
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function updateServerObject() in servers.py")
    serverCache = load()
    for sv in serverCache:
        if str(sv.getId()) == str(server.getId()):
            serverCache.remove(sv)
            serverCache.append(server)
            save(serverCache)
            return
    addServer(server)
    
    
def updateServer(message) -> List[Server]:
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function updateServer() in servers.py")
    """
    Update a server in the server cache. If not found, add it.
    
    Parameters:
        serverCache (list): A list of Server objects.
        message (discord.Message): The server to update.
    """
    serverCache = load()
    serverID = message.guild.id
    
    userID = message.author.id
    userName = message.author.name

    for sv in serverCache:
        if sv.getId() == serverID:
            sv.updateUser(userID, userName, [], [])
            save(serverCache)
            return serverCache
    
    serverName = message.guild.name
    server = Server(name=serverName, id=serverID, tags=[], roles=[], users=[])
    server.updateUser(userID, userName, [], [])
    if Registry.read("SOFTWARE.CordOS.Kernel.PrintLogs") == "1": print(f"Added server {serverName}({serverID})")
    if Registry.read("SOFTWARE.CordOS.Kernel.PrintLogs") == "1": print(f"Cache: {serverCache}")
    addServer(server)
    return serverCache

def getServer(id: int) -> Server:
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function getServer() in servers.py")
    """
    Get a server from the server cache.
    
    Parameters:
        serverCache (list): A list of Server objects.
        id (int): The ID of the server to get.
    """
    serverCache = load()
    for server in serverCache:
        if server.getId() == id:
            return server
    return None

def getUserAtServer(id: int, userID: int) -> User:
    IO.println("[SERVERS APIv1] WARNING! Using deprecated function getUserAtServer() in servers.py")
    """
    Get a user from a server in the server cache.
    
    Parameters:
        serverCache (list): A list of Server objects.
        id (int): The ID of the server to get.
        userID (int): The ID of the user to get.
    """
    server = getServer(id)
    if server is None:
        return None
    return server.getUser(userID)
