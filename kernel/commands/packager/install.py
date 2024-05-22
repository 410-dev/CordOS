import json
import shutil
import string

import kernel.commands.packager.database as Database
import kernel.commands.packager.sources as Sources
import kernel.partitionmgr
import kernel.commands.packager.spec as Spec
import kernel.commands.packager.fetch as Fetch
import kernel.registry as Registry
import kernel.io as IO
import kernel.journaling as Journaling
import kernel.partitionmgr as PartitionMgr
import kernel.profile as Profile
import os
import random
import json

from typing import List


def install(keywords: list, case: str, url=False):
    # Get sources list
    sourcesList = Sources.getSources()

    # If urls, then download all specs
    specQueue = []
    if url:
        for spec in keywords:
            spec = Fetch.fetchSpec(spec)
            if spec["state"] == "SUCCESS":
                # Register package
                spec.pop("state")
                spec = Spec.Spec(spec)
                specQueue.append(spec)
            else:
                IO.println(f"Error while fetching package: {spec}")
                IO.println(spec["state"])

    # Get dependencies
    dependencies: List[dict] = getDependencies(sourcesList, keywords)

    # Check if installed
    for dependency in dependencies:
        installed: bool = Database.isInstalled(dependency['name'], condition=dependency['condition'], packageVersion=dependency['version'])
        if installed:
            dependencies.remove(dependency)

    # check conflicts
    conflicts: dict = {}
    for dependency in dependencies:
        conflictList: List[str] = Database.getConflicts(dependency['name'], condition=dependency['condition'], version=dependency['version'])
        if len(conflictList) > 0:
            if dependency['name'] in conflicts:
                conflicts[dependency['name']].append(conflictList)
            else:
                conflicts[dependency['name']] = conflictList

    for conflict in getConflicts(sourcesList, keywords):
        # conflict is dict with keys: name, target, condition, version
        if Database.isInstalled(conflict['name'], condition=conflict['condition'], packageVersion=conflict['version']):
            if conflict['target'] in conflicts:
                conflicts[conflict['target']].append(conflict['name'])
            else:
                conflicts[conflict['target']] = [conflict['name']]

    # Throw error if conflicts
    if len(conflicts) > 0:
        IO.println("Error - Package installation cannot be continued due to conflicts.")
        IO.println("Conflicts found:")
        for conflict in conflicts:
            IO.println(f"{conflict} conflicts with:")
            for conflictingPackage in conflicts[conflict]:
                IO.println(f"  {conflictingPackage}")
        return

    # Get packages
    if not url:
        specURLs = getSpecURLOf(sourcesList, keywords)
    
        # Download specs
        for spec in specURLs:
            spec = Fetch.fetchSpec(spec)
            if spec["state"] == "SUCCESS":
                # Register package
                spec.pop("state")
                spec = Spec.Spec(spec)
                specQueue.append(spec)
            else:
                IO.println(f"Error while fetching package: {spec}")
                IO.println(spec["state"])

    # Check compatibility
    for spec in specQueue:
        # SDK
        if not Profile.isPackageSDKCompatible(spec.getSDKVersion()):
            IO.println(f"Error: Package {spec.getName()} is not compatible with current SDK version. Expected SDK version in range: {spec.getVersion()}, package has SDK version: {spec.getSDKVersion()}")
            return

        # Architecture
        if not spec.getArch() == "any" and not spec.getArch() == Profile.getArch():
            IO.println(f"Error: Package {spec.getName()} is not compatible with current architecture. Expected architecture: {spec.getArch()}, system architecture: {Profile.getArch()}")
            return

    # Create temporary location for packages
    randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    tempLocation = PartitionMgr.cache() + "/packages/" + randomstr
    os.mkdir(tempLocation)

    installFailed = []

    def shouldRunInstruction(instruction: dict, memory: dict):
        if instruction["if"] is None:
            return True

        for key in instruction["if"].keys():
            if key not in memory:
                return not instruction["if"][key]['exists']
            compare = instruction["if"][key]['compare']
            value = instruction["if"][key]['value']
            if compare == "==":
                if memory[key] != value:
                    return False
            elif compare == "!=":
                if memory[key] == value:
                    return False
            elif compare == ">":
                if memory[key] <= value:
                    return False
            elif compare == "<":
                if memory[key] >= value:
                    return False
            elif compare == ">=":
                if memory[key] < value:
                    return False
            elif compare == "<=":
                if memory[key] > value:
                    return False
        return True

    # Run install procedures for each package by following its specs
    for idx, spec in enumerate(specQueue):
        # Get procedure as list
        procedure = spec.getObject("procedure")
        if procedure is None:
            IO.println(f"Warning: Package {spec.getName()} does not contain procedure to install, skipping.")
            installFailed.append(spec.getName())
            continue

        dedicatedMemory: dict = {"case": case}
        for instructionObject in procedure:
            task = instructionObject["task"]
            if not shouldRunInstruction(instructionObject, dedicatedMemory):
                continue
            if task == "delete":
                try:
                    target: list = instructionObject["target"]
                    for t in target:
                        os.remove(t)
                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "install":
                try:
                    package = instructionObject["package"]
                    packageLocation = tempLocation + "/" + spec.getName()
                    if spec.getObject("payloads")[package] is None:
                        IO.println(f"Skip {idx}: Warning - Package {spec.getName()} does not contain package '{package}'.")
                        continue
                    os.mkdir(packageLocation)
                    IO.println(f"Get {idx}: ", end="")
                    Fetch.fetchPackage(spec, packageLocation, label=package)
                    IO.println(f"Install {idx}: ", end="")
                    # Unpack package
                    packageObjPath: str = str(os.path.join(packageLocation, package))
                    extractTo: str = str(os.path.join(packageLocation, f"extracted-{package}"))
                    shutil.unpack_archive(packageObjPath, extractTo)

                    # Create receipt
                    def recursiveFSSearch(path: str) -> list:
                        files = []
                        for root, dirs, files in os.walk(path):
                            for f in files:
                                files.append(os.path.join(root, f))
                        return files

                    IO.println(f"Building file lists...")
                    files = recursiveFSSearch(extractTo)
                    meta = {
                        "extracted": extractTo,
                        "files": files
                    }

                    # Copy files to root
                    shutil.copytree(extractTo, kernel.partitionmgr.root())
                    shutil.copy(os.path.join(packageLocation, "receipt"), kernel.partitionmgr.root())

                    # Database register
                    Database.register(spec, meta["files"], meta)

                    # Clean up
                    shutil.rmtree(packageLocation)

                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "filecheck":
                try:
                    conditions = instructionObject["conditions"]
                    anyFalse = False
                    for condition in conditions:
                        fileName = condition['file']
                        exists = condition['exists'] if 'exists' in condition else True # Assume true
                        value = condition['value'] if 'value' in condition else None
                        if fileName == None:
                            continue

                        if not os.path.exists(os.path.join(PartitionMgr.root(), fileName)) and exists:
                            IO.println(f"fck: File {fileName} does not exist.")
                            anyFalse = True
                            break

                        if value is not None:
                            with open(os.path.join(PartitionMgr.root(), fileName), "r") as file:
                                content = file.read().strip()
                                if content != value:
                                    IO.println(f"fck: File {fileName} does not match value.")
                                    anyFalse = True
                                    break

                    if anyFalse and instructionObject["false"]:
                        for key in instructionObject["false"].keys():
                            dedicatedMemory[key] = instructionObject["false"][key]
                    elif not anyFalse and instructionObject["true"]:
                        for key in instructionObject["true"].keys():
                            dedicatedMemory[key] = instructionObject["true"][key]
                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "inputprompt":
                try:
                    message: str = instructionObject["message"]
                    value = input(message)
                    cases = instructionObject["cases"]
                    for caseObject in cases:
                        if caseObject['input'] == value:
                            if caseObject['message'] is not None:
                                IO.println(caseObject['message'])
                            if caseObject['set'] is not None:
                                for key in caseObject['set'].keys():
                                    dedicatedMemory[key] = caseObject['set'][key]
                            break
                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "IO.println":
                try:
                    message: str = instructionObject["message"]
                    for memory in dedicatedMemory:
                        message = message.replace(f"{{{memory}}}", dedicatedMemory[memory])
                    IO.println(message)
                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "copy":
                try:
                    source: list = instructionObject["source"]
                    destination: list = instructionObject["destination"]
                    for idx2, src in enumerate(source):
                        target: str = destination[idx2]
                        shutil.copy(src, target)

                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            if task == "write":
                try:
                    target: str = instructionObject["target"]
                    content: str = instructionObject["content"]
                    with open(target, "w") as file:
                        file.write(content)
                except Exception as e:
                    if instructionObject["ignoreFail"]:
                        IO.println(f"Error: {e}")
                    else:
                        IO.println(f"Error: {e}")
                        installFailed.append(spec.getName())
                        break

            else:
                IO.println(f"Warning: Unknown task: {task}")


