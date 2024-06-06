# Updates the isolated command bundles to the latest version in system global

import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation
import kernel.services.DiscordUIService.fastpermission as FastPermission
import kernel.registry as Registry
import kernel.journaling as Journaling

async def mainAsync(args: list, message):
    if not Isolation.getIsolationAvailable(message):
        await message.reply("Isolation is not available on this instance.", mention_author=True)
        return
    if not Isolation.getIsolationPermission(message, "local.commands.modify"):
        await message.reply(f"Instance does not have permission to update: local.commands.modify: {Isolation.getIsolationPermission(message, 'local.commands.modify')}", mention_author=True)
        return
    permission = Registry.read("SOFTWARE.CordOS.Security.Install", default="root")
    if not FastPermission.hasPermission(message, permission):
        await message.reply(f"You do not have permission to use this command. (Requires {permission})", mention_author=True)
        return
    await message.reply("Updating isolated command bundles and registries to the latest version in system global.", mention_author=True)
    Journaling.record("INFO", "Updating isolated command bundles to the latest version in system global.")
    Isolation.mkIsolation_sync(message, [("commands", "commands")])
    Journaling.record("INFO", "Updating isolated command bundles to the latest version in system global.")
    Isolation.mkIsolation_patchImports(message, Isolation.getContainerPath(message, ""))
    Journaling.record("INFO", "Syncing registries...")
    Isolation.prepareRegistry(message)
    Journaling.record("INFO", "Isolated command bundles and registries are updated.")
    await message.reply("Isolated command bundles and registries are updated.", mention_author=True)
