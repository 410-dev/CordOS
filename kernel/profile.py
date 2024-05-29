import kernel.registry as Registry
import kernel.host as Host


def isPackageSDKCompatible(sdkv: int):
    sdkRange = getPackageSDKRange()
    return sdkRange[0] <= sdkv <= sdkRange[1]


def isServiceSDKCompatible(sdkv: int):
    # return Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.Compatibility.SDKMinimum") <= sdkv <= Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.Compatibility.SDKMaximum")
    return int(Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.Compatibility.SDKMinimum", default=0)) <= sdkv <= int(Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.Compatibility.SDKMaximum", default=1))


def getPackageSDKRange():
    # return Registry.read("SOFTWARE.NanoPyOS.Packages.Compatibility.SDKMinimum"), Registry.read("SOFTWARE.NanoPyOS.Packages.Compatibility.SDKMaximum")
    return int(Registry.read("SOFTWARE.NanoPyOS.Packages.Compatibility.SDKMinimum", default=0)), int(Registry.read("SOFTWARE.NanoPyOS.Packages.Compatibility.SDKMaximum", default=1))


def getArch():
    return Host.getHostOSArchitecture()


def isArchCompatible(archStr: str):
    return getArch() == archStr or archStr == "any" or archStr in getArch()


def isPlatformCompatible(platformStr: str):
    return Host.getHostOSType() == platformStr or platformStr == "any" or platformStr in Host.getHostOSType()


def getKernelVersion():
    return Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Version")


def getKernelName():
    return Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Name")


def getKernelBuild():
    return Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Build")
