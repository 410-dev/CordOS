import os
import subprocess

def getHostOSType():
    return os.name

def isPOSIX():
    return os.name == "posix"

def isWindows():
    return os.name == "nt"

def getHostOSName():
    return os.uname().sysname

def getHostOSRelease():
    return os.uname().release

def getHostOSVersion():
    return os.uname().version

def getHostOSArchitecture():
    return os.uname().machine

def getHostOSInfo():
    return os.uname()

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