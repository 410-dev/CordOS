import traceback
import kernel.registry as Registry
import kernel.services.DiscordUIService.subsystem.server as Server

from kernel.services.DiscordUIService.objects.user import User
from kernel.services.DiscordUIService.objects.server import Server

class Tags:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.user: User = Server.getUserAtServer(self.message.getMessageObject())

    async def mainAsync(self):
        
        try:
            if len(self.args) > 0:
                self.args.pop(0)

            if not self.user.hasPermission(Registry.read("SOFTWARE.CordOS.Security.Tags")):
                await self.message.reply(f"You do not have permission to use this command. (Requires {Registry.read('SOFTWARE.CordOS.Security.Tags')})", mention_author=True)
                return
            
            if len(self.args) < 2 or len(self.args) > 4:
                await self.message.reply(f"Invalid number of arguments. Expected 2 ~ 4, got {len(self.args)}", mention_author=True)
                return
            
            action: str = self.args[0]
            target: str = self.args[1].replace("<", "").replace(">", "").replace("@", "").replace("!", "")
            tagName: str = self.args[2] if len(self.args) >= 3 else None
            tagValue: str = self.args[3] if len(self.args) == 4 else None

            try:
                int(target)
            except:
                await self.message.reply(f"Invalid target user ID: {target}", mention_author=True)
                return
            
            targetUserObject: User = Server.getUserAtServer(self.message.getMessageObject())
            
            messageStr = ""

            if action == "add":
                targetUserObject.addTag(tagName, tagValue)
                messageStr = f"Added tag {tagName} to user {targetUserObject.name}"
                
            elif action == "remove":
                targetUserObject.removeTag(tagName)
                messageStr = f"Removed tag {tagName} from user {targetUserObject.name}"

            elif action == "list":
                tags = targetUserObject.getTags()
                messageStr = f"Tags for user {targetUserObject.name}:\n```"
                for tag in tags:
                    messageStr += f"{tag['id']}: {tag['value']}\n"
                messageStr += "```"
                
            # Update server json
            Server.updateUserAtServer(targetUserObject, self.message)
            
            await self.message.reply(messageStr, mention_author=True)
            
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error while updating user information: {e}", mention_author=True)
            