import os

def getHostOSType():
    return os.name

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
