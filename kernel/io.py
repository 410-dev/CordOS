from kernel.drivers.StandardIODevice import stdio_input, stdio_output

defaultOutput = stdio_output
defaultInput = stdio_input


def init(outputFunction=print, inputFunction=input):
    global defaultOutput
    global defaultInput
    defaultOutput = outputFunction
    defaultInput = inputFunction
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
    defaultInput = inputFunction
    return


def setOutput(outputFunction):
    global defaultOutput
    defaultOutput = outputFunction
    return
