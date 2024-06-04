# IOEvent 번들 개발 한국어 문서

## 개발 가이드
CordOS의 입출력 번들 표준은 다음과 같은 규칙을 가집니다:

1. 커널 제공 이벤트 번들은 반드시 `/kernel/events/` 디렉토리에 위치해야 합니다.
2. 제3자 제공 이벤트 번들은 레지스트리 키 `SOFTWARE.CordOS.Events.EventsBundleContainer` 의 리스트 값중 하나에 위치해야 합니다. (권장 기본 위치: `etc/events`)
3. 이벤트 번들은 반드시 `discordui.py` 파일을 포함해야 합니다. (선택사항: Sync Mode 를 지원하기 위해서 `main.py` 를 포함할 수 있습니다.)
4. 이벤트의 종류는 Passive Input, Interactive Input, Output 세 종류가 있습니다.
   1. Passive Input: 입력값이 prefix 인지, CordOS 의 response 값인지 확인하지 않은 이벤트입니다. 이 이벤트는 `{event container}/passive/` 디렉토리에 위치해야 합니다.
   2. Interactive Input: 입력값이 prefix 를 가지고 있고 CordOS 의 response 값이 아닐 경우 발생하는 이벤트입니다. 이 이벤트는 `{event container}/interactive/` 디렉토리에 위치해야 합니다.
   3. Output: 출력 DiscordMessageWrapper 에서 발생하는 출력 이벤트입니다. `message.send()`, `message.reply()` 를 포함한 모든 출력형 함수에 적용되어있습니다. 이 이벤트는 `{event container}/output/` 디렉토리에 위치해야 합니다.
   4. Output Reply: `message.reply()` 함수가 실행될 때 발생하는 이벤트입니다. 이 이벤트는 `{event container}/output/reply/` 디렉토리에 위치해야 합니다.
   5. Output Send: `message.send()` 함수가 실행될 때 발생하는 이벤트입니다. 이 이벤트는 `{event container}/output/send/` 디렉토리에 위치해야 합니다. 
5. `discordui.py`: 이벤트가 실행될 때 호출되는 파일이며, 호출되는 대상은 다음과 같습니다.
   1. `async def mainAsync(message: DiscordMessageWrapper)` 를 호출합니다.
6. 선택사항: `main.py`: Sync Mode 를 지원하기 위해 포함되는 파일이며, 호출되는 대상은 다음과 같습니다.
   1. `def main(message: str)` 를 호출합니다.

## 개발 예시
discordui.py (Function 구조)

```python
from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper


async def mainAsync(message: DiscordMessageWrapper):
   await message.reply("Hello, world!")
```
 
main.py (Function 구조)
```python
def main(message: str):
    return "Hello, world!"
```
