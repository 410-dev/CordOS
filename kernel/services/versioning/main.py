import os
import shutil
import kernel.registry as Registry
import kernel.host as Host

"""

This service runs sync mode - Be careful!

"""

def cp(src, dest):
    for root, dirs, files in os.walk(src):
        # Calculate the relative path from the source directory to the current directory
        relative_path = os.path.relpath(root, src)
        current_dest = os.path.join(dest, relative_path)

        # Make sure the current directory exists in the destination
        if not os.path.exists(current_dest):
            os.makedirs(current_dest)
            print(f"Created directory: {current_dest}")

        for file in files:
            src_file_path = os.path.join(root, file)
            dest_file_path = os.path.join(current_dest, file)

            # Copy each file
            shutil.copy2(src_file_path, dest_file_path)
            print(f"Copied {src_file_path} to {dest_file_path}")


def main():
    if Registry.read("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue", default="0") == "0":
        return

    print("Upgrade service started.")
    print("Removing upgrade queue flag.")
    Registry.write("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue", "0")

    try:
        print("Starting upgrade process.")
        upgradeFile: str = Registry.read("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeMode")

        print(f"Overwriting files from {upgradeFile} to root directory.")
        cp(upgradeFile, os.getcwd())

        # If posix
        if Host.isHostPOSIX():
            print("Setting bootable.")
            Host.executeCommand("chmod +x boot.sh")

        print(f"Upgrade complete.")

    except Exception as e:
        print(f"Error upgrading system. e: {e}")
        pass

    print("Upgrade service stopped, and will restart.")
    exit(1)

