# Webhook 서비스

## 용도
CordOS 에서 Webhook 을 활용하는 백그라운드 작업을 관리하는 서비스입니다.<br>
백그라운드 이벤트가 발생할 경우 Webhook 을 통해 Discord Webhook 으로 메시지를 전송하거나, 타 http 서버로 요청을 전송할 수 있습니다.<br>
예를 들어, 특정한 값이 변경되었거나 조건이 충족되었다면 `await message.reply()` 없이 Discord Webhook 을 통해 알릴 수 있습니다.<br>


## Webhook 백그라운드 작업 제작 방법
Webhook 백그라운드 작업 파일은 간단한 python 스크립트입니다.<br>
아래는 Webhook 백그라운드 작업 파일의 예시입니다.
```python
import kernel.services.DiscordUIService.webhook as Webhook # 웹훅 모듈을 불러옵니다.

# 라이브러리 위치를 인자로 받는 main 함수를 정의합니다. 이 함수는 매초마다 비동기적으로 실행됩니다.
def main(library: str):
    urls: list = Webhook.getLinkages("mywebhook") # 해당 웹훅에 연동된 URL 을 모두 불러옵니다.
    for url in urls:
        Webhook.send(url, "Hello, World!") # 해당 URL 로 "Hello, World!" 라는 메시지를 전송합니다.
```
위와 같은 스크립트를 작성한 후, 해당 스크립트를 웹훅 등록 위치 (기본값: storage/webhooks) 에 저장합니다.<br>


## configure
`webhook link <url> <webhookid>`: 지정된 웹훅에 웹훅 URL 을 연동합니다.<br>
`webhook unlink <url> <webhookid>`: 지정된 웹훅에 연동된 웹훅 URL 을 제거합니다.<br>
`webhook list`: 등록된 웹훅을 출력합니다.<br>


## 레지스트리
| 키 이름                                                       | 기본 값                  | 설명                         |
|------------------------------------------------------------|-----------------------|----------------------------|
| `SOFTWARE.CordOS.Kernel.Services.Webhook.RegistrationPath` | storage/webhooks      | 웹훅 스크립트 등록 위치              |
| `SOFTWARE.CordOS.Kernel.Services.Webhook.LibraryPath`      | storage/webhooks/<id\> | 웹훅 스크립트가 사용 가능한 전용 스토리지 위치 |
| `SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled`          | 1                     | 웹훅 서비스 활성화 여부              |
| `SOFTWARE.CordOS.Kernel.Services.Webhook.ReloadOnCall`     | 1                     | 웹훅 스크립트 실행시 리로드 여부         |
| `SOFTWARE.CordOS.Kernel.Services.Webhook.Interval`         | 1                     | 웹훅 스크립트 반복 간격 (초)          |
| `SOFTWARE.CordOS.Kernel.Services.Webhook.EnableLogging`    | 1                     | 웹훅 실행 로그 출력 여부             |

