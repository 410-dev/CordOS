import requests
import json


def getSpecFromRepository(repoURL: str) -> str:
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
        return f"https://raw.githubusercontent.com/{author}/{repo}/{defaultBranch}/spec.json"
    except Exception as e:
        return f"Error while getting spec from repository. e: {e}"


def getSpecFromURL(specURL: str) -> str:
    try:
        return requests.get(specURL).json()
    except Exception as e:
        return f"Error while getting spec from URL. e: {e}"


def getSpecFromLocal(specPath: str) -> str:
    try:
        return json.load(open(specPath))
    except Exception as e:
        return f"Error while getting spec from local. e: {e}"
