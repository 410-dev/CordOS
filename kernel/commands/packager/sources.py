import requests
import json
import os

import kernel.commands.packager.database as Database
import kernel.commands.packager.spec as Spec

import kernel.profile as Profile


def download(url: str) -> dict:
    try:
        if url.startswith("file://"):
            return json.load(open(url[7:], "r"))
        else:
            response = requests.get(url)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                return {}
    except:
        return {}


def getSources():
    databaseLocation = Database.getSourcesDBPath()

    if not os.path.exists(databaseLocation):
        os.mkdir(databaseLocation)

    indexFilesList = os.listdir(databaseLocation)
    items = []
    for item in indexFilesList:
        if not item.endswith(".index.json"):
            indexFilesList.remove(item)
        else:
            try:
                items.append(json.load(open(f"{databaseLocation}/{item}", "r")))
            except Exception as e:
                print(f"Error while loading {item}. e: {e}")

    return items


def add(idxJsonURL: str):
    # Add source
    indexData = download(idxJsonURL)
    if indexData == {}:
        print("Invalid index file - Fetch failed")
        return "Invalid index file - Fetch failed"

    if not 'spec' in indexData or not 'specv' in indexData:
        print("Invalid index file - Missing fields")
        return "Invalid index file - Missing fields"

    if indexData['specv'] != 1 or indexData['spec'] != "CordOSInstallablePackageRepositoryIndex":
        print("Invalid index file - Index version/spec mismatch")
        return "Invalid index file - Index version/spec mismatch"

    databaseLocation = Database.getSourcesDBPath()
    id = indexData["id"]
    with open(f"{databaseLocation}/{id}.index.json", "w") as f:
        f.write(json.dumps(indexData, indent=4))
    print("Source added successfully")
    return "Source added successfully"


def remove(idxJsonURL: str):
    # Remove source
    databaseLocation = Database.getSourcesDBPath()
    id = idxJsonURL.split("/")[-1].split(".")[0]
    if os.path.exists(f"{databaseLocation}/{id}.index.json"):
        os.remove(f"{databaseLocation}/{id}.index.json")
        print("Source removed successfully")
        return "Source removed successfully"
    else:
        print("Source not found")
        return "Source not found"


def sync():
    # Sync sources
    indexList = getSources()
    print("Syncing sources...")
    changedSources = []
    for index in indexList:
        print(f"Syncing {index['name']} ({index['id']}): {index['index']}...")
        newIndex = download(index['index'])
        if newIndex == {}:
            print(f"Failed syncing {index['name']} ({index['id']}): {index['index']}")
            continue
        if not 'spec' in newIndex or not 'specv' in newIndex:
            print(f"Failed syncing {index['name']} ({index['id']}): {index['index']} - Missing fields")
            continue
        if newIndex['specv'] != 1 or newIndex['spec'] != "CordOSInstallablePackageRepositoryIndex":
            print(f"Failed syncing {index['name']} ({index['id']}): {index['index']} - Index version/spec mismatch")
            continue
        if newIndex['updateTime'] != index['updateTime']:
            changedSources.append(index['name'])
            with open(f"{Database.getSourcesDBPath()}/{index['id']}.index.json", "w") as f:
                f.write(json.dumps(newIndex, indent=4))
            print(f"Synced (Updated) {index['name']} ({index['id']}): {index['index']}")
        else:
            print(f"Synced (No changes) {index['name']} ({index['id']}): {index['index']}")

    print(f"Sync completed. Updated sources: {len(changedSources)} of {len(indexList)}")
    return f"Sync completed. Updated sources: {len(changedSources)} of {len(indexList)}"


def listUpdatablePackages(indexList: list = None) -> list:
    # List updatable packages
    if indexList is None:
        indexList = getSources()

    updatablePackages = []
    for index in indexList:
        packagesInIndex = index['packages']
        for package in packagesInIndex:
            if not Database.isInstalled(package['name']):
                continue

            installedVersion: Spec = Database.getInfo(package['name'])
            if installedVersion.getVersion() == package['version'] and installedVersion.getBuild() == package['build']:
                continue

            if not Profile.isPackageSDKCompatible(package['sdk']):
                print(f"Package {package['name']} is not compatible with current SDK version")
                continue

            if not Profile.isArchCompatible(package['arch']):
                print(f"Package {package['name']} is not compatible with current architecture")
                continue

            url: str = package['url']
            # Iterate through package fields
            for field in package.keys():
                if isinstance(package[field], str) or isinstance(package[field], int):
                    url = url.replace(f"{{{field}}}", str(package[field]))

            package['url'] = url
            updatablePackages.append(package)

    return updatablePackages
