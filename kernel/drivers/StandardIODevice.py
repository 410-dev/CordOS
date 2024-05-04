def stdio_input(prompt: str) -> str:
    return input(prompt)


def stdio_output(string: str, end: str = '\n', flush: bool = False):
    print(string, end=end, flush=flush)
