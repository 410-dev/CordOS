import traceback

import kernel.registry as Registry
import kernel.launchcmd as Launcher
import kernel.servicectl as ServiceCtl
import kernel.ipc as IPC
import kernel.io as IO

def main():
    IO.println("====SystemUI Shell Mode====")

    while not IPC.read("power.off"):
        runnablePath = ""
        cmd = ""
        args: list = []

        try:
            msgContent: str = input("> ")
            if msgContent == "":
                continue
            args: list = Launcher.splitArguments(msgContent)
            cmd: str = Launcher.getCommand(args)
            runnablePath: str = Launcher.getRunnableModule(args)
        except Exception as e:
            IO.println(f"Failed looking up for command. This should not occur. {e}")
            continue

        if runnablePath == "" or runnablePath is None:
            IO.println(f"Command {cmd} not found.")
            continue

        try:
            Launcher.launchRunnable(runnablePath, args)
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": IO.println(f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            IO.println(f"Error executing command '{cmd}': {e}")

