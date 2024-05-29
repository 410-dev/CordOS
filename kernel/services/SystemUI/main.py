import traceback

import kernel.registry as Registry
import kernel.services.SystemUI.execute as Launcher
import kernel.journaling as Journaling
import kernel.ipc as IPC
import kernel.io as IO

def main():
    Journaling.record("INFO", "SystemUI Shell Mode started.")
    IO.println("====SystemUI Shell Mode====")

    while not IPC.read("power.off"):
        cmd = ""
        try:
            Journaling.record("INFO", "Awaiting command input.")
            msgContent: str = input("> ")
            if msgContent == "":
                continue
            Launcher.run(msgContent)
        except Exception as e:
            Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.NanoPyOS.Kernel.PrintErrors") == "1": IO.println(f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.NanoPyOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            IO.println(f"Error executing command '{cmd}': {e}")

