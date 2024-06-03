import os
import time

import kernel.partitionmgr as PartitionMgr
import kernel.clock as Clock
import kernel.ipc as IPC
import kernel.io as IO

def main():
    cache = os.path.join(PartitionMgr.cache(), "krnlsrv")

    clockLastFile = os.path.join(cache, "clock", "last")

    os.makedirs(os.path.dirname(clockLastFile), exist_ok=True)

    if os.path.isfile(clockLastFile):
        IO.println(f"WARNING: SYSTEM NOT SHUTDOWN PROPERLY. THIS MAY BE DUE TO SYSTEM CRASH.")
        with open(clockLastFile, "r") as f:
            ltime = f.read()
            ltime = ltime.split("\n")[0]
            IO.println(f"Last unexpected termination time: {ltime}")

    try:
        def run():
            with open(clockLastFile, "w") as f:
                f.write(f"TIME:{Clock.getTime()}\nEPOCH:{Clock.getEpoch()}\nUPTIME:{Clock.getUptime()}")

        IPC.repeatUntilShutdown(1, run)

        # On shutdown trigger
        os.remove(clockLastFile)
        IO.println("Safe shutdown tracker stopped.")

    except KeyboardInterrupt:
        pass