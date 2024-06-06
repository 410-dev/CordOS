import kernel.registry as Registry
import kernel.host as Host


def isPackageSDKCompatible(sdkv: int):
    sdkRange = getPackageSDKRange()
    return sdkRange[0] <= sdkv <= sdkRange[1]


def isServiceSDKCompatible(sdkv: int):
    sdkRange = getServiceSDKRange()
    return sdkRange[0] <= sdkv <= sdkRange[1]


def getServiceSDKRange():
    # return Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMinimum"), Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMaximum")
    return int(Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMinimum", default=0)), int(Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMaximum", default=1))

def getPackageSDKRange():
    # return Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMinimum"), Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMaximum")
    return int(Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMinimum", default=0)), int(Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMaximum", default=1))


def getArch():
    return Host.getHostOSArchitecture()


def isArchCompatible(archStr: str):
    return getArch() == archStr or archStr == "any" or archStr in getArch()


def isPlatformCompatible(platformStr: str):
    return Host.getHostOSType() == platformStr or platformStr == "any" or platformStr in Host.getHostOSType()


def getKernelVersion():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")


def getKernelName():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Name")


def getKernelBuild():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Build")
