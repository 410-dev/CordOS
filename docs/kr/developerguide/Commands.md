# 명령어 개발 한국어 문서

## 개발 가이드
CordOS의 명령어 번들 표준은 다음과 같은 규칙을 가집니다:

1. 커널 명령어 번들은 반드시 `/kernel/commands/` 디렉토리에 위치해야 합니다.
2. 제3자 제공 명령어 번들은 레지스트리 키 `SOFTWARE.CordOS.Kernel.Programs.Paths` 의 리스트 값중 하나에 위치해야 합니다. (권장 기본 위치: `/data/commands`)
3. 명령어 번들은 반드시 `main.py`, `manual.txt` 파일을 포함해야 합니다.
4. `manual.txt`: help 명령어가 읽어들이는 매뉴얼 텍스트입니다. 명령어의 사용법과 설명을 포함해야 합니다.
5. `main.py`: 명령어가 실행될 때 호출되는 파일이며, 호출되는 대상은 다음과 같습니다.
   1. **Function 구조**
      1. `async def main(args: list, message)` 를 호출하며, Class 구조보다 하위 우선순위를 가집니다.
      2. *2.0 버전에서 Class 구조보다 높은 실행 우선순위를 가질 예정입니다.*
   2. **Class 구조:**
      1. Class 명은 명령어의 철자가 대문자화 되어야 합니다. 예를 들어, help 명령어의 경우 코드는 다음과 같이 선언합니다: `class Help:`
      2. Class 는 반드시 `__init__(self, args: list, message)` 와 `async exec(self)` 함수를 포함해야 합니다.
      3. `__init__` 함수는 명령어가 호출될 때 인자를 받아들이는 역할을 합니다.
      4. `exec` 함수는 명령어가 실행될 때 호출되는 함수입니다.
      5. *2.0 버전에서 Class 구조는 Function 구조보다 낮은 실행 우선순위를 가질 예정입니다.*

## 개발 예시
main.py (Function 구조)
```python
async def main(args: list, message):
   await message.reply("Hello, world!")
```

main.py (Class 구조)
```python
class Command:
    def __init__(self, args: list, message):
        self.args = args
        self.message = message

    async def exec(self):
        await self.message.reply("Hello, world!")
```

manual.txt
```
Command

이 명령어는 Hello, World! 를 출력합니다.

Usage: command
```
