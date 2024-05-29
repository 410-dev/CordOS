import signal
import os
import kernel.ipc as IPC
import kernel.io as IO
import kernel.host as Host

import kernel.services.SystemUI.execute as Launcher


def terminationSteps():
    try:
        id = IPC.read("remotesystemui.publisher.id")
        pw = IPC.read("remotesystemui.publisher.auth")
        if id is not None and pw is not None:
            IO.println("Shutting down remote SystemUI.")
            Launcher.run(f"remoteconnect {id}@localhost NPYOSAUTH_1.0:{id}:login.remote:password:{pw}:login")
            Launcher.run(f"remoteconnect {id}@localhost NPYOSAUTH_1.0:{id}:login.remote:password:{pw}:terminate")
        else:
            IO.println("Remote SystemUI not found. Skipping shutdown.")
    except Exception as e:
        pass


def main(args: list):

    if len(args) < 1:
        IO.println("Usage: power <off|reboot|halt|reset>")
        return

    if args[0] == "off":
        terminationSteps()
        IPC.set("power.off", True)
        IPC.set("power.off.state", "OFF")
        IO.println(f"Shutdown signal published. System will shutdown after all services have stopped.")

    elif args[0] == "reboot":
        terminationSteps()
        IPC.set("power.off", True)
        IPC.set("power.off.state", "REBOOT")
        IO.println(f"Reboot signal published. System will reboot after all services have stopped.")

    elif args[0] == "reboot-safe":
        terminationSteps()
        IPC.set("power.off", True)
        IPC.set("power.off.state", "REBOOT-SAFE")
        IO.println(f"Reboot signal published. System will reboot after all services have stopped.")

    elif args[0] == "halt":
        terminationSteps()
        IO.println(f"System will now be force terminated. Goodbye.")
        IPC.set("power.off", True)
        IPC.set("power.off.state", "OFF")
        if Host.isPOSIX():
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            pid = os.getpid()
            Host.executeCommand("taskkill /F /PID " + str(pid))

    elif args[0] == "reset":
        terminationSteps()
        IO.println(f"System will now be reset.")
        IPC.set("power.off", True)
        IPC.set("power.off.state", "REBOOT")
        with open("restart", "w") as f:
            f.write("reboot")
        if Host.isPOSIX():
            os.kill(os.getpid(), signal.SIGTERM)
        else:
            pid = os.getpid()
            Host.executeCommand("taskkill /F /PID " + str(pid))

    else:
        IO.println("Usage: power <off|reboot|halt|reset>")
        return


def off():
    main(["off"])


def reboot():
    main(["reboot"])


def reboot_safe():
    main(["reboot-safe"])


def halt():
    main(["halt"])


def reset():
    main(["reset"])
