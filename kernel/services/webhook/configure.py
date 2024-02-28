import kernel.registry as Registry
import kernel.webhook as Webhook

import os

async def main(args: list, message):

    # Args:
    #    link <url> <webhookid>
    #    unlink <url> <webhookid>
    #    list

    if len(args) < 1:
        await message.reply("Usage: webhook <link|unlink|list> <url> <webhookid>")
        return

    if args[0] == "link":
        if len(args) < 3:
            await message.reply("Missing arguments: <url> <webhookid>")
            return
        
        links = Webhook.getLibrary(args[2]) + "/linkages"
        # write url with no special characters
        specialChars: list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "-"]
        url = args[1]
        url = url.split("webhooks/")[1]
        for char in specialChars:
            url = url.replace(char, "")
        

        with open(f"{links}/{url}", 'w') as f:
            f.write(args[1])

        await message.reply(f"Linked {args[1]} to {args[2]}")

    elif args[0] == "unlink":
        if len(args) < 3:
            await message.reply("Missing arguments: <url> <webhookid>")
            return
        
        links = Webhook.getLibrary(args[2]) + "/linkages"
        # write url with no special characters
        specialChars: list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "-"]
        url = args[1]
        url = url.split("webhooks/")[1]
        for char in specialChars:
            url = url.replace(char, "")

        try:
            os.remove(f"{links}/{url}")
            await message.reply(f"Unlinked {args[1]} from {args[2]}")
        except:
           await  message.reply(f"Failed to unlink {args[1]} from {args[2]}")

    elif args[0] == "list":
        webhooks = Webhook.list()
        await message.reply(f"Webhooks: {webhooks}")
    
    