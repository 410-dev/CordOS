import traceback

import kernel.registry as Registry
import kernel.launchcmd as Launcher
import kernel.journaling as Journaling
import kernel.io as IO


def run(command: str):
    runnablePath = ""
    cmd = ""
    args: list = []

    try:
        Journaling.record("INFO", f"Received command input: {command}")
        args: list = Launcher.splitArguments(command)
        cmd: str = Launcher.getCommand(args)
        runnablePath: str = Launcher.getRunnableModule(args)
        Journaling.record("INFO", f"Command: {cmd}, Runnable: {runnablePath}")
    except Exception as e:
        Journaling.record("ERROR", f"Failed looking up for command. This should not occur. {e}")
        IO.println(f"Failed looking up for command. This should not occur. {e}")

    if runnablePath == "" or runnablePath is None:
        Journaling.record("ERROR", f"Command {cmd} not found.")
        IO.println(f"Command {cmd} not found.")
        return

    try:
        Journaling.record("INFO", f"Executing command '{cmd}' with args {args}.")
        Launcher.launchRunnable(runnablePath, args)
        Journaling.record("INFO", f"Command '{cmd}' executed successfully.")
    except Exception as e:
        Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.NanoPyOS.Kernel.PrintErrors") == "1": IO.println(f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.NanoPyOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error executing command '{cmd}': {e}")
