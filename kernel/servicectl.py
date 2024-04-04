import os
import threading
import json

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr

def start(stage: int):
    if Registry.read("SOFTWARE.CordOS.Kernel.Services.Enabled") == "0":
        return

    print(f"Starting services for stage {stage}")

    servicesList: list = os.listdir("kernel/services")

    for service in servicesList:

        if "main.py" not in os.listdir(f"kernel/services/{service}"):
            continue

        try:
            with open(f"kernel/services/{service}/service.json", 'r') as f:
                serviceData = json.loads(f.read())
                if serviceData['stage'] != stage:
                    continue

                # Check compatibility
                if serviceData['api'] < int(Registry.read("SOFTWARE.CordOS.Kernel.Services.APIMinimum")):
                    print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too old). Skipping.")
                    continue
                if serviceData['api'] > int(Registry.read("SOFTWARE.CordOS.Kernel.Services.APIMaximum")):
                    print(f"Service Failed: Service '{service}' is not compatible with this version of CordOS (Too new). Skipping.")
                    continue

                if Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service}.Enabled") == "0":
                    continue

                Registry.write(f"SOFTWARE.CordOS.Kernel.Services.{service}.Enabled", "1")
        except:
            pass

        try:
            import importlib
            moduleName = f"kernel.services.{service}.main"
            print(f"Starting service (Stage {stage}) '{service}'.")
            module = importlib.import_module(moduleName)

            if Registry.read("SOFTWARE.CordOS.Kernel.Services.ReloadOnCall") == "1":
                if not Registry.read(f"SOFTWARE.CordOS.Kernel.Services.{service}.ReloadOnCall") == "0":
                    importlib.reload(module)

            thread = threading.Thread(target=module.main)
            thread.daemon = True
            thread.start()

            print(f"Started service (Stage {stage}) '{service}'.")

        except Exception as e:
            print(f"Error in starting service '{service}' e: {e}")
            pass

def markStopped(service: str):
    cache: str = PartitionMgr.cache()
    cache = os.path.join(cache, "krnlsrv", "services")
    os.makedirs(cache, exist_ok=True)
    with open(os.path.join(cache, service), "w") as f:
        f.write("0")