import traceback

import kernel.registry as Registry
import kernel.launchcmd as Launcher
import kernel.servicectl as ServiceCtl
import kernel.ipc as IPC

def main():
    while not IPC.read("kernel.off"):
        runnablePath = ""
        cmd = ""
        args: list = []

        try:
            msgContent: str = input("> ")
            args: list = Launcher.splitArguments(msgContent)
            cmd: str = Launcher.getCommand(args)
            runnablePath: str = Launcher.getRunnableModule(args)
        except Exception as e:
            print(f"Failed looking up for command. This should not occur. {e}")

        if runnablePath == "" or runnablePath is None:
            print(f"Command {cmd} not found.")

        try:
            Launcher.launchRunnable(runnablePath, args)
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            print(f"Error executing command '{cmd}': {e}")
