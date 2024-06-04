from kernel.services.DiscordUIService.objects.user import User
from kernel.services.DiscordUIService.objects.server import Server

from typing import List

def parseUser(json_obj: dict) -> User:
    """
    Parse a User object from a JSON object.

    Parameters:
        json_obj (dict): A dictionary object representing a User object in JSON format.
        roles (List[Role]): A list of Role objects associated with the user.

    Returns:
        User: A User object.
    """
    id = json_obj['id']
    name = json_obj['name']
    tags = json_obj['tags']
    roles = json_obj['roles']
    return User(id, name, tags, roles)


def parseServer(json_obj: dict) -> Server:
    """
    Parse a Server object from a JSON object.

    Parameters:
        json_obj (dict): A dictionary object representing a Server object in JSON format.

    Returns:
        Server: A Server object.
    """
    name = json_obj['name']
    id = json_obj['id']
    tags = json_obj['tags']
    roles = json_obj['roles']
    users_json = json_obj['users']
    users = [parseUser(user_json) for user_json in users_json]
    return Server(name, id, tags, roles, users)


def findUser(servers: List[Server], user_id: int, server_id: int) -> User:
    """
    Find a User object from a list of Server objects based on the user_id and server_id.

    Parameters:
        servers (List[Server]): A list of Server objects.
        user_id (int): The id of the User object to be found.
        server_id (int): The id of the Server object containing the User object to be found.

    Returns:
        User: A User object if found, otherwise raises a ValueError.
    """
    for server in servers:
        if server.getId() == server_id:
            users = server.getUsers()
            for user in users:
                if user.getId() == user_id:
                    return user
    raise ValueError(f"No user found with user_id={user_id} and server_id={server_id}")