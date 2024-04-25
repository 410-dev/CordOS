import os
import json

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr

from kernel.commands.packager.spec import Spec


def getPackagesDBPath():
    path = Registry.read("SOFTWARE.CordOS.Packages.Database.Location", default=f"{PartitionMgr.data()}/etc/packager/database/")
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def getSourcesDBPath():
    path = Registry.read("SOFTWARE.CordOS.Sources.Database.Location", default=f"{PartitionMgr.data()}/etc/packager/sources/")
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def compare(value1, value2, condition):
    if condition == "==":
        return value1 == value2
    elif condition == ">":
        return value1 > value2
    elif condition == "<":
        return value1 < value2
    elif condition == ">=":
        return value1 >= value2
    elif condition == "<=":
        return value1 <= value2
    elif condition == "!=":
        return value1 != value2


def isInstalled(packageName: str, condition: str = "==", packageVersion: str = "any", packageBuild: int = -1):
    # Check if package is installed
    databaseLocation = getPackagesDBPath()

    packageList = os.listdir(databaseLocation)
    for package in packageList:
        if not package == f"{packageName}.cpkg":
            continue

        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            if packageVersion == "any" and packageBuild == -1:
                return True

            spec = Spec(f"{databaseLocation}/{package}/spec.json")
            if packageVersion == "any":
                if compare(spec.getBuild(), packageBuild, condition):
                    return True
            elif packageBuild == -1:
                if compare(spec.getVersion(), packageVersion, condition):
                    return True
            else:
                if compare(spec.getVersion(), packageVersion, condition) and compare(spec.getBuild(), packageBuild, condition):
                    return True


def register(spec: Spec, receipt: list, meta: dict):
    # Register package
    databaseLocation = getPackagesDBPath()

    if not os.path.exists(f"{databaseLocation}/{spec.getName()}.cpkg"):
        os.mkdir(f"{databaseLocation}/{spec.getName()}.cpkg")

    with open(f"{databaseLocation}/{spec.getName()}.cpkg/spec.json", "w") as file:
        file.write(spec.data)

    receipt: str = "\n".join(receipt)
    with open(f"{databaseLocation}/{spec.getName()}.cpkg/receipt", "w") as file:
        file.write(receipt)

    with open(f"{databaseLocation}/{spec.getName()}.cpkg/meta", "w") as file:
        file.write(json.dumps(meta))


def listDependentOn(packageName: str):
    # List packages dependent on package
    databaseLocation = getPackagesDBPath()
    dependencyList: list = []
    for package in os.listdir(databaseLocation):
        if not os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            continue

        spec = Spec(f"{databaseLocation}/{package}/spec.json")
        if spec.getObject("dependencies") is None:
            continue

        dependencies: dict = spec.getObject("dependencies")
        if packageName in dependencies:
            dependencyList.append(package)

    return dependencyList


def getConflicts(packageName: str, condition: str = "==", version: str = "any", build: int = -1) -> list:
    # Check if package conflicts with installed packages
    databaseLocation = getPackagesDBPath()

    packageList = os.listdir(databaseLocation)
    conflictList: list = []
    for package in packageList:
        if not package == f"{packageName}.cpkg":
            continue

        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            spec = Spec(f"{databaseLocation}/{package}/spec.json")
            if version == "any" and build == -1:
                conflictList.append(package)
            elif compare(spec.getVersion(), version, condition) and compare(spec.getBuild(), build, condition):
                conflictList.append(package)

    return conflictList


def unregister(packageName: str):
    # Unregister package
    databaseLocation = getPackagesDBPath()

    packageList = os.listdir(databaseLocation)
    for package in packageList:
        if not package == f"{packageName}.cpkg":
            continue

        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            os.remove(f"{databaseLocation}/{package}/spec.json")
        if os.path.isfile(f"{databaseLocation}/{package}/receipt"):
            os.remove(f"{databaseLocation}/{package}/receipt")
        os.rmdir(f"{databaseLocation}/{package}")


def getInfo(packageName: str) -> Spec:
    # Get package info
    databaseLocation = getPackagesDBPath()

    packageList = os.listdir(databaseLocation)
    for package in packageList:
        if not package == f"{packageName}.cpkg":
            continue

        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            spec = Spec(f"{databaseLocation}/{package}/spec.json")
            return spec


def getPackagesInstalled(includeInfo: list = None) -> list:
    # Get installed packages
    if includeInfo is None:
        includeInfo = ["name"]
    databaseLocation = getPackagesDBPath()

    packageList = os.listdir(databaseLocation)
    installedPackages: list = []
    for package in packageList:
        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            jsonData = json.load(open(f"{databaseLocation}/{package}/spec.json", "r"))
            packageInfo = {}
            if len(includeInfo) == 1:
                installedPackages.append(jsonData[includeInfo[0]])
                continue

            for info in includeInfo:
                packageInfo[info] = jsonData[info]

            installedPackages.append(packageInfo)

    return installedPackages
