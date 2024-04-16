import os

import kernel.registry as Registry
import kernel.partitionmgr as PartitionMgr

from kernel.commands.install.spec import Spec


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
    databaseLocation = Registry.read("SOFTWARE.CordOS.Packages.Database.Location", default=f"{PartitionMgr.data()}/etc/packages.d/")

    if not os.path.exists(databaseLocation):
        os.mkdir(databaseLocation)

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


def register(spec: Spec, receipt: list):
    # Register package
    databaseLocation = Registry.read("SOFTWARE.CordOS.Packages.Database.Location", default=f"{PartitionMgr.data()}/etc/packages.d/")

    if not os.path.exists(databaseLocation):
        os.mkdir(databaseLocation)

    if not os.path.exists(f"{databaseLocation}/{spec.getName()}"):
        os.mkdir(f"{databaseLocation}/{spec.getName()}")

    with open(f"{databaseLocation}/{spec.getName()}/spec.json", "w") as file:
        file.write(spec.data)

    receipt: str = "\n".join(receipt)
    with open(f"{databaseLocation}/{spec.getName()}/receipt", "w") as file:
        file.write(receipt)


def listDependentOn(packageName: str):
    # List packages dependent on package
    databaseLocation = Registry.read("SOFTWARE.CordOS.Packages.Database.Location", default=f"{PartitionMgr.data()}/etc/packages.d/")
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


def unregister(packageName: str):
    # Unregister package
    databaseLocation = Registry.read("SOFTWARE.CordOS.Packages.Database.Location", default=f"{PartitionMgr.data()}/etc/packages.d/")

    if not os.path.exists(databaseLocation):
        os.mkdir(databaseLocation)

    packageList = os.listdir(databaseLocation)
    for package in packageList:
        if not package == f"{packageName}.cpkg":
            continue

        if os.path.isfile(f"{databaseLocation}/{package}/spec.json"):
            os.remove(f"{databaseLocation}/{package}/spec.json")
        if os.path.isfile(f"{databaseLocation}/{package}/receipt"):
            os.remove(f"{databaseLocation}/{package}/receipt")
        os.rmdir(f"{databaseLocation}/{package}")
