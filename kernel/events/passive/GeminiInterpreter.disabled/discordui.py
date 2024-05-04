import kernel.events.passive.GeminiInterpreter.ConstructiveIODevice as IODrivers
import kernel.events.passive.GeminiInterpreter.GeminiConnector as GeminiConnector
import kernel.services.DiscordUIService.asynclauncher as AsyncLauncher

import kernel.journaling as Journaling
import kernel.ipc as IPC
import kernel.io as IO
import kernel.registry as Registry
import kernel.launchcmd as Launcher
import objects.discordmessage as DiscordMessage

import discord
import traceback
import json

async def mainAsync(message: DiscordMessage.DiscordMessageWrapper):
    if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.Enabled", default="0") != "1":
        return
    Journaling.record("INFO", "Experimental feature LLM Assistant is enabled.")
    discordClient: discord.Client = IPC.read("discord.client")
    llmCommand: str = message.content
    IO.println(f"Comparing discord id with bot id: {discordClient.user.id}...")
    if message.content.startswith(f"<@{discordClient.user.id}>") or message.content.startswith(f"<@!{discordClient.user.id}>"):
        llmCommand = llmCommand.replace(f"<@{discordClient.user.id}>", "").replace(f"<@!{discordClient.user.id}>", "")
    else:
        return

    if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.DisableExperimentalWarning", default="0") != "1":
        await message.reply("This feature is experimental and may not work as intended. Use at your own risk. Any response from this does not mean or intended by developer of CordOS or any related components of this feature.", mention_author=True)

    if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.DisableWorkingStartMessage", default="0") != "1":
        await message.reply("LLM is currently working... Please wait.", mention_author=True)

    # Copy message instance to a new instance
    modifiableWrapper = DiscordMessage.DiscordMessageWrapper(message.message)
    modifiableWrapper.content = "fasthelp"
    modifiableWrapper.useStdIO = True
    modifiableWrapper.indrv = IODrivers.constructiveInput
    modifiableWrapper.outdrv = IODrivers.constructiveOutput

    # Execute the command
    await interpreter(modifiableWrapper)

    # Pull the output from the IO driver
    output: list = IODrivers.IORecords.getOutputRecordsAsString().split("\n")
    IODrivers.IORecords.clearOutputRecords()

    # Drop first line
    output.pop(0)

    # Iterate over the output and send them
    fullOutput: list = []
    for line in output:
        manualStr: str = ""
        # manualStr += f"Manual for {line} command: =================="
        modifiableWrapper.useStdIO = True
        modifiableWrapper.indrv = IODrivers.constructiveInput
        modifiableWrapper.outdrv = IODrivers.constructiveOutput
        modifiableWrapper.content = f"help {line}"
        await interpreter(modifiableWrapper)
        manualStr += "\n"
        manualStr += IODrivers.IORecords.getOutputRecordsAsString()
        IODrivers.IORecords.clearOutputRecords()
        manualStr = "\n".join([line for line in manualStr.split("\n") if line.strip() != ""])
        manualStr = manualStr.replace("```", "")
        manualStr += "=================="
        fullOutput.append(manualStr)

    # Send the output
    stringForLLM = "\n".join(fullOutput)
    stringForLLM += "Given the manual above, provide appropriate command, and appropriate command only, by following the given request. Make sure to use listed commands ONLY without creation. Here's example:\n"
    stringForLLM += "\"User<@1226964349940273152>: 현재 버전좀 알려줘\"\n\n"
    stringForLLM += "Output should show as such:\n"
    stringForLLM += "{\n"
    stringForLLM += "\"reasoning\": \"The user is asking for version. The version related command is 'version' command.\",\n"
    stringForLLM += "\"generated\": [\"version\"]"
    stringForLLM += "}\n\n"
    stringForLLM += "Here's an invalid request:\n"
    stringForLLM += "\"User<@1226964349940273152>: 그림 그려봐\"\n\n"
    stringForLLM += "Output should show as such:\n"
    stringForLLM += "{\n"
    stringForLLM += "\"reasoning\": \"The user request cannot be handled using given modules. User has to know that such task is unsupported, and see the available lists. This can be achieved by showing message using 'echo' command and 'fasthelp' consecutively.\",\n"
    stringForLLM += "\"generated\": [\"echo 요청하신 작업은 현재 설치된 명령어로 실행이 불가능 합니다. 실행 가능 명령어를 보시려면 'fasthelp' 명령어를 입력하세요.\", \"fasthelp\"]\n"
    stringForLLM += "}\n\n"
    stringForLLM += "Here's the actual user request:\n"
    stringForLLM += f"\"User<@{discordClient.user.id}>: {llmCommand}\"\n\n"

    output: str = GeminiConnector.sendRequest(stringForLLM)
    IO.println(f"Output from LLM: {output}")

    # Parse output to dict
    output: dict = json.loads(output)
    reasoning: str = output["reasoning"]
    generated: list = output["generated"]

    if Registry.read("SOFTWARE.CordOS.Experimental.LLMAssistant.DisableReasoningStepMessage", default="0") != "1":
        await message.reply(f"LLM concluded to execute `{generated}` with following reasoning:\n`{reasoning}`", mention_author=True)

    for cmd in generated:
        message.content = cmd
        await interpreter(message)


async def interpreter(message: DiscordMessage.DiscordMessageWrapper):
    try:
        args: list = Launcher.splitArguments(message.content)
        cmd: str = Launcher.getCommand(args)
        Journaling.record("INFO", f"Command '{cmd}' executed by {message.author.name}#{message.author.discriminator}.")
        runnablePath: str = Launcher.getRunnableModule(args, "discordui")
        Journaling.record("INFO", f"Command '{cmd}' found at '{runnablePath}'.")
    except Exception as e:
        Journaling.record("ERROR", f"Failed looking up for command. The issue is highly likely from Launcher.getRunnableModule. e: {e}")
        await message.reply(f"Failed looking up for command. This should not occur. {e}", mention_author=True)
        return

    if runnablePath == "" or runnablePath is None:
        Journaling.record("WARNING", f"Command '{cmd}' not found.")
        await message.reply(f"Command {cmd} not found.", mention_author=True)
        return

    try:
        Journaling.record("INFO", f"Executing command - Passing to AsyncLauncher.runRunnableModule: '{cmd}'.")
        await AsyncLauncher.runRunnableModule(runnablePath, args, message)
    except Exception as e:
        Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{cmd}': {e}")
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        await message.reply(f"Error executing command '{cmd}': {e}", mention_author=True)

