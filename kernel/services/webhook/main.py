import kernel.registry as Registry
import kernel.ipc as IPC
import kernel.webhook as Webhook

import os
import time
import threading

def main():
    
    enabled = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled")
    if enabled == "0":
        return

    ipcState = ""

    try:
        while (enabled == "1" and ipcState != Registry.read("SOFTWARE.CordOS.Kernel.Signals.Shutdown")):
            
            # Update enabled
            enabled = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled")
            ipcState = IPC.read(Registry.read("SOFTWARE.CordOS.Kernel.Services.CoreServices.IPC.LabelKernelState"))

            regPath = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.RegistrationPath")

            # If enabled, call webhook
            webhookList: list = Webhook.list()
            for webhookModule in webhookList:
                try:
                    import importlib
                    moduleName = f"{regPath.replace('/', '.')}.{webhookModule}"
                    module = importlib.import_module(moduleName)

                    if Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.ReloadOnCall") == "1":
                        importlib.reload(module)

                    libraryPath = Webhook.getLibrary(webhookModule)

                    # Pass libraryPath as argument
                    thread = threading.Thread(target=module.main, args=(libraryPath,))
                    thread.daemon = True
                    thread.start()

                except Exception as e:
                    print(f"Error in running webhook '{webhookModule}'. e: {e}")
                    pass

            # Sleep
            time.sleep(int(Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.TimeSync")))
    except Exception as e:
        print(f"Error in starting / running service. e: {e}")
        pass