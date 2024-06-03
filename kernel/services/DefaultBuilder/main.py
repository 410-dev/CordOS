import kernel.partitionmgr as PartitionMgr
import kernel.profile as Profile
import kernel.journaling as Journaling

def main():
    if PartitionMgr.Etc.isFile("corestorageversion") and PartitionMgr.Etc.read("corestorageversion") == Profile.getKernelBuild():
        Journaling.record("INFO", f"CoreStorage ({PartitionMgr.etc()}) is up-to-date and matches the current kernel build.")
        return

    Journaling.record("INFO", f"CoreStorage ({PartitionMgr.etc()}) is outdated or does not match the current kernel build. Updating...")
    try:
        PartitionMgr.RootFS.copy("defaults/etc", PartitionMgr.etc())
        PartitionMgr.Etc.write("corestorageversion", Profile.getKernelBuild())
    except Exception as e:
        Journaling.record("ERROR", f"Failed to update CoreStorage ({PartitionMgr.etc()}). Reason: {e}")
        return

    Journaling.record("INFO", f"CoreStorage ({PartitionMgr.etc()}) has been updated to match the current kernel build.")
