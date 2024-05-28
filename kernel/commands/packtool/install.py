import kernel.io as IO
import kernel.host as Host
import kernel.partitionmgr as PartitionManager
import kernel.commands.packtool.spec as Spec
import kernel.commands.packtool.database as Database
import requests
import json


def install(urls: list):
    for url in urls:
        IO.println(f"Installing {url}...")
        success, stage, message = installTask(url)
        if not success:
            IO.println(message)
            return


def installTask(url: str) -> tuple:
    # Download url as plain text - this is specification
    IO.println("Downloading spec...")
    response = requests.get(url)
    if response.status_code != 200:
        return False, "DOWNLOAD_SPEC", f"Failed to download {url} - status code {response.status_code}"

    # Try parsing to JSON
    try:
        IO.println("Parsing spec...")
        spec = json.loads(response.text)
    except:
        return False, "PARSE_SPEC", f"Failed to parse {url} as JSON"

    # Check if spec is valid
    IO.println("Validating spec...")
    if not Spec.validateSpec(spec):
        return False, "VALIDATE_SPEC", f"Spec {url} is not valid"

    # Check dependencies and conflicts
    IO.println("Checking dependencies...")
    if 'dependencies' in spec:
        for dependency in spec['dependencies']:
            if not Database.installed(dependency['id'], dependency['scope'], dependency['git'], dependency['version'], dependency['build']):
                return False, "CHK_DEPENDENCY", f"Dependency {dependency['name']} is not installed"

    if 'conflicts' in spec:
        for conflict in spec['conflicts']:
            if Database.installed(conflict['id'], conflict['scope'], conflict['git'], conflict['version'], conflict['build']):
                return False, "CHK_CONFLICT", f"Conflicting package {conflict['name']} is installed"

    # Check if spec is already installed
    IO.println("Checking spec...")
    originalSpec = Database.getSpecOf(spec['id'], spec['scope'])
    update = False
    if originalSpec is not None:
        if originalSpec['version'] == spec['version'] and originalSpec['build'] == spec['build'] and originalSpec['git'] == spec['git']:
            return False, "CHK_DUPLICATION", f"Spec {spec['name']} is already installed with version {spec['version']}"
        else:
            IO.println(f"Spec {spec['name']} is already installed with version {originalSpec['version']} and build {originalSpec['build']}. Updating...")
            Database.dropSpec(spec['name'], spec['scope'])
            update = True

    # Install spec
    IO.println("Installing spec...")
    Database.setSpecOf(spec['id'], spec['scope'], spec)

    # Run git clone
    IO.println("Updating scope keys...")
    clonePath = spec['scope']
    specialKeys = [
        ("$storage", PartitionManager.data()),
        ("$etc", PartitionManager.etc()),
    ]
    for key, value in specialKeys:
        clonePath = clonePath.replace(key, value)

    # Drop first slash if exists
    while clonePath.startswith("/"):
        clonePath = clonePath[1:]

    if not update:
        IO.println(f"Installing {spec['name']} {spec['version']} with build {spec['build']}...")
        command = [
            "git",
            "clone",
            spec['git'],
            clonePath
        ]
    else:
        IO.println(f"Updating {spec['name']} {spec['version']} with build {spec['build']}...")
        command = [
            "git",
            "-C",
            clonePath,
            "pull"
        ]
    subprocessRun: dict = Host.executeCommand2(command)
    if subprocessRun['returncode'] != 0:
        return False, "GIT_CLONE", f"Failed to clone repository {spec['git']} to {clonePath} - return code {subprocessRun['returncode']} with output {subprocessRun['stdout']}"
    return True, "SUCCESS", f"Successfully installed {spec['name']} {spec['version']} with build {spec['build']}"
