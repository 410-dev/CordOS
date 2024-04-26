# 서비스 번들 개발 한국어 문서

## 개발 가이드
CordOS의 서비스 번들 표준은 다음과 같은 규칙을 가집니다:

1. 커널 서비스 번들은 반드시 `/kernel/services/` 디렉토리에 위치해야 합니다.
2. 제3자 제공 서비스 번들은 레지스트리 키 `SOFTWARE.CordOS.Kernel.Services.OtherServices` 의 값에 해당하는 위치에 위치해야 합니다. (기본값: `/data/services`)
3. 서비스 번들은 반드시 `configure.py`, `main.py`, `service.json` 파일을 포함해야 합니다.
4. `configure.py`: 사용자 명령어 `servies configure <service> args...` 가 실행되었을 때 호출되는 파일이며, 호출되는 대상은 `async main(args: list, message: DiscordMessageWrapper)` 입니다.
5. `main.py`: CordOS 시동시 비동기적으로 실행됩니다. 호출되는 대상은 `def main()` 입니다.
6. `service.json`: 서비스 실행시 로드되는 서비스 정보 파일입니다. 해당 파일은 다음과 같은 필드를 가져야 합니다:
   1. `sdk` [SDKv1+]: 정수형 - 사용되는 커널 SDK 버전입니다. 호환 값은 레지스트리의 `SOFTWARE.CordOS.Kernel.Services.SDKMinimum` 과 `SOFTWARE.CordOS.Kernel.Services.SDKMaximum` 의 사잇값이여야 합니다.
   2. `stage` [SDKv1+]: 정수형 (0-3) - 서비스가 실행될 시점을 지정합니다. 각 숫자의 시점은 다음과 같습니다.
      1. Stage 0: 부트로더와 프리로딩이 정상 실행 후, `system.py` 가 로드될 때 실행합니다.
      2. Stage 1: Stage 0 이후 `kernel.clock` 과 `kernel.ipc` 가 순차적으로 초기화 된 후 실행합니다.
      3. Stage 2: `data/config.json` 가 로드되고 최소한의 레지스트리를 불러옵니다. 이후 Discord 클라이언트를 초기화 한 후 실행됩니다.
      4. Stage 3 (권장): Discord 이벤트 리스너 및 최소한의 기초 함수들이 초기화/등록 된 후 실행합니다. 중요한 초기화 단계의 서비스가 아니라면 실행 단계를 3으로 설정하는 것을 권장합니다.
   3. `name` [SDKv1+]: Alphanumeric 문자열: 서비스의 이름이며 공백을 포함한 특수문자는 허용되지 않습니다.
   4. `sync` [SDKv1+]: Boolean (true 혹은 false) - true 일 경우, 서비스가 동기적으로 실행됩니다. 기본값은 false입니다. 동기적으로 실행 될 경우 부트 프로세스가 해당 서비스의 실행이 완료될 때까지 대기합니다.
   5. `role` [SDKv1+]: 문자열 - 서비스의 역할을 지정합니다. 이는 동일한 역할을 하는 서비스가 중복적으로 로드되는 현상을 막기 위해 사용됩니다. 예를 들어, `critical.unique.shell` 로 설정된 서비스는 시스템의 셸 기능을 담당하며 동일한 역할을 가진 다른 서비스는 로드되지 않습니다. `role` 값이 `critical.unique.***` 로 시작한다면 해당 역할의 서비스는 중복 로드되지 않습니다.
   6. `id` [SDKv1+]: 문자열 - 서비스의 고유 식별자입니다. 이 값은 서비스의 고유성을 보장합니다.

## 개발 예시
configure.py
```python
import kernel.registry as Registry
from objects.discordmessage import DiscordMessageWrapper

# 이 함수는 사용자 명령어 `services configure <service> args...` 가 실행되었을 때 호출됩니다.
async def mainAsync(args: list, message: DiscordMessageWrapper):
   
    # 명령어가 올바르게 입력되었는지 확인합니다.
    if len(args) < 2:
        await message.reply("Usage: servicename <configurename> <value>")
        return
    
    # 첫번째 인자가 keyname 일 경우, 레지스트리에 값을 쓰고 응답합니다.
    if args[0] == "keyname":
       Registry.write("REGKEY", args[1])
       await message.reply("Key set to " + args[1])
    else:
        await message.reply("Invalid configure key")
```

main.py
```python
def main():
    while True:
        # 백그라운드에서 실행될 코드를 작성합니다.
        pass
```

service.json
```json
{
    "id": "com.example.servicename",
    "role": "critical",
    "name": "example",
    "sdk": 2,
    "stage": 3,
    "sync": false
}
```


## 레지스트리 엑세스

CordOS 및 NanoPyOS 는 기본적으로 레지스트리 완전 접근을 허용하나, 필요하지 않을 경우 권장하지 않습니다. 기본적으로 제공되는 레지스트리 스코프는 다음과 같습니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}` 및 모든 하위 키: 읽기 및 쓰기

`kernel.servicectl` 에 의해 실행될 경우 다음과 같은 값은 자동으로 생성됩니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.Enabled`: 기본값 1

`kernel.servicectl` 은 다음과 같은 값을 인식합니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.Enabled`: 이진정수 (0 혹은 1) - 0일 경우 서비스를 실행하지 않음.
2. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.ReloadOnCall`: 이진정수 (0 혹은 1) - 0일 경우 로드시 서비스를 갱신하지 않음

