# Registries 한국어 문서
이 문서에서는 기본 레지스트리와 시스템이 읽어들이는 모든 레지스트리에 대해 서술한 문서이며, 일부 정보는 업데이트 되지 않았을 수 있습니다.

## 기본 레지스트리
| 레지스트리                                                    | 유형 | 기본값 | Fix-On-Boot | 설명 |
|----------------------------------------------------------| --- | --- | --- | --- |
| SOFTWARE.CordOS.Kernel.Signals.Shutdown                  | String | SIGTERM | Yes | 시스템을 종료하는 데 사용되는 시그널 문자열입니다. |
| SOFTWARE.CordOS.Kernel.Programs.Paths                    | List | {"data": ["kernel/commands/", "commands/"]} | No | 실행 가능한 프로그램이 위치한 경로의 목록입니다. |
| SOFTWARE.CordOS.Kernel.Signals.Restart                   | String | SIGRESTART | Yes | 시스템을 다시 시작하는 데 사용되는 시그널 문자열입니다. |
| SOFTWARE.CordOS.Kernel.Programs.OthersEnabled            | Binary Integer | 1 | No | 커널 범위 외의 이진 파일이 실행될 수 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Enabled                  | Binary Integer | 1 | No | 커널에서 서비스가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.SafeModeServices         | String | power, | No | 안전 모드에서 활성화될 수 있는 서비스의 쉼표로 구분된 목록입니다. |
| SOFTWARE.CordOS.Kernel.Services.OthersEnabled            | Binary Integer | 1 | No | 커널 범위 외의 서비스가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.OtherServices            | String | data/services | No | 커널 범위 외의 서비스가 위치한 디렉토리의 경로입니다. |
| SOFTWARE.CordOS.Kernel.Services.SDKMinimum               | Integer | 1 | Yes | 커널 서비스에서 지원하는 최소 SDK 버전입니다. |
| SOFTWARE.CordOS.Kernel.Services.SDKMaximum               | Integer | 2 | Yes | 커널 서비스에서 지원하는 최대 SDK 버전입니다. |
| SOFTWARE.CordOS.Kernel.Services.ReloadOnCall             | Binary Integer | 1 | No | SDK 호출시 서비스를 다시로드할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.Enabled          | Binary Integer | 1 | No | 웹훅이 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.ReloadOnCall     | Binary Integer | 1 | No | SDK 호출시 웹훅을 다시로드할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.Interval         | Binary Integer | 1 | No | 웹훅의 시간 동기화가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.EnableLogging    | Binary Integer | 1 | No | 웹훅의 로깅이 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.LibraryPath      | String | data/files/webhooks/\<id> | No | 웹훅 라이브러리의 경로입니다. |
| SOFTWARE.CordOS.Kernel.Services.Webhook.RegistrationPath | String | data/webhooks | No | 웹훅 등록 디렉토리의 경로입니다. |
| SOFTWARE.CordOS.Kernel.Hooks.Enabled                     | Binary Integer | 1 | No | 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Hooks.OthersEnabled               | Binary Integer | 1 | No | 커널 범위 외의 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.ReloadOnCall                      | Binary Integer | 1 | No | SDK 호출시 커널을 다시로드할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.PrintTraceback                    | Binary Integer | 1 | No | 트레이스백을 인쇄할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.PrintLogs                         | Binary Integer | 1 | No | 로그를 인쇄할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.PrintErrors                       | Binary Integer | 1 | No | 오류를 인쇄할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Kernel.Profiles.Foundation               | String | cordOS | Yes | cordOS의 기반 프로필입니다. |
| SOFTWARE.CordOS.Kernel.Profiles.Version                  | Float | 1.0 | Yes | cordOS 프로필의 버전입니다. |
| SOFTWARE.CordOS.Kernel.Profiles.BotName                  | String | cordOS Bot | Yes | cordOS를 사용하는 봇의 이름입니다. |
| SOFTWARE.CordOS.Kernel.Profiles.BotVersion               | String | 1.0rc-2 | Yes | cordOS를 사용하는 봇의 버전입니다. |
| SOFTWARE.CordOS.Events.Inbound.CommandHooks.Enabled      | Binary Integer | 0 | No | 입력 이벤트에 대한 명령 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Inbound.CommandHooks.Loaded       | List | [] | No | 입력 이벤트에 대한 로드된 명령 후크 목록입니다. |
| SOFTWARE.CordOS.Events.Inbound.Hooks.Enabled             | Binary Integer | 0 | No | 입력 이벤트에 대한 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Inbound.Hooks.Loaded              | List | [] | No | 입력 이벤트에 대한 로드된 후크 목록입니다. |
| SOFTWARE.CordOS.Events.Inbound.PrintMessage              | Binary Integer | 1 | No | 수신된 메시지를 인쇄할지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Inbound.PrintMessageFormat        | String | Message from $uname in $serverid ($servername): $message | No | 수신된 메시지의 인쇄 형식입니다. |
| SOFTWARE.CordOS.Events.Outbound.CommandHooks.Enabled     | Binary Integer | 0 | No | 출력 이벤트에 대한 명령 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Outbound.CommandHooks.Loaded      | List | [] | No | 출력 이벤트에 대한 로드된 명령 후크 목록입니다. |
| SOFTWARE.CordOS.Events.Outbound.Hooks.Enabled            | Binary Integer | 0 | No | 출력 이벤트에 대한 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Outbound.Hooks.Loaded             | List | [] | No | 출력 이벤트에 대한 로드된 후크 목록입니다. |
| SOFTWARE.CordOS.Events.Boot.Hooks.Enabled                | Binary Integer | 0 | No | 부팅 이벤트에 대한 후크가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Boot.Hooks.Loaded                 | List | [] | No | 부팅 이벤트에 대한 로드된 후크 목록입니다. |
| SOFTWARE.CordOS.Events.Boot.Broadcast.Enabled            | Binary Integer | 0 | No | 부팅 이벤트에 대한 브로드캐스트가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |
| SOFTWARE.CordOS.Events.Boot.Broadcast.Message            | String |  | No | 부팅 이벤트 중 브로드캐스트할 메시지입니다. |
| SOFTWARE.CordOS.Events.Boot.Broadcast.Blacklist          | List | [] | No | 부팅 이벤트 중 브로드캐스트할 항목의 블랙리스트입니다. |
| SOFTWARE.CordOS.Config.Core.Prefix                       | String | . | No | cordOS 명령어 트리고 접두사입니다. |
| SOFTWARE.CordOS.Security.Definitions.unavailable         | Integer | 1 | No | "사용 불가" 사용자의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Definitions.user                | Integer | 2 | No | 일반 사용자의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Definitions.mod                 | Integer | 3 | No | 모더레이터의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Definitions.admin               | Integer | 4 | No | 관리자의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Definitions.root                | Integer | 5 | No | 루트 사용자의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Definitions.developer           | Integer | 5 | No | 개발자의 보안 수준 정의입니다. |
| SOFTWARE.CordOS.Security.Permissions.Definitions.DEFAULT | String | unavailable | No | 기본 권한 수준이며 일반적으로 unavailable 을 기본값으로 가집니다. |
| SOFTWARE.CordOS.Security.Config                          | String | root | No | 보안에 대한 구성입니다. |
| SOFTWARE.CordOS.Security.Install                         | String | admin | No | 설치에 대한 권한입니다. |
| SOFTWARE.CordOS.Security.Registry                        | String | root | No | 레지스트리에 대한 권한입니다. |
| SOFTWARE.CordOS.Security.Tags                            | String | admin | No | 태그에 대한 권한입니다. |
| SOFTWARE.CordOS.Security.Services                        | String | root | No | 서비스에 대한 권한입니다. |
| SOFTWARE.CordOS.Debug                                    | Binary Integer | 0 | No | 디버그 모드가 활성화되어 있는지 여부를 나타내는 이진 (참=1 또는 거짓=0) 값입니다. |



## 시스템 참조 레지스트리

| 레지스트리                              | 유형   | 기본값     | 설명     |
| --------------------------------------- | ------ |---------| -------- |
| SOFTWARE.CordOS.Kernel.Signals.Shutdown | String | SIGTERM | 시스템을 |
| SOFTWARE.CordOS.Kernel.Services.OtherServicesMinimumBootStage | Integer | 3       | 커널 범위 외의 서비스가 부팅 중에 로드되는 최소 단계입니다. |