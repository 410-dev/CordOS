import traceback
import os

import kernel.config as Config
import kernel.registry as Registry
import kernel.servers as Servers

class Services:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.config = Config.load()
        self.permission = Registry.read("SOFTWARE.CordOS.Security.Services")
        self.user = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)

    async def chkPermission(self, permission):
        if self.user.hasPermission(permission) == False:
            await self.message.reply(f"You do not have permission to use this command. (Requires {permission})", mention_author=True)
            return False
        return True
    
    async def exec(self):

        # Check access permission
        if await self.chkPermission(self.permission) == False:
            return
        
        # Check if args are present
        if len(self.args) < 2:
            await self.message.reply(f"Missing arguments. \nUsage: services <configure|list> [service] args...", mention_author=True)
            return
        
        # Check if command is configure
        if self.args[1] == "configure":
            if len(self.args) < 3:
                await self.message.reply("Usage: services configure <service> args...", mention_author=True)
                return

            try:
                import importlib
                moduleName = f"kernel.services.{self.args[2]}.configure"
                module = importlib.import_module(moduleName)

                if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                    importlib.reload(module)

                await module.main(self.args[3:], self.message)
            except ModuleNotFoundError:
                await self.message.reply(f"Service '{self.args[2]}' not found.", mention_author=True)
                return

            except Exception as e:
                await self.message.reply(f"Error in configuring service '{self.args[1]}' e: {e}", mention_author=True)
                traceback.print_exc()
                pass
            return
        elif self.args[1] == "list":
            servicesList: list = os.listdir("kernel/services")
            services = ""
            for service in servicesList:
                try:
                    if "main.py" not in os.listdir(f"kernel/services/{service}"):
                        continue
                except:
                    continue
                services += f"{service}\n"
            await self.message.reply(f"Services:\n{services}", mention_author=True)
        else:
            await self.message.reply(f"Unknown action: {self.args[0]}\nUsage: services <configure|list> [service] args...", mention_author=True)
            return
        return