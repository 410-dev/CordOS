import json
import commands.packtool.database as database


def listPackages() -> str:
    specPaths = database.listSpecs()
    show = []
    for specPath in specPaths:
        if specPath.endswith(f".json"):
            with open(specPath, "r") as f:
                spec = json.loads(f.read())
                if not spec.validateSpec(spec):
                    continue

                show.append(f"{spec['id']}: {spec['name']} {spec['version']} ({spec['build']}) at {spec['scope']} {spec['installed'] if 'installed' in spec else ''}")
    return "\n".join(show)
