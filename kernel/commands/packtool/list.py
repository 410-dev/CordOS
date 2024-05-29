import kernel.commands.packtool.spec as Spec
import kernel.commands.packtool.database as Database
import json


def listPackages() -> str:
    specPaths = Database.listSpecs()
    show = []
    for specPath in specPaths:
        if specPath.endswith(f".json"):
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if not Spec.validateSpec(spec):
                    continue

                show.append(f"{spec['id']}: {spec['name']} {spec['version']} ({spec['build']}) at {spec['scope']} {spec['installed'] if 'installed' in spec else ''}")
    return "\n".join(show)
