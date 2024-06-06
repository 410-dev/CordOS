import kernel.partitionmgr as PartitionManager
import json
import os

def path(subdirectory: str = "") -> str:
    return PartitionManager.Etc.path(f"packtool/{subdirectory}")


def getSpecOf(uid: str, scope: str) -> dict:
    # return path(f"specs/{scope}/{name}.json")
    if os.path.exists(path(f"specs/{scope}/{uid}.json")):
        with open(path(f"specs/{scope}/{uid}.json"), "r") as f:
            return json.loads(f.read())
    return None


def setSpecOf(name: str, scope: str, spec: dict):
    PartitionManager.Etc.write(f"packtool/specs/{scope}/{name}.json", json.dumps(spec, indent=4))


def checkSpec(name: str, scope: str) -> bool:
    return PartitionManager.Etc.exists(f"packtool/specs/{scope}/{name}.json")


def dropSpec(name: str, scope: str):
    PartitionManager.Etc.rm(f"packtool/specs/{scope}/{name}.json")


def listSpecs() -> list:
    def recursion(p: str, s: list) -> list:
        print(f"recursion({PartitionManager.Etc.path(p)}, {s})")
        for element in PartitionManager.Etc.list(p):
            if PartitionManager.Etc.isDir(f"{p}/{element}"):
                s = recursion(f"{p}/{element}", s)
            else:
                s.append(f"{p}/{element}")
        return s

    PartitionManager.Etc.mkdir("packtool/specs")

    returned = recursion("packtool/specs", [])
    for i in range(len(returned)):
        returned[i] = os.path.join(PartitionManager.Etc.path(), returned[i])
    return returned


def installed(uid: str, scope: str, git: str, version: str, build: str) -> bool:
    spec = getSpecOf(uid, scope)
    if spec is None:
        return False

    if git is not None and spec['git'] != git:
        return False

    def compare(a, b, comparator):
        if comparator == "<=":
            return a <= b
        elif comparator == ">=":
            return a >= b
        elif comparator == "==":
            return a == b
        elif comparator == "!=":
            return a != b
        elif comparator == "<":
            return a < b
        elif comparator == ">":
            return a > b
        elif comparator == "any":
            return True
        return False

    def separateComparator(value):
        if value == "any":
            return value, "any"

        for comparator in [">=", "<=", "==", "!=", ">", "<"]:
            if comparator in value:
                return value.split(comparator), comparator
        return value, "=="

    if version is None:
        version = "any"
    if build is None:
        build = "any"
    version, versionComparator = separateComparator(version)
    build, buildComparator = separateComparator(build)

    if not compare(spec['version'], version, versionComparator):
        return False
    if not compare(spec['build'], build, buildComparator):
        return False

    return True
