import json
import kernel.registry as Registry


class Spec:
    def __init__(self, path):
        self.path = path
        self.data = json.load(open(path))

        # Load from JSON
        self.spec: str = self.data["spec"]
        self.specv: int = self.data["specv"]
        self.sdk: int = self.data["sdk"]

        # Check compatibility
        installerSpecVersion = int(Registry.read("SOFTWARE.CordOS.Packages.Compatibility.InstallerSpecVersion", default=1))
        systemSupportedSDKMinimum = int(Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMinimum", default=1))
        systemSupportedSDKMaximum = int(Registry.read("SOFTWARE.CordOS.Packages.Compatibility.SDKMaximum", default=1))

        if self.spec is None or self.specv is None or self.sdk is None:
            raise Exception("Invalid spec file. (Missing fields)")

        if self.spec != "CordOSInstallablePackage":
            raise Exception("Invalid spec file. (Header mismatch)")

        if self.specv != installerSpecVersion:
            raise Exception("Invalid spec file. (Version mismatch)")

        if self.sdk < systemSupportedSDKMinimum or self.sdk > systemSupportedSDKMaximum:
            raise Exception("Incompatible package. (SDK version mismatch)")

    def getSDKVersion(self):
        return self.sdk

    def getName(self):
        return self.getObject("name")

    def getVersion(self):
        return self.getObject("version")

    def getBuild(self):
        return self.getObject("build")

    def getDescription(self):
        return self.getObject("description")

    def getAuthor(self):
        return self.getObject("author")

    def getObject(self, key):
        if "." in key:
            keys = key.split(".")
            obj = self.data
            for key in keys:
                obj = obj[key]
            return obj

        return self.data[key]
