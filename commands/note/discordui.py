import kernel.registry as Registry
import kernel.servers as Servers


class Note:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.SVNOTEREG = "SOFTWARE.CordOS.Plugins.Note.$server."
        self.USRNOTEREG = "SOFTWARE.CordOS.Plugins.Note.$server.$user."
    
    async def mainAsync(self):
        
        action: str = ""
        targreg: str = ""
        
        content: str = ""
        title: str = ""
        
        user = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)
        
        if user.hasTag("banned"): 
            await self.message.reply("You are banned from using this command.", mention_author=True)
            return
        
        if "-l" in self.args:
            # List notes
            targreg = self.SVNOTEREG.replace("$server", str(self.message.guild.id))
            action = "list"
            
            if "-u" in self.args:
                # List user notes
                targreg = self.USRNOTEREG.replace("$server", str(self.message.guild.id)).replace("$user", str(self.message.author.id))

        elif "-d" in self.args:
            # Delete note
            title = self.args[-1]
            targreg = self.SVNOTEREG.replace("$server", str(self.message.guild.id)) + title
            action = "delete"
            
            if "-u" in self.args:
                # Delete user note
                targreg = self.USRNOTEREG.replace("$server", str(self.message.guild.id)).replace("$user", str(self.message.author.id)) + title
        
        elif "-u" in self.args:
            
            if len(self.args) < 2:
                # Read user note
                title = self.args[-1]
                targreg = self.USRNOTEREG.replace("$server", str(self.message.guild.id)).replace("$user", str(self.message.author.id)) + title
                action = "list"
                
            else:
                # Add user note
                content: str = self.args[-1]
                title: str = self.args[-2]
                targreg = self.USRNOTEREG.replace("$server", str(self.message.guild.id)).replace("$user", str(self.message.author.id)) + title
                action = "add"
        
        else:
            
            if len(self.args) < 2:
                # Read note
                title = self.args[-1]
                targreg = self.SVNOTEREG.replace("$server", str(self.message.guild.id)) + title
                action = "list"
                
            else:
                # Add note
                content: str = self.args[-1]
                title: str = self.args[-2]
                targreg = self.SVNOTEREG.replace("$server", str(self.message.guild.id)) + title
                action = "add"
            
        
        if action == "add":
            result: str = Registry.read(targreg)
            if result == None or result == "" or "-o" in self.args:
                Registry.write(targreg, content)
                await self.message.reply("Note added.", mention_author=True)
            else:
                await self.message.reply("Note already exists. Use -o to overwrite.", mention_author=True)                
        
        elif action == "list":
            result: str = Registry.read(targreg)
            if result == None or result == "":
                await self.message.reply("No notes found.", mention_author=True)
            else:
                outstr: str = ""
                if type(result) == list:
                    for i in result:
                        if i.find("=") != -1:
                            outstr += f"{i}\n"
                            
                else:
                    outstr = result
                await self.message.reply(f"Notes:\n{outstr}", mention_author=True)
        
        elif action == "delete":
            try:
                result: str = Registry.read(targreg)
                if result == None or result == "":
                    await self.message.reply(f"No notes found.", mention_author=True)
                else:
                    Registry.delete(targreg)
                    await self.message.reply("Note deleted.", mention_author=True)
                
            except:
                await self.message.reply(f"Action incompleted due to error. Perhaps you tried to delete a registry key?", mention_author=True)
                
        else:
            await self.message.reply(f"Unknown action: {action}", mention_author=True)

    