# Services 한국어 문서

## 개발 가이드
CordOS 의 Service 시스템은 NanoPyOS 표준을 따릅니다. <br> 
CordOS 가 따르는 NanoPyOS 표준은 다음과 같은 규칙을 가집니다:

1. 서비스 번들은 반드시 `/kernel/services/` 디렉토리에 위치해야 합니다.
2. 서비스 번들은 반드시 `configure.py`, `main.py`, `service.json` 파일을 포함해야 합니다.
3. `configure.py`: 사용자 명령어 `servies configure <service> args...` 가 실행되었을 때 호출되는 파일이며, 호출되는 대상은 `async main(args: list, message)` 입니다.
4. `main.py`: CordOS 시동시 비동기적으로 실행됩니다. 호출되는 대상은 `def main()` 입니다.
5. `service.json`: 서비스 실행시 로드되는 서비스 정보 파일입니다. 해당 파일은 다음과 같은 필드를 가져야 합니다:
   1. `api`: 정수형 - 사용되는 커널 API 버전입니다. 호환 값은 레지스트리의 `SOFTWARE.CordOS.Kernel.Services.APIMinimum` 과 `SOFTWARE.CordOS.Kernel.Services.APIMaximum` 의 사잇값이여야 합니다.
   2. `stage`: 정수형 (0-3) - 서비스가 실행될 시점을 지정합니다. 각 숫자의 시점은 다음과 같습니다.
      1. Stage 0: 부트로더와 프리로딩이 정상 실행 후, `system.py` 가 로드될 때 실행합니다.
      2. Stage 1: Stage 0 이후 `kernel.clock` 과 `kernel.ipc` 가 순차적으로 초기화 된 후 실행합니다.
      3. Stage 2: `data/config.json` 가 로드되고 최소한의 레지스트리를 불러옵니다. 이후 Discord 클라이언트를 초기화 한 후 실행됩니다.
      4. Stage 3 (권장): Discord 이벤트 리스너 및 최소한의 기초 함수들이 초기화/등록 된 후 실행합니다. 중요한 초기화 단계의 서비스가 아니라면 실행 단계를 3으로 설정하는 것을 권장합니다.
   3. `name`: Alphanumeric 문자열: 서비스의 이름이며 공백을 포함한 특수문자는 허용되지 않습니다.



## 레지스트리 엑세스

CordOS 및 NanoPyOS 는 기본적으로 레지스트리 완전 접근을 허용하나, 필요하지 않을 경우 권장하지 않습니다. 기본적으로 제공되는 레지스트리 스코프는 다음과 같습니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}` 및 모든 하위 키: 읽기 및 쓰기

`kernel.servicectl` 에 의해 실행될 경우 다음과 같은 값은 자동으로 생성됩니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.Enabled`: 기본값 1

`kernel.servicectl` 은 다음과 같은 값을 인식합니다:

1. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.Enabled`: 이진정수 (0 혹은 1) - 0일 경우 서비스를 실행하지 않음.
2. `SOFTWARE.CordOS.Kernel.Services.{서비스 이름}.ReloadOnCall`: 이진정수 (0 혹은 1) - 0일 경우 로드시 서비스를 갱신하지 않음

