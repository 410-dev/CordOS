# Updates the isolated command bundles to the latest version in system global

import kernel.services.DiscordUIService.subsystem.sv_isolation as Isolation
import kernel.journaling as Journaling

async def mainAsync(args: list, message):
    if not Isolation.getIsolationPermission(message, "global.commands.execute") or not Isolation.getIsolationPermission(message, "local.commands.modify"):
        await message.reply(f"Instance does not have permission to update: global.commands.execute: {Isolation.getIsolationPermission(message, 'global.commands.execute')}, local.commands.modify: {Isolation.getIsolationPermission(message, 'local.commands.modify')}", mention_author=True)
        return
    await message.reply("Updating isolated command bundles to the latest version in system global.", mention_author=True)
    Journaling.record("INFO", "Updating isolated command bundles to the latest version in system global.")
    Isolation.mkIsolation_sync(message, [("commands", "commands")])
    Journaling.record("INFO", "Updating isolated command bundles to the latest version in system global.")
    Isolation.mkIsolation_patchImports(message, Isolation.getContainerPath(message, ""))
    await message.reply("Isolated command bundles updated.", mention_author=True)