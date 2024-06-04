import kernel.registry as Registry
import kernel.ipc as IPC
import kernel.services.DiscordUIService.webhook as Webhook
import kernel.io as IO

import threading

def main():
    
    enabled = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled")
    if enabled == "0":
        return

    try:
        def loop():
            
            # Update enabled
            enabled = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled")
            regPath = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.RegistrationPath")

            if enabled == "0":
                return

            # If enabled, call webhook
            webhookList: list = Webhook.list()
            for webhookModule in webhookList:
                try:
                    if Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.EnableLogging") == "1":
                        IO.println(f"Running webhook '{webhookModule}'")
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

                    if Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.EnableLogging") == "1":
                        IO.println(f"Webhook '{webhookModule}' launch successfully.")

                except Exception as e:
                    IO.println(f"Error in running webhook '{webhookModule}'. e: {e}")
                    pass

        IPC.repeatUntilShutdown(int(Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.Interval")), loop)
        IO.println("Webhook service stopped.")
    except Exception as e:
        IO.println(f"Error in starting / running service. e: {e}")
        pass
