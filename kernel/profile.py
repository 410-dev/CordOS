import kernel.registry as Registry
import kernel.host as Host


def isPackageSDKCompatible(sdkv: int):
    return Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMinimum") <= sdkv <= Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMaximum")


def isServiceSDKCompatible(sdkv: int):
    return Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMinimum") <= sdkv <= Registry.read("SOFTWARE.CordOS.Kernel.Services.Compatibility.SDKMaximum")


def getPackageSDKRange():
    return Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMinimum"), Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMaximum")


def getArch():
    return Host.getHostOSArchitecture()


def isArchCompatible(archStr: str):
    return getArch() == archStr or archStr == "any" or archStr in getArch()


def getKernelVersion():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")


def getKernelName():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Name")


def getKernelBuild():
    return Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Build")
