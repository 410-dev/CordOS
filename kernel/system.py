import sys
import traceback
import time
import threading

import kernel.registry as Registry
import kernel.servicectl as Services
import kernel.clock as Clock
import kernel.ipc as IPC
import kernel.journaling as Journaling

def main(argsList: list) -> int:
    try:

        # Check commandline arguments
        Clock.init()
        safeMode: bool = "--safe" in argsList

        foundation = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Foundation")
        version = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
        print(f"Starting up {foundation} {version}")
        Journaling.record("INFO", f"Starting up {foundation} {version}")

        # Load configurations
        Journaling.record("INFO", "Starting service stage 0 with safe mode: " + str(safeMode))
        Services.start(0, safeMode)
        Journaling.record("INFO", "Service stage 0 completed.")
        Journaling.record("INFO", "Setting IPC kernel.safemode to " + str(safeMode) + "...")
        IPC.set("kernel.safemode", safeMode)
        Journaling.record("INFO", "Starting service stage 1 with safe mode: " + str(safeMode))
        Services.start(1, safeMode)
        Journaling.record("INFO", "Service stage 1 completed.")
        Journaling.record("INFO", "Starting service stage 2 with safe mode: " + str(safeMode))
        Services.start(2, safeMode)
        Journaling.record("INFO", "Service stage 2 completed.")
        Journaling.record("INFO", "Starting service stage 3 with safe mode: " + str(safeMode))
        Services.start(3, safeMode)
        Journaling.record("INFO", "Service stage 3 completed.")
        Journaling.record("INFO", "Starting service stage 4 with safe mode: " + str(safeMode))
        Services.start(4, safeMode)  # Shell level
        Journaling.record("INFO", "Service stage 4 completed.")

        Journaling.record("INFO", "Waiting for all service termination...")
        while threading.active_count() > 1:
            time.sleep(1)

        Journaling.record("INFO", "Terminate signal received. Exiting...")

        state = IPC.read("power.off.state", default="REBOOT")
        if state == "OFF":
            return 0
        elif state == "REBOOT":
            return 1
        elif state == "SAFE":
            return 3
        else:
            return 2


    except Exception as e:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"KERNEL CRASHED WITH UNHANDLED EXCEPTION")
        print(f"---------------------------------------")
        print(f"Error Time: {time.ctime()}")
        print(f"Error: {e}")
        print(f"---------------------------------------")
        print(f"Stack Trace:")
        traceback.print_exc()
        print(f"---------------------------------------")
        print(f"System will restart in safe mode after 3 seconds.")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        time.sleep(3)
        return 3
