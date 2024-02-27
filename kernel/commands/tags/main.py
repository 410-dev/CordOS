import traceback
import kernel.registry as Registry
import kernel.servers as Servers

from objects.user import User
from objects.server import Server

class Tags:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.user: User = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)

    async def exec(self):
        
        try:
            if not self.user.hasPermission(Registry.read("SOFTWARE.CordOS.Security.Tags")):
                await self.message.reply(f"You do not have permission to use this command. (Requires {Registry.read('SOFTWARE.CordOS.Security.Tags')})", mention_author=True)
                return
            
            if len(self.args) != 3:
                await self.message.reply(f"Invalid number of arguments. Expected 3, got {len(self.args)}", mention_author=True)
                return
            
            action: str = self.args[0]
            target: str = self.args[1].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
            tags: list = self.args[2].split(" ")
            
            targetUserObject: User = Servers.getUserAtServer(self.message.guild.id, target)
            
            messageStr = ""
            unprocessed: list = []
            
            if action == "add":
                for tag in tags:
                    if targetUserObject.hasTag(tag):
                        unprocessed.append(tag)
                        continue
                    
                    targetUserObject.addTag(tag)
                messageStr = f"Added tags {tags} to user {targetUserObject.name}"
                if len(unprocessed) > 0:
                    messageStr += f"\nTags {unprocessed} were already added to user {targetUserObject.name}"
                
            elif action == "remove":
                for tag in tags:
                    if not targetUserObject.hasTag(tag):
                        unprocessed.append(tag)
                        continue
                    targetUserObject.removeTag(tag)
                messageStr = f"Removed tags {tags} from user {targetUserObject.name}"
                if len(unprocessed) > 0:
                    messageStr += f"\nTags {unprocessed} were not removed to user {targetUserObject.name}"
                
            # Update server json
            serverObject: Server = Servers.getServer(self.message.guild.id)
            serverObject.updateUserObject(targetUserObject, overwrite=True)
            Servers.updateServerObject(serverObject)
            
            await self.message.reply(messageStr, mention_author=True)
            
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error while updating user information: {e}", mention_author=True)
            