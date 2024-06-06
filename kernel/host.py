import os
import subprocess

def getHostOSType():
    return os.name

def isPOSIX():
    return os.name == "posix"

def isWindows():
    return os.name == "nt"

def getHostOSName():
    if isPOSIX():
        return os.uname().sysname
    elif isWindows():
        return os.name
    return "Unknown"

def getHostOSRelease():
    if isPOSIX():
        return os.uname().release
    elif isWindows():
        return os.name
    return "Unknown"

def getHostOSVersion():
    if isPOSIX():
        return os.uname().version
    elif isWindows():
        return os.name
    return "Unknown"

def getHostOSArchitecture():
    if isPOSIX():
        return os.uname().machine
    elif isWindows():
        return os.name

def getHostOSInfo():
    if isPOSIX():
        return os.uname()
    elif isWindows():
        return os.name

def executeCommand(command: str):
    return os.system(command)

def executeCommandWithStdOut(command: str) -> str:
    return os.popen(command).read()


def executeCommand2(command: list, cwd = "./") -> dict:
    # The returning dictionary contains the following keys
    # "cmd": the command executed
    # "returncode": the return code of the command
    # "stdout": the standard output of the command
    # "stderr": the standard error of the command
    try:
        returned = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, cwd=cwd)
        return {
            "cmd": command,
            "returncode": returned.returncode,
            "stdout": returned.stdout.decode("utf-8"),
            "stderr": returned.stderr.decode("utf-8")
        }
    except subprocess.CalledProcessError as e:
        return {
            "cmd": command,
            "returncode": e.returncode,
            "stdout": e.stdout.decode("utf-8") if e.stdout else "",
            "stderr": e.stderr.decode("utf-8") if e.stderr else str(e)
        }
    except Exception as e:
        return {
            "cmd": command,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }