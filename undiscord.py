print("Undiscord Tool for CordOS")
print("This tool will remove all discord related code from the CordOS source code.")

import os
import re
import fnmatch

# Remove all discord related code
knownDiscordFiles = [
    "*/discordui.py",
    "*/configure_discordui.py",
    "./commands/jot",
    "./commands/note",
    "./commands/tags",
    "./commands/vc",
    "./kernel/events/interaction/DiscordUIInterpreter",
    "./kernel/events/passive/GeminiInterpreter.disabled",
    "./kernel/events/passive/MessageLogger",
    "./kernel/objects/discordmessage.py",
    "./kernel/objects/embedmsg.py",
    "./kernel/objects/server.py",
    "./kernel/objects/user.py",
    "./kernel/services/DiscordUIService",
    "./kernel/services/webhook",
    "./kernel/servers.py",
    "./kernel/webhook.py",
]

neglectQueryPatterns = [
    "*.git/*",
    "*/docs/*",
    "*.pyc",
    "*/venv/*",
    "*/.venv/*",
    "*/__pycache__/*",
    "*/etc/*",
    "*/storage/*",
    "*/tmp/*",
    "*.idea/*",
    "*.gitignore",
    "*.gitattributes",
    "*.DS_Store",
    "*undiscord.py"
]


def recursiveFileBuild(path: str, l: list) -> list:
    for element in os.listdir(path):
        full_path = os.path.join(path, element)
        if any(fnmatch.fnmatch(full_path, pattern) for pattern in neglectQueryPatterns):
            continue

        if os.path.isdir(full_path):
            l += recursiveFileBuild(full_path, [])
        else:
            l.append(full_path)
    return l


def recursiveDirectoryDelete(path: str):
    for element in os.listdir(path):
        if os.path.isdir(os.path.join(path, element)):
            recursiveDirectoryDelete(os.path.join(path, element))
        else:
            os.remove(os.path.join(path, element))
            print(f"Removed {os.path.join(path, element)}")
    os.rmdir(path)
    print(f"Removed {path}")


def expandAsterisk(expandableList: list, fullFileList: list) -> list:  # Return fully expanded list
    expandedList = expandableList.copy()
    for idx, pattern in enumerate(expandableList):
        for file in fullFileList:
            if fnmatch.fnmatch(file, pattern):
                if pattern in expandedList:
                    expandedList.remove(pattern)
                expandedList.insert(0, file)

    for idx, element in enumerate(expandedList):
        expandedList[idx] = element.replace("/", os.sep)
    return expandedList


print("Building file list...")
fileList = expandAsterisk(knownDiscordFiles, recursiveFileBuild(".", []))

print("Removable files: ")
for file in fileList:
    print(file)

print("Removing files...")
for file in fileList:
    if os.path.isdir(file):
        recursiveDirectoryDelete(file)
    elif os.path.isfile(file):
        os.remove(file)
        print(f"Removed {file}")
    else:
        print(f"Warning: {file} is not a file or directory.")

print("Rebuilding file list for refactoring...")
fileList = recursiveFileBuild(".", [])


print("Refactoring files...")
substitutionList = [
    ("CordOS", "NanoPyOS"),
    ("cordos", "nanopyos"),
    ("CORDOS", "NANOPYOS")
]
for file in fileList:
    if os.path.isfile(file):
        try:
            with open(file, "r") as f:
                content = f.read()
                for substitution in substitutionList:
                    content = content.replace(substitution[0], substitution[1])
                with open(file, "w") as f2:
                    f2.write(content)
                    print(f"Refactored {file} successfully.")
        except Exception as e:
            print(f"Error in refactoring {file}. e: {e}")

print("Updating requirements.txt...")
try:
    with open("requirements.txt", "r") as f:
        content = f.read()
        contentData = content.split("\n")
        newContent = ""
        for line in contentData:
            if "discord" not in line:
                newContent += line + "\n"
        with open("requirements.txt", "w") as f2:
            f2.write(newContent)
            print("Updated requirements.txt successfully.")
except Exception as e:
    print(f"Error in updating requirements.txt. e: {e}")

print("Done.")
