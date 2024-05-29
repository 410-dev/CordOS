import kernel.io as IO
import kernel.partitionmgr as PartitionManager
import kernel.commands.packtool.spec as Spec
import kernel.commands.packtool.database as Database
import json


def remove(ids: list, ignoreDependencies: bool, removeAsChain: bool) -> bool:
    for uid in ids:
        IO.println(f"Removing {uid}...")
        success, stage, message = removeTask(uid, ignoreDependencies, removeAsChain)
        IO.println(message)
        if not success:
            return False
    return True


def removeTask(uid: str, ignoreDependencies: bool, removeAsChain: bool, uninstallingDueToDependency: bool = False) -> tuple:

    if uninstallingDueToDependency:
        IO.println(f"Removing {uid} due to dependency...")

    specPaths = Database.listSpecs()
    targetSpec = None
    for specPath in specPaths:
        if specPath.endswith(f"{uid}.json"):
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if not Spec.validateSpec(spec):
                    return False, "VALIDATE_SPEC", f"Spec {uid} is not valid"
                targetSpec = spec

    if targetSpec is None:
        return False, "CHECK_SPEC", f"Package {uid} is not installed"

    if 'installed' in targetSpec and targetSpec['installed'] == "patch":
        return False, "CHECK_SPEC", f"Package {uid} is installed as patch. This could not be removed automatically."

    if 'target' not in targetSpec:
        return False, "CHECK_SPEC", f"Package {uid} does not contain target. This could not be removed automatically."

    if not ignoreDependencies:
        for specPath in specPaths:
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if 'dependencies' in spec:
                    for dependency in spec['dependencies']:
                        if dependency['id'] == uid:
                            if not removeAsChain:
                                return False, "CHECK_DEPENDENCY", f"Package {uid} is a dependency of {spec['uid']}."
                            removeTask(spec['uid'], ignoreDependencies, removeAsChain)

    target = targetSpec['target']
    if PartitionManager.RootFS.rm(target):
        return True, "REMOVE", f"Package {uid} removed successfully"
    else:
        return False, "REMOVE", f"Package {uid} could not be removed"
