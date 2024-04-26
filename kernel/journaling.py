import datetime
import traceback
import os

import kernel.clock as Clock
import kernel.partitionmgr as PartitionMgr

def record(state: str, text: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = traceback.extract_stack(None, 2)[0]

    callerName = caller.name
    if "<" in callerName or "main" == callerName or "mainAsync" in callerName:
        bundleName = os.path.dirname(caller.filename).replace("//", "/").replace("\\", "/").split("/")[-1]
        scriptFileName = os.path.basename(caller.filename).replace(".py", "")
        callerName = f"{bundleName}.{scriptFileName}"

    specificJournal = f"{PartitionMgr.data()}/etc/journals/{Clock.getStartTime().split(".")[0]}/{callerName}.journal"
    globalJournal = f"{PartitionMgr.data()}/etc/journals/{Clock.getStartTime().split(".")[0]}/_.journal"

    # Create directory
    directory = os.path.dirname(specificJournal)
    os.makedirs(directory, exist_ok=True)

    # Write to file if not exists
    if not os.path.exists(specificJournal):
        with open(specificJournal, "w") as f:
            scriptPath = caller.filename.replace("//", "/").replace("\\", "/").replace(os.path.abspath(PartitionMgr.root()).replace("//", "/").replace("\\", "/"), "")
            f.write(f"Script Location: {scriptPath}\n")
            f.write(f"[{timestamp}] [{state}] [{caller.name}@{callerName}] {text}\n")
    else:
        with open(specificJournal, "a") as f:
            f.write(f"[{timestamp}] [{state}] [{caller.name}@{callerName}] {text}\n")

    if not os.path.exists(globalJournal):
        with open(globalJournal, "w") as f:
            f.write(f"[{timestamp}] [{state}] [{caller.name}@{callerName}] {text}\n")
    else:
        with open(globalJournal, "a") as f:
            f.write(f"[{timestamp}] [{state}] [{caller.name}@{callerName}] {text}\n")
