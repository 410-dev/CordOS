from objects.user import User

import kernel.registry as Registry

class Server:
    def __init__(self, name: str, id: int, tags: list, roles: list, users: list):
        self._name = name
        self._id = id
        self._tags = tags
        self._roles = roles
        self._users = users

    def getName(self) -> str:
        return self._name

    def setName(self, name: str):
        self._name = name

    def getId(self) -> int:
        return self._id

    def setId(self, id: int):
        self._id = id

    def getTags(self) -> list:
        return self._tags

    def setTags(self, tags: list):
        self._tags = tags

    def addTag(self, tag):
        self._tags.append(tag)

    def removeTag(self, tag):
        self._tags.remove(tag)

    def getRoles(self) -> list:
        return self._roles

    def setRoles(self, roles: list):
        self._roles = roles

    def addRole(self, role):
        self._roles.append(role)

    def removeRole(self, role):
        self._roles.remove(role)

    def getUsers(self) -> list:
        return self._users

    def setUsers(self, users: list):
        self._users = users

    def addUser(self, user):
        self._users.append(user)

    def removeUser(self, user):
        self._users.remove(user)
        
    def getUser(self, userID: int) -> User:
        for user in self._users:
            if str(user.getId()) == str(userID):
                return user
        return None
    
    def updateUser(self, userID: int, userName: str, userTags: list, userRoles: list, overwrite: bool = False):
        for user in self._users:
            if str(user.getId()) == str(userID):
                user.setName(userName)
                if overwrite:
                    if Registry.read("SOFTWARE.CordOS.Kernel.PrintLogs") == "1": print("Overwriting user tags and roles")
                    user.setTags(userTags)
                    user.setRoles(userRoles)
                return
            
        self._users.append(User(userID, userName, userTags, userRoles))
    
    def updateUserObject(self, user: User, overwrite: bool = False):
        self.updateUser(user.getId(), user.getName(), user.getTags(), user.getRoles(), overwrite)
    
    def getTagsAsJsonObjectLists(self) -> list:
        return [tag.toJson() for tag in self._tags]
    
    def getRolesAsJsonObjectLists(self) -> list:
        return [role.toJson() for role in self._roles]
    
    def getUsersAsJsonObjectLists(self) -> list:
        return [user.toJson() for user in self._users]
    
    def toJson(self) -> dict:
        return {
            "name": self.getName(),
            "id": self.getId(),
            "tags": self.getTagsAsJsonObjectLists(),
            "roles": self.getRolesAsJsonObjectLists(),
            "users": self.getUsersAsJsonObjectLists()
        }