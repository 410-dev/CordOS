import kernel.registry as Registry


class User:
    
    def __init__(self, id: int, name: str, tags: list, roles: list):
        self.id = id
        self.name = name
        self.tags = tags
        self.roles = roles
    
    
    def getId(self):
        return self.id
    
    
    def setId(self, id: int):
        self.id = id
    
    
    def getName(self):
        return self.name
    
    
    def setName(self, name: str):
        self.name = name
    
    
    def getTags(self):
        return self.tags
    
    
    def setTags(self, tags: list):
        self.tags = tags
        
    def hasTag(self, tag: str):
        return tag in self.tags
    
    def hasPermission(self, permissionTag: str):
        return self.hasTag(permissionTag) or self.hasTag(Registry.read("SOFTWARE.CordOS.Security.Master"))
    
    def getRoles(self):
        return self.roles
    
    def setRoles(self, roles: list):
        self.roles = roles
    
    
    def addTag(self, tag: str):
        self.tags.append(tag)
    
    
    def addTags(self, tags: list):
        self.tags.extend(tags)
    
    
    def removeTag(self, tag: str):
        self.tags.remove(tag)


    def addRole(self, role: str):
        self.roles.append(role)
    
    
    def addRoles(self, roles: list):
        self.roles.extend(roles)
    
    
    def removeRole(self, role: str):
        self.roles.remove(role)

    def toJson(self):
        return {
            "id": self.getId(),
            "name": self.getName(),
            "tags": self.getTags(),
            "roles": self.getRoles()
        }