def getDependencies(sourcesList, keywords: list) -> List[dict]:
    # get dependency list
    dependencies = []
    for source in sourcesList:
        for package in source["packages"]:
            if not package["name"] in keywords:
                continue

            for dependency in package["dependencies"]:
                if not dependency.has_key("version"):
                    dependency['condition'] = "=="
                    dependency['version'] = "any"
                else:
                    if dependency['version'].startswith("=="):
                        dependency['version'] = dependency['version'][2:]
                        dependency['condition'] = "=="
                    elif dependency['version'].startswith(">="):
                        dependency['version'] = dependency['version'][2:]
                        dependency['condition'] = ">="
                    elif dependency['version'].startswith("<="):
                        dependency['version'] = dependency['version'][2:]
                        dependency['condition'] = "<="
                    elif dependency['version'].startswith(">"):
                        dependency['version'] = dependency['version'][1:]
                        dependency['condition'] = ">"
                    elif dependency['version'].startswith("<"):
                        dependency['version'] = dependency['version'][1:]
                        dependency['condition'] = "<"
                    elif dependency['version'].startswith("!="):
                        dependency['version'] = dependency['version'][2:]
                        dependency['condition'] = "!="
                    else:
                        dependency['condition'] = "=="
                dependencies.append(dependency)
                subsequentDependencies: List[dict] = getDependencies(sourcesList, [dependency['name']])
                dependencies.extend(subsequentDependencies)
    return dependencies


