





## Configurations
### servers.json

### config.json
- registry: The part where you can modify on runtime.



### Tags
root: Use all commands in the bot
- Permissions:
  - edit registry
  - All permissions below
admin: 
  - view settings
  - edit roles
  - edit tags
  - All permissions below


formattedMsg = formattedMsg.replace("$uname", message.author.name)
formattedMsg = formattedMsg.replace("$author", message.author)
formattedMsg = formattedMsg.replace("$uid", message.author.id)
formattedMsg = formattedMsg.replace("$serverid", message.guild.id)
formattedMsg = formattedMsg.replace("$servername", message.guild.name)
formattedMsg = formattedMsg.replace("$message", message.content)