
class IORecords:
    inputRecords = []
    outputRecords = []

    @staticmethod
    def addInputRecord(record: str):
        IORecords.inputRecords.append(record)

    @staticmethod
    def addOutputRecord(record: str):
        IORecords.outputRecords.append(record)

    @staticmethod
    def clearInputRecords():
        IORecords.inputRecords = []

    @staticmethod
    def clearOutputRecords():
        IORecords.outputRecords = []

    @staticmethod
    def clearAllRecords():
        IORecords.clearInputRecords()
        IORecords.clearOutputRecords()

    @staticmethod
    def getOutputRecords():
        return IORecords.outputRecords

    @staticmethod
    def getOutputRecordsAsString():
        return '\n'.join(IORecords.outputRecords)

    @staticmethod
    def getInputRecords():
        return IORecords.inputRecords

    @staticmethod
    def getInputRecordsAsString():
        return '\n'.join(IORecords.inputRecords)

def constructiveOutput(line: str, end: str = '\n', flush: bool = False):
    IORecords.addOutputRecord(line)
    print(line, end=end, flush=flush)


def constructiveInput(prompt: str) -> str:
    line = input(prompt)
    IORecords.addInputRecord(line)
    return line
