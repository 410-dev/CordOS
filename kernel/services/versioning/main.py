import os
import shutil
import kernel.registry as Registry
import kernel.host as Host
import kernel.io as IO

"""

This service runs sync mode - Be careful!

"""

def cp(src: str, dest: str):
    for root, dirs, files in os.walk(src, topdown=True):
        # Ensure the directory structure is mirrored in dest
        for dir_name in dirs:
            source_dir = os.path.join(root, dir_name)
            relative_path = os.path.relpath(source_dir, src)
            destination_dir = os.path.join(dest, relative_path)

            try:
                os.makedirs(destination_dir)
                IO.println(f"Directory created: {destination_dir}")
            except FileExistsError:
                IO.println(f"Directory already exists: {destination_dir}")

        # Copy each file
        for file_name in files:
            source_file = os.path.join(root, file_name)
            relative_path = os.path.relpath(source_file, src)
            destination_file = os.path.join(dest, relative_path)

            shutil.copy2(source_file, destination_file)
            IO.println(f"File copied: {source_file} to {destination_file}")


def main():
    if Registry.read("SOFTWARE.NanoPyOS.Boot.VersioningIssue.UpgradeQueue", default="0") == "0":
        return

    IO.println("Upgrade service started.")
    IO.println("Removing upgrade queue flag.")
    Registry.write("SOFTWARE.NanoPyOS.Boot.VersioningIssue.UpgradeQueue", "0")

    try:
        IO.println("Starting upgrade process.")
        upgradeFile: str = Registry.read("SOFTWARE.NanoPyOS.Boot.VersioningIssue.UpgradeMode")
        upgradeFile = os.path.join(os.getcwd(), upgradeFile)

        IO.println(f"Overwriting files from {upgradeFile} to root directory.")
        cp(upgradeFile, os.getcwd())

        # If posix
        if Host.isPOSIX():
            IO.println("Setting bootable.")
            Host.executeCommand("chmod +x boot.sh")

        IO.println(f"Upgrade complete.")

        IO.println(f"Cleaning up upgrade files.")
        shutil.rmtree(upgradeFile)
        IO.println(f"Upgrade files cleaned up.")

    except Exception as e:
        IO.println(f"Error upgrading system. e: {e}")
        pass

    IO.println("Upgrade service stopped, and will restart.")
    exit(1)

