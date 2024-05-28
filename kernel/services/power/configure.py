import signal
import sys
import os
import kernel.ipc as IPC
import kernel.registry as Registry
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


async def mainAsync(args: list, message):

    if len(args) < 1:
        await message.reply("Usage: power off")
        return

    if args[0] == "off":
        IPC.set("power.off", True)
        IPC.set("power.off.state", "OFF")
        terminationSteps()
        await message.reply(f"Shutdown signal published. System will shutdown after all services have stopped.")

    elif args[0] == "reboot":
        IPC.set("power.off", True)
        IPC.set("power.off.state", "REBOOT")
        terminationSteps()
        await message.reply(f"Reboot signal published. System will reboot after all services have stopped.")

    elif args[0] == "halt":
        haltKey = f"KernelHaltSignal.{message.author.id}"
        haltValue = IPC.read(haltKey, default="0")
        if haltValue != "1" and (len(args) < 2 or args[1] != "--no-warning"):
            IPC.set(haltKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system force halt. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power halt-cancel`.")

        else:
            terminationSteps()
            await message.reply(f"System will now be force terminated. Goodbye.")
            IPC.set("power.off", True)
            IPC.set("power.off.state", "OFF")
            if Host.isPOSIX():
                os.kill(os.getpid(), signal.SIGINT)
            else:
                pid = os.getpid()
                Host.executeCommand("taskkill /F /PID " + str(pid))

    elif args[0] == "reset":
        resetKey = f"KernelResetSignal.{message.author.id}"
        resetValue = IPC.read(resetKey)
        if resetValue != "1" and (len(args) < 2 or args[1] != "--no-warning"):
            IPC.set(resetKey, "1")
            await message.reply(f"!!!!! EXTREME SENSITIVE WARNING !!!!!\nYou have triggered system reset. ***This will stop the system immediately and may cause data loss***. If you are sure, type the trigger command again. If you are not sure, type `power off` to shutdown the system. To cancel the confirmation, type `power reset-cancel`.")

        else:
            terminationSteps()
            await message.reply(f"System will now be reset.")
            IPC.set("power.off", True)
            IPC.set("power.off.state", "REBOOT")
            with open("restart", "w") as f:
                f.write("reboot")
            if Host.isPOSIX():
                os.kill(os.getpid(), signal.SIGINT)
            else:
                pid = os.getpid()
                Host.executeCommand("taskkill /F /PID " + str(pid))

    elif args[0] == "halt-cancel":
        haltKey = f"KernelHaltSignal.{message.author.id}"
        IPC.delete(haltKey)
        await message.reply("Force-halt cancelled.")

    elif args[0] == "reset-cancel":
        resetKey = f"KernelResetSignal.{message.author.id}"
        IPC.delete(resetKey)
        await message.reply("Reset cancelled.")

    else:
        await message.reply("Usage: power off")
        return


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
