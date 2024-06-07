import kernel.io as IO
import kernel.partitionmgr as PartitionManager
import kernel.journaling as Journaling
import commands.packtool.database as database
import commands.packtool.spec as Spec
import json


def remove(ids: list, ignoreDependencies: bool, removeAsChain: bool) -> tuple:
    data = {}
    message = ""
    for uid in ids:
        IO.println(f"Removing {uid}...")
        Journaling.record("INFO", f"Removing {uid}...")
        success, stage, message, data = removeTask(uid, ignoreDependencies, removeAsChain, data)
        IO.println(message)
        Journaling.record("INFO", message)
        if not success:
            return False, message
    return True, message


def removeTask(uid: str, ignoreDependencies: bool, removeAsChain: bool, data: dict, uninstallingDueToDependency: bool = False) -> tuple:

    if uid.startswith("--"):
        data[uid] = True
        return True, "DATA_SET", f"Set data {uid} to True", data

    if uninstallingDueToDependency:
        IO.println(f"Removing {uid} due to dependency...")
        Journaling.record("INFO", f"Removing {uid} due to dependency...")

    specPaths = database.listSpecs()
    targetSpec = None
    for specPath in specPaths:
        if specPath.endswith(f"{uid}.json"):
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if not Spec.validateSpec(spec):
                    return False, "VALIDATE_SPEC", f"Spec {uid} is not valid", data
                targetSpec = spec

    if targetSpec is None:
        return False, "CHECK_SPEC", f"Package {uid} is not installed", data

    if 'installed' in targetSpec and targetSpec['installed'] == "patch":
        return False, "CHECK_SPEC", f"Package {uid} is installed as patch. This could not be removed automatically.", data

    if 'target' not in targetSpec:
        return False, "CHECK_SPEC", f"Package {uid} does not contain target. This could not be removed automatically.", data

    if not ignoreDependencies:
        for specPath in specPaths:
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if 'dependencies' in spec:
                    for dependency in spec['dependencies']:
                        if dependency['id'] == uid:
                            if not removeAsChain:
                                return False, "CHECK_DEPENDENCY", f"Package {uid} is a dependency of {spec['uid']}.", data
                            removeTask(spec['uid'], ignoreDependencies, removeAsChain, data)

    target = targetSpec['target']
    if PartitionManager.RootFS.rm(target):
        database.dropSpec(uid, targetSpec['scope'])
        return True, "REMOVE", f"Package {uid} removed successfully", data
    else:
        return False, "REMOVE", f"Package {uid} could not be removed", data
