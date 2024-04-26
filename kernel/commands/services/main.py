import traceback
import os

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr
import kernel.io as IO

def main(args: list):

    # Check if args are present
    if len(args) < 2:
        IO.println(f"Missing arguments. \nUsage: services <configure|list> [service] args...")
        return

    # Check if command is configure
    if args[1] == "configure":
        if len(args) < 3:
            IO.println("Usage: services configure <service> args...")
            return

        try:
            import importlib
            userServiceLocation = Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices").replace("/", ".").replace("\\", ".")
            moduleName = f"{userServiceLocation}.{args[2]}.configure"
            if os.path.isfile(moduleName.replace(".", "/") + ".py"):
                with open(moduleName.replace(".", "/") + ".py", 'r') as f:
                    if "def main(" not in f.read():
                        IO.println(f"User service '{args[2]}' does not have a configure function in configure module.")
                        return

            module = importlib.import_module(moduleName)

            if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                importlib.reload(module)

            module.main(args[3:])

        except ModuleNotFoundError:
            try:
                import importlib
                moduleName = f"kernel.services.{args[2]}.configure"
                if os.path.isfile(moduleName.replace(".", "/") + ".py"):
                    with open(moduleName.replace(".", "/") + ".py", 'r') as f:
                        if "def main(" not in f.read():
                            IO.println(f"Kernel service '{args[2]}' does not have a configure function in configure module.")
                            return
                module = importlib.import_module(moduleName)

                if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                    importlib.reload(module)

                module.main(args[3:])

            except ModuleNotFoundError:
                IO.println(f"Service '{args[2]}' not found.")
                return

            except Exception as e:
                IO.println(f"Error in configuring service '{args[2]}' e: {e}")
                traceback.print_exc()
                pass

        except Exception as e:
            IO.println(f"Error in configuring service '{args[1]}' e: {e}")
            traceback.print_exc()
            pass
        return
    elif args[1] == "list":
        kernelServices: list = os.listdir("kernel/services")
        userServices: list = []
        if os.path.isdir(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices")):
            userServices: list = os.listdir(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices"))
        services = "Kernel Services:\n"
        for service in kernelServices:
            try:
                if "main.py" not in os.listdir(f"kernel/services/{service}"):
                    continue
            except:
                continue
            services += f"{service}\n"

        services += "\nUser Services:\n"
        for service in userServices:
            try:
                if "main.py" not in os.listdir(f"{Registry.read('SOFTWARE.CordOS.Kernel.Services.OtherServices')}/{service}"):
                    continue
            except:
                continue
            services += f"{service}\n"
        IO.println(f"{services}")
    elif args[1] == "loaded":
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

        IO.println(f"{response}")

    else:
        IO.println(f"Unknown action: {args[0]}\nUsage: services <configure|list> [service] args...")
        return
    return
