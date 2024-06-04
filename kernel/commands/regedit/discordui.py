import traceback
import kernel.config as Config
import kernel.registry as Registry
import kernel.services.DiscordUIService.servers as Servers

class Regedit:

    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.config = Config.load()
        self.regPermission = Registry.read("SOFTWARE.CordOS.Security.Registry")
        self.user = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)

    async def chkPermission(self, permission):
        if not self.user.hasPermission(permission):
            await self.message.reply(f"You do not have permission to use this command. (Requires {permission})",
                                     mention_author=True)
            return False
        return True

    async def mainAsync(self):

        try:

            # Remove first index of args if the length is greater than 0
            if len(self.args) > 0:
                self.args.pop(0)

            # Check if user has permission to use this command
            if not await self.chkPermission(self.regPermission): return

            # Replace key variables
            key = ""
            if len(self.args) == 1 or len(self.args) == 2:
                key = self.args[0].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))

            # Check number of arguments
            if len(self.args) == 2:
                if self.args[0] == "-d":
                    key = self.args[1].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))
                    var = Registry.read(key)
                    if var == None:
                        await self.message.reply(f"Registry key `{key}` does not exist.", mention_author=True)
                    else:
                        val = self.args[1].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))
                        Registry.delete(key)
                        await self.message.reply(f"Registry `{key}` erased.", mention_author=True)
                elif self.args[0] == "-df":
                    key = self.args[1].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))
                    var = Registry.read(key)
                    if var == None:
                        await self.message.reply(f"Registry key `{key}` does not exist.", mention_author=True)
                    else:
                        val = self.args[1].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))
                        Registry.delete(key, deleteSubkeys=True)
                        await self.message.reply(f"Registry `{key}` erased.", mention_author=True)
                else:
                    var = Registry.read(key)
                    val = self.args[1].replace("$user", str(self.message.author.id)).replace("$server", str(self.message.guild.id))
                    Registry.write(key, val)
                    await self.message.reply(f"Registry Updated\n`{key}` = `{var}` -> `{val}`", mention_author=True)

            elif len(self.args) == 1:
                regType = Registry.isKey(key)
                if regType == 2:
                    await self.message.reply(f"Registry value `{key}` is `{Registry.read(key)}`", mention_author=True)
                elif regType == 1:
                    l = Registry.read(key)
                    for i in range(len(l)):
                        if l[i].find("=") != -1:
                            l[i] = "[Val] " + l[i].replace("=", ": ")
                        else:
                            l[i] = "[Key] " + l[i]
                    l = "\n".join(l)
                    await self.message.reply(f"Registry key `{key}` contains:\n\n```{l}```", mention_author=True)
                else:
                    await self.message.reply(f"Registry key does not exist.", mention_author=True)

            else:
                await self.message.reply(f"Invalid number of arguments. Expected 1 or 2, got {len(self.args)}", mention_author=True)

        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await self.message.reply(f"Error in settings. e: {e}", mention_author=True)
