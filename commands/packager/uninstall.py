import kernel.partitionmgr as PartitionMgr
import kernel.journaling as Journaling

def uninstall(packages: list):
    Journaling.record("INFO", f"Uninstalling packages: {', '.join(packages)}")
