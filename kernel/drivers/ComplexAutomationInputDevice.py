class ComplexAutomationInputDevice:
    def __init__(self, automatedInputDecisionMaker: callable):
        self.input = []
        self.output = []
        self.fullLog = []
        self.decisionMaker = automatedInputDecisionMaker

    def capture_input(self, prompt: str) -> str:
        # Expect callable to have signature: callable(prompt: str, capturedInput: list, capturedOutput: list, fullLog: list) -> str
        data = self.decisionMaker(prompt, self.input, self.output, self.fullLog)
        self.output.append(prompt)
        self.input.append(data)
        return data

    def capture_output(self, string: str, end: str = '', flush: bool = False):
        self.output.append(string)
        print(string, end=end, flush=flush)
        return

    def setDecisionMaker(self, automatedInputDecisionMaker: callable):
        self.decisionMaker = automatedInputDecisionMaker
        return
