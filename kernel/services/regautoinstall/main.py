import os
import kernel.registry as Registry
import kernel.journaling as Journaling

def main():
    if not os.path.isdir("AUTOREGINST") and not os.path.exists("PERSISTAUTOREGINST"):
        return

    if os.path.exists("PERSISTAUTOREGINST"):
        for file in os.listdir("PERSISTAUTOREGINST"):
            if file.endswith(".cordreg"):
                Journaling.record("INFO", f"Running auto-registry install for {file}.")
                Registry.build(f"PERSISTAUTOREGINST/{file}")

    if os.path.isdir("AUTOREGINST"):
        for file in os.listdir("AUTOREGINST"):
            if file.endswith(".cordreg"):
                Journaling.record("INFO", f"Running auto-registry install for {file}.")
                Registry.build(f"AUTOREGINST/{file}")
                os.remove(f"AUTOREGINST/{file}")
        os.rmdir("AUTOREGINST")
