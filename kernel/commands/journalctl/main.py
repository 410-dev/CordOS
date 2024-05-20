import kernel.io as IO
import kernel.journaling as Journaling
import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr
import kernel.clock as Clock
import kernel.ipc as IPC

import traceback
import json
import os


def journalIndex() -> str:
    labels: list = Journaling.JournalingContainer.journals.keys()
    index: str = ""
    for label in labels:
        index += f"{label}\n"
    return index

def getLastNLines(target: str, n: int) -> str:
    journal = Journaling.JournalingContainer.journals[target]
    entries = journal["entries"]
    if n > len(entries):
        n = len(entries)
    return "".join(entries[-n:])



def main(args: list):
    try:
        # Available: dump, list, get
        if len(args) < 2:
            IO.println("Not enough arguments.\nUsage: journalctl <dump|list|read> (target) (length)")
            return
        if args[1] == "dump":
            Journaling.JournalingContainer.dump()
            IO.println("Journal dumped. The dump file is only accessible locally.")

        elif args[1] == "dump-ipc":
            to: str = f"{PartitionMgr.etc()}/journals/ipcdump@{Clock.getTime().split('.')[0]}.json"
            os.makedirs(os.path.dirname(to), exist_ok=True)
            with open(to, "w") as f:
                ipcobj = {
                    "memory": IPC.IPCMemory.memory,
                    "refs": IPC.IPCMemory.referenceTime
                }
                json.dump(ipcobj, f, indent=4)

            IO.println("IPC Memory dumped. The dump file is only accessible locally.")

        elif args[1] == "list":
            IO.println(journalIndex())

        elif args[1] == "read":
            if len(args) < 3:
                IO.println("Not enough arguments.\nUsage: journalctl read <target> (length)")
                return
            target = args[2]
            if target not in Journaling.JournalingContainer.journals.keys():
                IO.println("Target not found.")
                return
            if len(args) > 3:
                try:
                    length = int(args[3])
                    IO.println(getLastNLines(target, length))
                except:
                    IO.println("Invalid length.")
                    return
            IO.println(getLastNLines(target, 10))
    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error in journalctl. e: {e}")