def getConflicts(sourcesList, keywords: list) -> List[dict]:
    # get conflicts list
    conflicts = []
    for source in sourcesList:
        for package in source["packages"]:
            if not package["name"] in keywords:
                continue

            for conflict in package["conflicts"]:
                if not conflict.has_key("version"):
                    conflict['condition'] = "=="
                    conflict['version'] = "any"
                else:
                    if conflict['version'].startswith("=="):
                        conflict['version'] = conflict['version'][2:]
                        conflict['condition'] = "=="
                    elif conflict['version'].startswith(">="):
                        conflict['version'] = conflict['version'][2:]
                        conflict['condition'] = ">="
                    elif conflict['version'].startswith("<="):
                        conflict['version'] = conflict['version'][2:]
                        conflict['condition'] = "<="
                    elif conflict['version'].startswith(">"):
                        conflict['version'] = conflict['version'][1:]
                        conflict['condition'] = ">"
                    elif conflict['version'].startswith("<"):
                        conflict['version'] = conflict['version'][1:]
                        conflict['condition'] = "<"
                    elif conflict['version'].startswith("!="):
                        conflict['version'] = conflict['version'][2:]
                        conflict['condition'] = "!="
                    else:
                        conflict['condition'] = "=="
                conflict['target'] = package['name']
                conflicts.append(conflict)
                subsequentConflicts: List[dict] = getConflicts(sourcesList, [conflict['name']])
                conflicts.extend(subsequentConflicts)
    return conflicts


def getSpecURLOf(sourcesList, keywords: list) -> list:
    # Get packages
    packages = []
    for source in sourcesList:
        for package in source["packages"]:
            if package["name"] in keywords:
                packageUrl: str = source["source"]
                packageUrl = packageUrl.replace("{name}", package["name"])
                packageUrl = packageUrl.replace("{version}", package["version"])
                packageUrl = packageUrl.replace("{build}", str(package["build"]))
                packageUrl = packageUrl.replace("{sdk}", str(package["sdk"]))
                packageUrl = packageUrl.replace("{arch}", str(package["arch"]))
                packages.append(packageUrl)
                keywords.remove(package["name"])
                
    return packages
