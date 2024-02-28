import kernel.partitionmgr as PartitionMgr

import os
import datetime

def init():
    cacheLoc: str = PartitionMgr.cache()
    cacheLoc = os.path.join(cacheLoc, "krnlsrv", "clock")
    os.makedirs(cacheLoc, exist_ok=True)
    if not os.path.exists(os.path.join(cacheLoc, "start")):
        with open(os.path.join(cacheLoc, "start"), "w") as f:
            f.write(str(datetime.datetime.now().timestamp()))
            print("Clock initialized.")
    

def getUptime():
    cacheLoc: str = PartitionMgr.cache()
    cacheLoc = os.path.join(cacheLoc, "krnlsrv", "clock")
    try:
        with open(os.path.join(cacheLoc, "start"), "r") as f:
            start = float(f.read())
            now = datetime.datetime.now().timestamp()
            uptime = now - start
            return str(datetime.timedelta(seconds=uptime))
    except:
        print("Error in reading start file.")
        return "0:00:00"
    
def getUptimeSeconds():
    cacheLoc: str = PartitionMgr.cache()
    cacheLoc = os.path.join(cacheLoc, "krnlsrv", "clock")
    try:
        with open(os.path.join(cacheLoc, "start"), "r") as f:
            start = float(f.read())
            now = datetime.datetime.now().timestamp()
            uptime = now - start
            return uptime
    except:
        print("Error in reading start file.")
        return 0
    
def getTime() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getEpoch() -> int:
    return int(datetime.datetime.now().timestamp())

def getDay() -> str:
    return datetime.datetime.now().strftime("%A")

def getDate() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")

def getYear() -> str:
    return datetime.datetime.now().strftime("%Y")

def getMonth() -> str:
    return datetime.datetime.now().strftime("%m")

def getHour() -> str:
    return datetime.datetime.now().strftime("%H")

def getMinute() -> str:
    return datetime.datetime.now().strftime("%M")

def getSecond() -> str:
    return datetime.datetime.now().strftime("%S")

def getMicrosecond() -> str:
    return datetime.datetime.now().strftime("%f")[:-3]

def getWeek() -> str:
    return datetime.datetime.now().strftime("%V")

def getWeekday() -> str:
    return datetime.datetime.now().strftime("%w")

def getISOWeek() -> str:
    return datetime.datetime.now().strftime("%G-W%V-%u")

def getISODate() -> str:
    return datetime.datetime.now().strftime("%G-%m-%d")
