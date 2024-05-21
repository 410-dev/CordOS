class SimpleAutomationInputDevice:
    def __init__(self, input_data: list):
        self.input = []
        self.output = []
        self.inputQueue = input_data

    def capture_input(self, prompt: str) -> str:
        data = self.inputQueue.pop(0)
        self.output.append(prompt)
        self.input.append(data)
        return data

    def capture_output(self, string: str, end: str = '', flush: bool = False):
        self.output.append(string)
        print(string, end=end, flush=flush)
        return

    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def clearInput(self):
        self.input = []
        return

    def clearOutput(self):
        self.output = []
        return

    def getInputAsString(self):
        return '\n'.join(self.input)

    def getOutputAsString(self):
        return '\n'.join(self.output)

    def clearAll(self):
        self.clearInput()
        self.clearOutput()
        return
