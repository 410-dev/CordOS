import kernel.journaling as Journaling

import asyncio
import random
import string


def runAsync(asyncFunction: callable, identifier: str = "".join(random.choices(string.ascii_letters + string.digits, k=8))) -> None:
    Journaling.record("INFO", f"[{identifier}] Running async function")

    async def wrapper():
        try:
            Journaling.record("INFO", f"[{identifier}] Wrapper start!")
            await asyncFunction()
            Journaling.record("INFO", f"[{identifier}] Wrapper end!")
        except Exception as e:
            Journaling.record("ERROR", f"[{identifier}] Error in async function: {e}")
            raise e

    try:
        Journaling.record("INFO", f"[{identifier}] Getting event loop")
        try:
            loop = asyncio.get_event_loop()
            Journaling.record("INFO", f"[{identifier}] Event loop obtained")
        except RuntimeError as e:
            if "There is no current event loop in thread" in str(e):
                Journaling.record("INFO", f"[{identifier}] No event loop, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                Journaling.record("INFO", f"[{identifier}] New event loop created and set")
            else:
                raise e

        if loop.is_running():
            Journaling.record("INFO", f"[{identifier}] Event loop is running, creating task")
            loop.create_task(wrapper())
            Journaling.record("INFO", f"[{identifier}] Task created")
        else:
            Journaling.record("INFO", f"[{identifier}] Event loop is not running, running until complete")
            loop.run_until_complete(loop.create_task(wrapper()))
            Journaling.record("INFO", f"[{identifier}] Event loop completed")

        Journaling.record("INFO", f"Function completed (identifier: {identifier})")
    except Exception as e:
        Journaling.record("ERROR", f"[{identifier}] Error in async function: {e}")
        raise e
