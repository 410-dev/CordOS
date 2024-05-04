import traceback

import kernel.registry as Registry
import kernel.launchcmd as Launcher
import kernel.journaling as Journaling
import kernel.ipc as IPC
import kernel.io as IO

def main():
    Journaling.record("INFO", "SystemUI Shell Mode started.")
    IO.println("====SystemUI Shell Mode====")

    while not IPC.read("power.off"):
        runnablePath = ""
        cmd = ""
        args: list = []

        try:
            Journaling.record("INFO", "Awaiting command input.")
            msgContent: str = input("> ")
            if msgContent == "":
                continue
            Journaling.record("INFO", f"Received command input: {msgContent}")
            args: list = Launcher.splitArguments(msgContent)
            cmd: str = Launcher.getCommand(args)
            runnablePath: str = Launcher.getRunnableModule(args)
            Journaling.record("INFO", f"Command: {cmd}, Runnable: {runnablePath}")
        except Exception as e:
            Journaling.record("ERROR", f"Failed looking up for command. This should not occur. {e}")
            IO.println(f"Failed looking up for command. This should not occur. {e}")
            continue

        if runnablePath == "" or runnablePath is None:
            Journaling.record("ERROR", f"Command {cmd} not found.")
            IO.println(f"Command {cmd} not found.")
            continue

        try:
            Journaling.record("INFO", f"Executing command '{cmd}' with args {args}.")
            Launcher.launchRunnable(runnablePath, args)
            Journaling.record("INFO", f"Command '{cmd}' executed successfully.")
        except Exception as e:
            Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": IO.println(f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            IO.println(f"Error executing command '{cmd}': {e}")

