import os
import threading
import json

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr

class ServicesContainer:
    kernelServices: dict = {
    }

    thirdPartyServices: dict = {
    }

    def addService(scope: str, stage: int, service: dict):
        if scope == "kernel":
            if stage not in ServicesContainer.kernelServices:
                ServicesContainer.kernelServices[stage] = []
            ServicesContainer.kernelServices[stage].append(service)
        else:
            if stage not in ServicesContainer.thirdPartyServices:
                ServicesContainer.thirdPartyServices[stage] = []
            ServicesContainer.thirdPartyServices[stage].append(service)

    def getService(scope: str, id: str):
        toSearch: dict = {}
        if scope == "kernel":
            toSearch = ServicesContainer.kernelServices
        else:
            toSearch = ServicesContainer.thirdPartyServices

        for stage in toSearch:
            for service in toSearch[stage]:
                if service['id'] == id:
                    return service
        return None


def isEnabled(serviceId: str):
    return ServicesContainer.getService("kernel", serviceId) is not None or ServicesContainer.getService("thirdparty", serviceId) is not None


def hasServiceAsRole(role: str) -> str:
    for stage in ServicesContainer.kernelServices:
        for service in ServicesContainer.kernelServices[stage]:
            if service['profile']['role'] == role:
                return service['id']
    for stage in ServicesContainer.thirdPartyServices:
        for service in ServicesContainer.thirdPartyServices[stage]:
            if service['profile']['role'] == role:
                return service['id']
    return None


def start(stage: int, safeMode: bool):
    if Registry.read("SOFTWARE.CordOS.Kernel.Services.Enabled") == "0":
        return

    safeMode = safeMode or Registry.read("SOFTWARE.CordOS.Kernel.SafeMode") == "1"

    if safeMode:
        print("System started with safe mode. Disabling all non-safemode services.")

    print(f"Starting services for stage {stage}")

    servicesList: list = os.listdir("kernel/services")
    safeServiceList: list = Registry.read("SOFTWARE.CordOS.Kernel.Services.SafeModeServices").split(",")
    for idx, line in enumerate(servicesList):
        servicesList[idx] = "kernel/services/" + line

    thirdPartyServicesLoc: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices")
    if os.path.isdir(thirdPartyServicesLoc):
        thirdPartyServicesList: list = os.listdir(thirdPartyServicesLoc)
        for idx, line in enumerate(thirdPartyServicesList):
            thirdPartyServicesList[idx] = thirdPartyServicesLoc + "/" + line
        servicesList.extend(thirdPartyServicesList)

    thirdPartyServiceLoadStage: int = int(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServicesMinimumBootStage", default=3))

    loadedKernelService: list = []
    loadedThirdPartyService: list = []

    for service in servicesList:

        if service.endswith(".disabled"):
            print(f"Service '{service}' is disabled. Skipping.")
            continue

        if safeMode:
            if service not in safeServiceList:
                print(f"Service '{service}' is not in safe mode list. Skipping.")
                continue

        if not os.path.isdir(service):
            continue

        if "main.py" not in os.listdir(service):
            continue

        runSync: bool = False

        serviceData: dict = {}
        try:
            with open(f"{service}/service.json", 'r') as f:
                serviceData = json.loads(f.read())

                # Check if keys exists
                keysRequired = ["sdk", "stage", "sync"]
                keysType = [int, int, bool]
                for i in range(len(keysRequired)):
                    if keysRequired[i] not in serviceData:
                        print(f"Service Failed: Service '{service}' is missing '{keysRequired[i]}' key. (Not Found) Skipping.")
                        continue
                    if not isinstance(serviceData[keysRequired[i]], keysType[i]):
                        print(f"Service Failed: Service '{service}' has invalid '{keysRequired[i]}' key. (Type Mismatch) Skipping.")
                        continue

                if serviceData['stage'] != stage:
                    continue

                # Check if non-kernel service.
                if not service.startswith("kernel/services"):
                    # If current stage did not meet the service's stage, skip.
                    if stage < thirdPartyServiceLoadStage:
                        print(f"Third-party service load is not allowed in stage {stage}. '{service}' is not loadable. Skipping.")
                        continue

                # Check compatibility
                if serviceData['sdk'] < int(Registry.read("SOFTWARE.CordOS.Kernel.Services.SDKMinimum")):
                    print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too old). Skipping.")
                    continue

                if serviceData['sdk'] > int(Registry.read("SOFTWARE.CordOS.Kernel.Services.SDKMaximum")):
                    print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too new). Skipping.")
                    continue

                if "critical.unique." in serviceData['role'] and hasServiceAsRole(serviceData['role']) is not None:
                    print(f"Service Failed: Service '{service}' has the same role as another service, while marked to be unique service. Skipping.")
                    continue

                if serviceData['sync']:
                    runSync = True

                if service.startswith("kernel/services"):
                    if Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service[len("kernel/services"):]}.Enabled") == "0":
                        continue

                    Registry.write(f"SOFTWARE.CordOS.Kernel.Services.{service[len("kernel/services"):]}.Enabled", "1")

                else:
                    serviceName = service.replace(thirdPartyServicesLoc.replace("/", ".").replace("\\", "."), "")
                    if Registry.read(f"SOFTWARE.CordOS.Services.{serviceName}.Enabled") == "0":
                        continue

                    Registry.write(f"SOFTWARE.CordOS.Services.{serviceName}.Enabled", "1")

        except:
            pass

        try:
            import importlib
            service = service.replace("/", ".").replace("\\", ".")
            moduleName = f"{service}.main"
            print(f"Starting service (Stage {stage}) '{service}'.")
            module = importlib.import_module(moduleName)

            if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                if not Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service}.ReloadOnCall") == "0":
                    importlib.reload(module)

            thread = threading.Thread(target=module.main)
            thread.daemon = True

            if runSync:
                print(f"Running service (Stage {stage}) '{service}' in sync mode.")
                thread.run()
                continue

            thread.start()

            serviceObject: dict = {
                "id": serviceData['id'],
                "name": serviceData['name'],
                "module": module,
                "thread": thread,
                "profile": serviceData
            }

            ServicesContainer.addService("kernel" if service.startswith("kernel.services") else "thirdparty", stage, serviceObject)

            print(f"Started service (Stage {stage}) '{service}'.")

            if service.startswith("kernel.services"):
                loadedKernelService.append(service.replace("kernel.services.", ""))
            else:
                loadedThirdPartyService.append(service.replace(thirdPartyServicesLoc.replace("/", ".").replace("\\", ".") + ".", ""))

        except Exception as e:
            print(f"Error in starting service '{service}' e: {e}")
            pass

    if not os.path.exists(PartitionMgr.cache() + "/krnlsrv"):
        os.makedirs(PartitionMgr.cache() + "/krnlsrv")
    with open(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_kernel", 'w') as f:
        f.write("\n".join(loadedKernelService))
    with open(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_thirdparty", 'w') as f:
        f.write("\n".join(loadedThirdPartyService))
