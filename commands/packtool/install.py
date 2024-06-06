import kernel.io as IO
import kernel.host as Host
import kernel.partitionmgr as PartitionManager
import kernel.journaling as Journaling
import commands.packtool.database as database
import commands.packtool.spec as Spec
import requests
import shutil
import json


def install(urls: list, mode: str, ignoreDependencies: bool, ignoreConflicts: bool, reinstall: bool) -> tuple:
    data = {}
    for url in urls:
        IO.println(f"Installing {url}...")
        Journaling.record("INFO", f"Installing {url}...")
        success, stage, message, data = installTask(url, mode, ignoreDependencies, ignoreConflicts, reinstall, data)
        if not success:
            Journaling.record("ERROR", f"Failed to install {url} - {stage}: {message}")
            IO.println(f"Failed to install {url} - {stage}: {message}")
            return False, f"Failed to install {url} - {stage}: {message}"
        IO.println(message)
    return True, "Successfully installed packages"


def installTask(url: str, mode: str, ignoreDependencies: bool, ignoreConflicts: bool, reinstall: bool, data: dict) -> tuple:

    if url.startswith("--"):
        data[url] = True
        Journaling.record("INFO", f"Set data {url} to True")
        return True, "DATA_SET", f"Set data {url} to True", data

    # Download url as plain text - this is specification
    IO.println("Downloading spec...")
    Journaling.record("INFO", f"Downloading spec {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        return False, "DOWNLOAD_SPEC", f"Failed to download {url} - status code {response.status_code}", data

    # Try parsing to JSON
    try:
        IO.println("Parsing spec...")
        Journaling.record("INFO", "Parsing spec...")
        spec = json.loads(response.text)
    except:
        return False, "PARSE_SPEC", f"Failed to parse {url} as JSON", data

    # Check if spec is valid
    IO.println("Validating spec...")
    Journaling.record("INFO", "Validating spec...")
    validationResult = Spec.validateSpec(spec)
    if not validationResult[0]:
        return False, "VALIDATE_SPEC", f"Spec {url} is not valid: {validationResult[1]}", data

    # Check dependencies and conflicts
    IO.println("Currently installing: " + spec['name'] + " " + spec['version'])
    Journaling.record("INFO", f"Currently installing: {spec['name']} {spec['version']}")
    IO.println("Checking dependencies...")
    Journaling.record("INFO", "Checking dependencies...")
    if 'dependencies' in spec and not ignoreDependencies:
        for dependency in spec['dependencies']:
            if not database.installed(dependency['id'], dependency['scope'], dependency['git'], dependency['version'], dependency['build']):
                return False, "CHK_DEPENDENCY", f"Dependency {dependency['name']} is not installed", data

    if 'conflicts' in spec and not ignoreConflicts:
        for conflict in spec['conflicts']:
            if database.installed(conflict['id'], conflict['scope'], conflict['git'], conflict['version'], conflict['build']):
                return False, "CHK_CONFLICT", f"Conflicting package {conflict['name']} is installed", data

    # Check if spec is already installed
    IO.println("Checking spec...")
    Journaling.record("INFO", "Checking spec...")
    originalSpec = database.getSpecOf(spec['id'], spec['scope'])
    update = False
    if originalSpec is not None:
        if originalSpec['version'] == spec['version'] and originalSpec['build'] == spec['build'] and originalSpec['git'] == spec['git'] and not reinstall:
            return False, "CHK_DUPLICATION", f"Spec {spec['name']} is already installed with version {spec['version']}", data
        else:
            if not reinstall:
                IO.println(f"Spec {spec['name']} is already installed with version {originalSpec['version']} and build {originalSpec['build']}. Updating...")
                Journaling.record("INFO", f"Spec {spec['name']} is already installed with version {originalSpec['version']} and build {originalSpec['build']}. Updating...")
            else:
                IO.println(f"Spec {spec['name']} is already installed with version {originalSpec['version']} and build {originalSpec['build']}. Reinstalling...")
                Journaling.record("INFO", f"Spec {spec['name']} is already installed with version {originalSpec['version']} and build {originalSpec['build']}. Reinstalling...")
            database.dropSpec(spec['name'], spec['scope'])
            update = True

    # Run git clone
    IO.println("Updating scope keys...")
    Journaling.record("INFO", "Updating scope keys...")
    clonePath = spec['scope']
    specialKeys = [
        ("$storage", PartitionManager.Data.path()),
        ("$etc", PartitionManager.Etc.path()),
        ("$root", PartitionManager.RootFS.path())
    ]
    for key, value in specialKeys:
        clonePath = clonePath.replace(key, value)

    # Drop first slash if exists
    while clonePath.startswith("/"):
        clonePath = clonePath[1:]

    if spec['scope'] != "$root" and ('autowrap' not in spec or spec['autowrap']):
        clonePath += f"/{spec['name'].replace(' ', '-')}"

    allowPatchInstall = spec['allowPatchInstall'] if 'allowPatchInstall' in spec else False

    if mode == "patch" and allowPatchInstall:
        if 'zip' not in spec:
            return False, "PATCH_ZIP", f"Spec {spec['name']} does not have 'zip' field for patch install", data
        IO.println(f"Downloading patch archive for {spec['name']} {spec['version']} to {clonePath}...")
        response = requests.get(spec['zip'])
        if response.status_code != 200:
            return False, "DOWNLOAD_PATCH", f"Failed to download patch archive for {spec['name']} {spec['version']} - status code {response.status_code}", data
        IO.println("Saving patch archive...")
        Journaling.record("INFO", "Saving patch archive...")
        with open(f"{clonePath}.zip", "wb") as file:
            file.write(response.content)
        IO.println("Extracting patch archive...")
        Journaling.record("INFO", "Extracting patch archive...")
        shutil.unpack_archive(f"{clonePath}.zip", clonePath)
        IO.println("Removing patch archive...")
        Journaling.record("INFO", "Removing patch archive...")
        shutil.rmtree(f"{clonePath}.zip")
        spec['installed'] = "patch"

    else:
        if not allowPatchInstall and mode == "patch":
            IO.println(f"Patch install is not allowed for {spec['name']} {spec['version']}")
            Journaling.record("ERROR", f"Patch install is not allowed for {spec['name']} {spec['version']}")

        if not update:
            IO.println(f"Installing {spec['name']} {spec['version']} to {clonePath}...")
            Journaling.record("INFO", f"Installing {spec['name']} {spec['version']} to {clonePath}...")
            command = [
                "git",
                "clone",
                spec['git'],
                clonePath
            ]
        else:
            IO.println(f"Updating {spec['name']} {spec['version']} at {clonePath}...")
            Journaling.record("INFO", f"Updating {spec['name']} {spec['version']} at {clonePath}...")
            command = [
                "git",
                "-C",
                clonePath,
                "pull"
            ]
        subprocessRun: dict = Host.executeCommand2(command)
        if subprocessRun['returncode'] != 0:
            output = subprocessRun['stdout'] + "\n\n" + subprocessRun['stderr']
            Journaling.record("ERROR", f"Failed to clone repository {spec['git']} to {clonePath} - return code {subprocessRun['returncode']} with output {output}")
            if "commit your changes" in output:
                if data['--force']:
                    IO.println("Hard reseting repository...")
                    Journaling.record("INFO", "Hard reseting repository...")
                    Host.executeCommand2(["git", "reset", "--hard"], cwd=clonePath)
                    Journaling.record("INFO", "Pulling repository...")
                    subprocessRun: dict = Host.executeCommand2(command)
                    if subprocessRun['returncode'] != 0:
                        return False, "GIT_CLONE", f"Failed to clone repository after hard reset {spec['git']} to {clonePath} - return code {subprocessRun['returncode']} with output {subprocessRun['stdout']}", data

            return False, "GIT_CLONE", f"Failed to clone repository {spec['git']} to {clonePath} - return code {subprocessRun['returncode']} with output {subprocessRun['stdout']}", data
        IO.println("Successfully installed files.")
        Journaling.record("INFO", "Successfully installed files.")

    # Install spec
    IO.println("Installing spec...")
    Journaling.record("INFO", "Installing spec...")
    spec['id'] = spec['id'].replace(" ", "-")
    spec['target'] = clonePath
    database.setSpecOf(spec['id'], spec['scope'], spec)

    IO.println(f"Installation complete for {spec['name']} {spec['version']}")
    Journaling.record("INFO", f"Installation complete for {spec['name']} {spec['version']}")

    return True, "SUCCESS", f"Successfully installed {spec['name']} {spec['version']}", data
