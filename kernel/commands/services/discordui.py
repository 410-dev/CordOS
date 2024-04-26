import traceback
import os

import kernel.config as Config
import kernel.registry as Registry
import kernel.servers as Servers
import kernel.partitionmgr as PartitionMgr

class Services:

    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
        self.config = Config.load()
        self.permission = Registry.read("SOFTWARE.CordOS.Security.Services")
        self.user = Servers.getUserAtServer(self.message.guild.id, self.message.author.id)

    async def chkPermission(self, permission):
        if self.user.hasPermission(permission) == False:
            await self.message.reply(f"You do not have permission to use this command. (Requires {permission})",
                                     mention_author=True)
            return False
        return True

    async def mainAsync(self):

        # Check access permission
        if await self.chkPermission(self.permission) == False:
            return

        # Check if args are present
        if len(self.args) < 2:
            await self.message.reply(f"Missing arguments. \nUsage: services <configure|list> [service] args...",
                                     mention_author=True)
            return

        # Check if command is configure
        if self.args[1] == "configure":
            if len(self.args) < 3:
                await self.message.reply("Usage: services configure <service> args...", mention_author=True)
                return

            try:
                import importlib
                userServiceLocation = Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices").replace("/",
                                                                                                             ".").replace(
                    "\\", ".")
                moduleName = f"{userServiceLocation}.{self.args[2]}.configure"
                if os.path.isfile(moduleName.replace(".", "/") + ".py"):
                    with open(moduleName.replace(".", "/") + ".py", 'r') as f:
                        if "async def mainAsync(" not in f.read():
                            self.message.reply(
                                f"User service '{self.args[2]}' does not have a configure function in configure module.",
                                mention_author=True)
                            return
                module = importlib.import_module(moduleName)

                if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                    importlib.reload(module)

                await module.mainAsync(self.args[3:], self.message)

            except ModuleNotFoundError:
                try:
                    import importlib
                    moduleName = f"kernel.services.{self.args[2]}.configure"
                    if os.path.isfile(moduleName.replace(".", "/") + ".py"):
                        with open(moduleName.replace(".", "/") + ".py", 'r') as f:
                            if "async def mainAsync(" not in f.read():
                                self.message.reply(
                                    f"Kernel service '{self.args[2]}' does not have a configure function in configure module.",
                                    mention_author=True)
                                return
                    module = importlib.import_module(moduleName)

                    if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                        importlib.reload(module)

                    await module.mainAsync(self.args[3:], self.message)

                except ModuleNotFoundError:
                    await self.message.reply(f"Service '{self.args[2]}' not found.", mention_author=True)
                    return

                except Exception as e:
                    await self.message.reply(f"Error in configuring service '{self.args[2]}' e: {e}",
                                             mention_author=True)
                    traceback.print_exc()
                    pass

            except Exception as e:
                await self.message.reply(f"Error in configuring service '{self.args[1]}' e: {e}", mention_author=True)
                traceback.print_exc()
                pass
            return
        elif self.args[1] == "list":
            kernelServices: list = os.listdir("kernel/services")
            userServices: list = []
            if os.path.isdir(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices")):
                userServices: list = os.listdir(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices"))
            services = "Kernel Services:\n```"
            for service in kernelServices:
                try:
                    if "main.py" not in os.listdir(f"kernel/services/{service}"):
                        continue
                except:
                    continue
                services += f"{service}\n"

            services += "```\nUser Services:\n```"
            for service in userServices:
                try:
                    if "main.py" not in os.listdir(
                            f"{Registry.read('SOFTWARE.CordOS.Kernel.Services.OtherServices')}/{service}"):
                        continue
                except:
                    continue
                services += f"{service}\n"
            await self.message.reply(f"{services} ```", mention_author=True)
        elif self.args[1] == "loaded":
            flist = os.listdir(PartitionMgr.cache() + "/krnlsrv")
            flist.sort()
            loadedKernelService = {}
            loadedThirdPartyService = {}
            for file in flist:
                if file.startswith("stg"):
                    stageNum = file.split("_")[0][len("stg"):]
                    scope = file.split("_")[2]
                    with open(PartitionMgr.cache() + "/krnlsrv/" + file, 'r') as f:
                        data = f.read().split("\n")
                        if scope == "kernel":
                            loadedKernelService[stageNum] = data
                        elif scope == "thirdparty":
                            loadedThirdPartyService[stageNum] = data

            response = ""
            for stage in loadedKernelService:
                response += f"Stage {stage} Kernel Services: {', '.join(loadedKernelService[stage])}\n"
            response += "\n"
            for stage in loadedThirdPartyService:
                response += f"Stage {stage} Third Party Services: {', '.join(loadedThirdPartyService[stage])}\n"

            await self.message.reply(f"```{response}```", mention_author=True)

        else:
            await self.message.reply(
                f"Unknown action: {self.args[0]}\nUsage: services <configure|list> [service] args...",
                mention_author=True)
            return
        return
