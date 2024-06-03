from commands.packager.spec import Spec

import requests
import json


def getSpecRawURLFromGitHubURL(repoURL: str, file: str) -> str:
    try:
        # Example input URL:
        # https://github.com/410-dev/CordOS or https://github.com/410-dev/CordOS.git
        if repoURL.endswith(".git"):
            repoURL = repoURL[:-4]
        author, repo = repoURL.split("/")[-2:]

        # Get branches from API
        # https://api.github.com/repos/410-dev/CordOS/branches
        branches = requests.get(f"https://api.github.com/repos/{author}/{repo}/branches").json()

        # Get default branch
        defaultBranch = ""
        for branch in branches:
            if branch["name"] in ["main", "master", "stable"]:
                defaultBranch = branch["name"]
                break
        if defaultBranch == "":
            print(f"Warning: Default branch not found in {author}/{repo}. Using first branch in list: {branches[0]['name']}")
            defaultBranch = branches[0]["name"]

        # Example output URL:
        # https://raw.githubusercontent.com/410-dev/CordOS/branch/spec.json
        return f"https://raw.githubusercontent.com/{author}/{repo}/{defaultBranch}/{file}"
    except Exception as e:
        return f"Error while getting spec from repository. e: {e}"


def fetchFromURL(specURL: str) -> dict:
    try:
        data: dict = requests.get(specURL).json()
        data['state'] = "SUCCESS"
        return data
    except Exception as e:
        return {"state": f"Error while getting spec from URL. e: {e}"}


def fetchFromLocal(specPath: str) -> dict:
    try:
        data: dict = json.load(open(specPath, "r"))
        data['state'] = "SUCCESS"
        return data
    except Exception as e:
        return {"state": f"Error while getting spec from local. e: {e}"}


def fetchSpec(specPath: str) -> dict:
    if specPath.startswith("http://github") or specPath.startswith("https://github") or "github.com" in specPath:
        specURL = getSpecRawURLFromGitHubURL(specPath, "spec.json")
        return fetchFromURL(specURL)
    elif specPath.startswith("file://"):
        return fetchFromLocal(specPath[7:])
    else:
        return fetchFromURL(specPath)


def fetchIndex(indexURL: str) -> dict:
    if indexURL.startswith("http://github") or indexURL.startswith("https://github") or "github.com" in indexURL:
        indexURL = getSpecRawURLFromGitHubURL(indexURL, "index.json")
        return fetchFromURL(indexURL)
    elif indexURL.startswith("file://"):
        return fetchFromLocal(indexURL[7:])
    else:
        return fetchFromURL(indexURL)


def fetchPackage(spec: Spec, output: str, label: str = "core"):
    packageFileURL: str = spec.getObject("payloads")[label]
    print(f"Downloading package from: {packageFileURL}", end=" ")
    result = requests.get(packageFileURL)
    extension = packageFileURL.split(".")[-1]
    with open(f"{output}/{label}.{extension}", "wb") as f:
        f.write(result.content)
        print(f"Success. ({output}/{label}.{extension})")
    return f"{output}/{label}.{extension}", extension
