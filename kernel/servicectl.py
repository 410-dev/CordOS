import os
import threading
import json

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr
import kernel.journaling as Journaling

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
        Journaling.record("INFO", "Service manager is disabled. Skipping service start.")
        return

    safeMode = safeMode or Registry.read("SOFTWARE.CordOS.Kernel.SafeMode") == "1"

    if safeMode:
        Journaling.record("INFO", "System started with safe mode. Disabling all non-safemode services.")
        print("System started with safe mode. Disabling all non-safemode services.")

    Journaling.record("INFO", f"Starting services for stage {stage}")
    print(f"Starting services for stage {stage}")

    servicesList: list = os.listdir("kernel/services")
    for idx, line in enumerate(servicesList):
        servicesList[idx] = "kernel/services/" + line

    thirdPartyServicesLoc: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices")
    if os.path.isdir(thirdPartyServicesLoc):
        thirdPartyServicesList: list = os.listdir(thirdPartyServicesLoc)
        for idx, line in enumerate(thirdPartyServicesList):
            thirdPartyServicesList[idx] = thirdPartyServicesLoc + "/" + line
        servicesList.extend(thirdPartyServicesList)

    thirdPartyServiceLoadStage: int = int(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServicesMinimumBootStage", default=3))
    Journaling.record("INFO", f"Third-party service load stage: {thirdPartyServiceLoadStage}")

    if not os.path.exists(PartitionMgr.cache() + "/krnlsrv"):
        os.makedirs(PartitionMgr.cache() + "/krnlsrv")

    for service in servicesList:
        launchsvc(service, safeMode, stage)



def launchsvc(service: str, safeMode: bool, stage: int) -> bool:
    thirdPartyServicesLoc: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServices")
    thirdPartyServiceLoadStage: int = int(Registry.read("SOFTWARE.CordOS.Kernel.Services.OtherServicesMinimumBootStage", default=3))
    safeServiceList: list = Registry.read("SOFTWARE.CordOS.Kernel.Services.SafeModeServices").split(",")

    if service.endswith(".disabled"):
        Journaling.record("INFO", f"Service '{service}' is disabled. Skipping.")
        print(f"Service '{service}' is disabled. Skipping.")
        return False

    if safeMode:
        if service not in safeServiceList:
            Journaling.record("INFO", f"Service '{service}' is not in safe mode list. Skipping.")
            print(f"Service '{service}' is not in safe mode list. Skipping.")
            return False

    if not os.path.isdir(service):
        Journaling.record("INFO", f"Service '{service}' is not a directory. Skipping.")
        return False

    if "main.py" not in os.listdir(service):
        Journaling.record("INFO", f"Service '{service}' does not have main.py. Skipping.")
        return False

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
                    Journaling.record("ERROR",
                                      f"Service '{service}' is missing '{keysRequired[i]}' key. (Not Found) Skipping.")
                    print(
                        f"Service Failed: Service '{service}' is missing '{keysRequired[i]}' key. (Not Found) Skipping.")
                    continue
                if not isinstance(serviceData[keysRequired[i]], keysType[i]):
                    Journaling.record("ERROR",
                                      f"Service '{service}' has invalid '{keysRequired[i]}' key. (Type Mismatch) Skipping.")
                    print(
                        f"Service Failed: Service '{service}' has invalid '{keysRequired[i]}' key. (Type Mismatch) Skipping.")
                    continue

            if serviceData['stage'] != stage and stage != -1:
                return False

            # Check if non-kernel service.
            if not service.startswith("kernel/services"):
                # If current stage did not meet the service's stage, skip.
                if stage < thirdPartyServiceLoadStage and stage != -1:
                    Journaling.record("INFO", f"Third-party service load is not allowed in stage {stage}. '{service}' is not loadable. Skipping.")
                    print(f"Third-party service load is not allowed in stage {stage}. '{service}' is not loadable. Skipping.")
                    return False

            # Check compatibility
            if serviceData['sdk'] < int(Registry.read("SOFTWARE.CordOS.Kernel.Services.SDKMinimum")):
                Journaling.record("ERROR",
                                  f"Service '{service}' is not compatible with this version of CordOS (Too old). Skipping.")
                print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too old). Skipping.")
                return False

            if serviceData['sdk'] > int(Registry.read("SOFTWARE.CordOS.Kernel.Services.SDKMaximum")):
                Journaling.record("ERROR",
                                  f"Service '{service}' is not compatible with this version of CordOS (Too new). Skipping.")
                print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too new). Skipping.")
                return False

            if "critical.unique." in serviceData['role'] and hasServiceAsRole(serviceData['role']) is not None:
                allowedUniqueUnuniques = Registry.read("SOFTWARE.CordOS.Kernel.Services.AllowedMultipleUniqueRoles",
                                                       default="").split(",")
                if serviceData['role'] not in allowedUniqueUnuniques and not serviceData[
                                                                                 'id'] in allowedUniqueUnuniques:
                    Journaling.record("ERROR", f"Service '{service}' has the same role as another service, while marked to be unique service. Skipping.")
                    print(f"Service Failed: Service '{service}' has the same role as another service, while marked to be unique service. Skipping.")
                    return False
                else:
                    Journaling.record("INFO", f"Service '{service}' has the same role as another service, but allowed to be loaded.")

            if serviceData['sync']:
                Journaling.record("INFO", f"Service '{service}' is configured to run in sync mode.")
                runSync = True

            if service.startswith("kernel/services"):
                if Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service[len("kernel/services"):]}.Enabled") == "0":
                    Journaling.record("INFO", f"Service '{service}' is disabled. Skipping.")
                    return False

                Registry.write(f"SOFTWARE.CordOS.Kernel.Services.{service[len("kernel/services"):]}.Enabled", "1")

            else:
                serviceName = service.replace(thirdPartyServicesLoc.replace("/", ".").replace("\\", "."), "")
                if Registry.read(f"SOFTWARE.CordOS.Services.{serviceName}.Enabled") == "0":
                    Journaling.record("INFO", f"Service '{service}' is disabled. Skipping.")
                    return False

                Registry.write(f"SOFTWARE.CordOS.Services.{serviceName}.Enabled", "1")

    except:
        pass

    try:
        import importlib
        service = service.replace("/", ".").replace("\\", ".")
        moduleName = f"{service}.main"
        Journaling.record("INFO", f"Starting service (Stage {stage}) '{service}'.")
        print(f"Starting service (Stage {stage}) '{service}'.")
        module = importlib.import_module(moduleName)

        if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
            if not Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service}.ReloadOnCall") == "0":
                Journaling.record("INFO", f"Reloading service '{service}'...")
                importlib.reload(module)

        thread = threading.Thread(target=module.main)
        thread.daemon = True

        if runSync:
            Journaling.record("INFO", f"Running service (Stage {stage}) '{service}' in sync mode.")
            print(f"Running service (Stage {stage}) '{service}' in sync mode.")
            thread.run()
            return False

        Journaling.record("INFO", f"Starting service (Stage {stage}) '{service}'.")
        thread.start()

        serviceObject: dict = {
            "id": serviceData['id'],
            "name": serviceData['name'],
            "module": module,
            "thread": thread,
            "profile": serviceData
        }

        Journaling.record("INFO", f"Registering service (Stage {stage}) '{service}'.")
        ServicesContainer.addService("kernel" if service.startswith("kernel.services") else "thirdparty", stage,
                                     serviceObject)

        Journaling.record("INFO", f"Started service (Stage {stage}) '{service}'.")
        print(f"Started service (Stage {stage}) '{service}'.")

        if service.startswith("kernel.services"):
            if os.path.exists(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_kernel"):
                mode = 'a'
            else:
                mode = 'w'

            with open(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_kernel", mode) as f:
                f.write(service.replace("kernel.services.", "") + "\n")

        else:
            if os.path.exists(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_thirdparty"):
                mode = 'a'
            else:
                mode = 'w'

            with open(PartitionMgr.cache() + f"/krnlsrv/stg{stage}_loaded_thirdparty", mode) as f:
                f.write(service.replace(thirdPartyServicesLoc.replace("/", ".").replace("\\", ".") + ".", "") + "\n")

        return True
    except Exception as e:
        print(f"Error in starting service '{service}' e: {e}")
        pass
