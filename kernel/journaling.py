import datetime
import traceback
def addJournal(text: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = traceback.extract_stack(None, 2)[0]
    print(f"[{timestamp}] {caller.filename} - {text}")