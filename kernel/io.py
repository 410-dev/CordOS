from kernel.drivers.StandardIODevice import stdio_input, stdio_output


backupOutput = stdio_output
backupInput = stdio_input

defaultOutput = stdio_output
defaultInput = stdio_input


def init(outputFunction=print, inputFunction=input):
    global defaultOutput
    global defaultInput
    global backupInput
    global backupOutput
    defaultOutput = outputFunction
    defaultInput = inputFunction
    backupInput = inputFunction
    backupOutput = outputFunction
    return


def printf(string):
    global defaultOutput
    defaultOutput(string)
    return


def println(string):
    printf(string + '\n')
    return


def read(prompt):
    global defaultInput
    return defaultInput(prompt)


def setInput(inputFunction):
    global defaultInput
    global backupInput
    backupInput = defaultInput
    defaultInput = inputFunction
    return


def setOutput(outputFunction):
    global defaultOutput
    global backupOutput
    backupOutput = defaultOutput
    defaultOutput = outputFunction
    return

def restoreInput():
    global defaultInput
    global backupInput
    defaultInput = backupInput
    return

def restoreOutput():
    global defaultOutput
    global backupOutput
    defaultOutput = backupOutput
    return

def restoreAll():
    restoreInput()
    restoreOutput()