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
        
    def hasTag(self, tagId: str):
        for tag in self.tags:
            if tag["id"] == tagId:
                return True
        return False

    def getTag(self, tagId: str):
        for tag in self.tags:
            if tag["id"] == tagId:
                return tag
        return None

    def getTagValue(self, tagId: str):
        for tag in self.tags:
            if tag["id"] == tagId:
                return tag["value"]
        return None
    
    def hasPermission(self, permissionTag: str):
        # Get tag of current user
        permissionValue = self.getTagValue("permission")
        if permissionValue is None:
            print(f"User {self.getName()} does not have permission tag.")
            return False

        # Convert value to integer
        permissionValue = Registry.read(f"SOFTWARE.CordOS.Security.Users.{permissionValue}", default=None, writeDefault=False)
        try:
            permissionValue = int(permissionValue)
        except:
            print(f"User {self.getName()} does not have a valid permission tag (not an integer).")
            return False

        # Check if permission is valid
        if permissionValue < 0 or permissionValue > 32767:
            print(f"User {self.getName()} does not have a valid permission tag (out of range).")
            return False

        # Get tag of permission value from registry
        permissionDefinition = Registry.read(f"SOFTWARE.CordOS.Security.Definitions.{permissionTag}", default=None, writeDefault=False)
        if permissionDefinition is None:
            print(f"Permission definition {permissionTag} does not exist.")
            return False

        # Convert value to integer
        try:
            permissionDefinition = int(permissionDefinition)
        except:
            print(f"Permission definition {permissionTag} is not a valid integer.")
            return False

        # Check if permission is valid
        if permissionDefinition < 0 or permissionDefinition > 32767:
            print(f"Permission definition {permissionTag} is not a valid integer (out of range).")
            return False

        # Check if user has permission
        print(f"User {self.getName()} has permission of {permissionValue} and action requires permission of {permissionDefinition}.")
        return permissionValue >= permissionDefinition


    def getRoles(self):
        return self.roles
    
    def setRoles(self, roles: list):
        self.roles = roles
    
    
    def addTag(self, tagName: str, tagValue: str):
        self.removeTag(tagName)
        self.tags.append({
            "id": tagName,
            "value": tagValue
        })
    
    
    def addTags(self, tags: list):
        for tag in tags:
            self.addTag(tag["id"], tag["value"])
    
    
    def removeTag(self, tagId: str):
        for tag in self.tags:
            if tag["id"] == tagId:
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