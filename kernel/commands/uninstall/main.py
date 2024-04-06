import traceback
import kernel.config as Config
import kernel.registry as Registry
import kernel.servers as Servers

class Uninstall:

    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.config = Config.load()
        self.regPermission = Registry.read("SOFTWARE.CordOS.Security.Install")
        self.user = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)

    async def chkPermission(self, permission):
        if not self.user.hasPermission(permission):
            await self.message.reply(f"You do not have permission to use this command. (Requires {permission})", mention_author=True)
            return False
        return True

    async def exec(self):
        try:
            # Check if user has permission to use this command
            if not await self.chkPermission(self.regPermission): return


            await self.message.reply("This command is not implemented yet.", mention_author=True)

        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error in settings. e: {e}", mention_author=True)

