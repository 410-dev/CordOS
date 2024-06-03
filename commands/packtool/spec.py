import kernel.registry as Registry
import kernel.journaling as Journaling
import kernel.profile as Profile


def getPreference(key: str, equals=None, default=None):
    if equals is not None:
        value = Registry.read(f"SOFTWARE.NanoPyOS.Packager.Prefs.{key}", default=default)
        if value == equals:
            return True
        return False
    return Registry.read(f"SOFTWARE.NanoPyOS.Packager.Prefs.{key}", default=default)


def validateSpec(data: dict):
    if getPreference("BypassSpecValidation", equals="1"):
        Journaling.record("INFO", "Bypassing spec validation")
        return True, "bypassed"

    if not getPreference("BypassSpecVersion", equals="1"):
        if data["spec"] is None:
            return False, "Spec version not found"
        elif data["spec"] != "NanoPyOS.Standards.PackageSpec":
            return False, "Spec version mismatch"

        if data["specv"] is None:
            return False, "Spec version not found"
        elif Profile.isPackageSDKCompatible(int(data["specv"])):
            return False, "Spec version mismatch"

    if not getPreference("BypassSpecArch", equals="1"):
        if data["arch"] is None:
            return False, "Arch not found"
        elif not Profile.isArchCompatible(data["arch"]):
            return False, "Arch mismatch"

    if not getPreference("BypassSpecPlatform", equals="1"):
        if data["platform"] is None:
            return False, "Platform not found"
        elif not Profile.isPlatformCompatible(data["platform"]):
            return False, "Platform mismatch"

    if not getPreference("BypassSpecServiceSDK", equals="1"):
        if data["sdk"] is None:
            return False, "SDK version not found"
        elif not Profile.isServiceSDKCompatible(int(data["sdk"])):
            return False, "SDK version mismatch"

    requiredFields = [
        ("name", str),
        ("id", str),
        ("version", str),
        ("author", str),
        ("description", str),
        ("build", int),
        # ("arch", str),      # If not specified, it is assumed to be "any"
        # ("platform", str),  # If not specified, it is assumed to be "any"
        ("scope", str),
        ("git", str),
        # ("dependencies", dict),
        # ("conflicts", dict),
        # ("pip", dict),
        # ("triggers", dict)
    ]

    for field, fieldType in requiredFields:
        if field not in data:
            return False, f"Field {field} not found"
        elif not isinstance(data[field], fieldType):
            return False, f"Field {field} type mismatch"

    return True, "success"
