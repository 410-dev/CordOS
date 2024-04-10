# IOEvent 번들 개발 한국어 문서

## 개발 가이드
CordOS의 입출력 번들 표준은 다음과 같은 규칙을 가집니다:

1. 커널 제공 이벤트 번들은 반드시 `/kernel/events/` 디렉토리에 위치해야 합니다.
2. 제3자 제공 이벤트 번들은 레지스트리 키 `SOFTWARE.CordOS.Events.EventsBundleContainer` 의 리스트 값중 하나에 위치해야 합니다. (권장 기본 위치: `data/events`)
3. 이벤트 번들은 반드시 `main.py` 파일을 포함해야 합니다.
4. 이벤트의 종류는 Passive Input, Interactive Input, Output 세 종류가 있습니다.
   1. Passive Input: 입력값이 prefix 인지, CordOS 의 response 값인지 확인하지 않은 이벤트입니다. 이 이벤트는 `{event container}/passive/` 디렉토리에 위치해야 합니다.
   2. Interactive Input: 입력값이 prefix 를 가지고 있고 CordOS 의 response 값이 아닐 경우 발생하는 이벤트입니다. 이 이벤트는 `{event container}/interactive/` 디렉토리에 위치해야 합니다.
   3. Output: 출력값을 전달할 때 발생하는 이벤트입니다. ***(미구현)***
5. `main.py`: 이벤트가 실행될 때 호출되는 파일이며, 호출되는 대상은 다음과 같습니다.
   1. `async def main(message)` 를 호출합니다.

## 개발 예시
main.py (Function 구조)
```python
async def main(message):
   await message.reply("Hello, world!")
```