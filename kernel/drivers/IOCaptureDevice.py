
class IOCaptureDevice:
    def __init__(self):
        self.input = []
        self.output = []

    def capture_input(self, prompt: str) -> str:
        data = input(prompt)
        self.output.append(prompt)
        self.input.append(data)
        return data

    def capture_output(self, string: str, end: str = '', flush: bool = False):
        self.output.append(string)
        if string == '\n':
            self.output.append('')
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
        return ''.join(self.output)

    def clearAll(self):
        self.clearInput()
        self.clearOutput()
        return
