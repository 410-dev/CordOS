# IOEventsManager 서비스

## 용도
CordOS 의 메시지 입출력의 이벤트를 관리하는 서비스입니다. 이벤트 발생시 실행할 코드를 등록할 수 있습니다.<br>
이벤트 번들 제작 방법은 [개발 가이드](../developerguide/IOEventBundle.md)를 참조하세요.

## 입출력 종류
- Passive Input: 입력값이 prefix 인지, CordOS 의 response 값인지 확인하지 않은 이벤트입니다. 
- Interactive Input: 입력값이 prefix 를 가지고 있고 CordOS 의 response 값이 아닐 경우 발생하는 이벤트입니다.
- Output: 출력 DiscordMessageWrapper 에서 발생하는 출력 이벤트입니다. 모든 출력형 함수에 적용되어있습니다.
- Output Reply: `message.reply()` 함수가 실행될 때 발생하는 이벤트입니다.
- Output Send: `message.send()` 함수가 실행될 때 발생하는 이벤트입니다.

## configure
`ioeventsmgr list`: 현재 등록된 이벤트 목록을 출력합니다.<br>
`ioeventsmgr disable <event name>`: 이벤트를 비활성화 합니다.<br>
`ioeventsmgr enable <event name>`: 이벤트를 활성화 합니다.<br>
`ioeventsmgr remove <event name>`: 이벤트를 제거합니다.<br>


## 레지스트리
| 키 이름                                                      | 기본 값                    | 설명                               |
|-----------------------------------------------------------|-------------------------|----------------------------------|
| `SOFTWARE.CordOS.Kernel.Services.ioeventsmgr.Print`       | 0                       | 이벤트 로드 과정의 로그 출력                 |
| `SOFTWARE.CordOS.Events.Kernel.InboundPassiveEnabled`     | 1                       | 커널의 Passive Input 이벤트 활성화 여부     |
| `SOFTWARE.CordOS.Events.Kernel.InboundInteractiveEnabled` | 1                       | 커널의 Interactive Input 이벤트 활성화 여부 |
| `SOFTWARE.CordOS.Events.Kernel.OutboundReplyEnabled`      | 0                       | 커널의 Reply 이벤트 활성화 여부             |
| `SOFTWARE.CordOS.Events.Kernel.OutboundSendEnabled`       | 0                       | 커널의 Send 이벤트 활성화 여부              |
| `SOFTWARE.CordOS.Events.Kernel.OutboundGlobalEnabled`     | 1                       | 커널의 Global 이벤트 활성화 여부            |
| `SOFTWARE.CordOS.Events.User.InboundPassiveEnabled`       | 1                       | 사용자의 Passive Input 이벤트 활성화 여부    |
| `SOFTWARE.CordOS.Events.User.InboundInteractiveEnabled`   | 1                       | 사용자의 Interactive Input 이벤트 활성화 여부 |
| `SOFTWARE.CordOS.Events.User.OutboundReplyEnabled`        | 0                       | 사용자의 Reply 이벤트 활성화 여부            |
| `SOFTWARE.CordOS.Events.User.OutboundSendEnabled`         | 0                       | 사용자의 Send 이벤트 활성화 여부             |
| `SOFTWARE.CordOS.Events.User.OutboundGlobalEnabled`       | 1                       | 사용자의 Global 이벤트 활성화 여부           |
| `SOFTWARE.CordOS.Events.EventsBundleContainer`            | `data/events/, events/` | 사용자 이벤트 번들 디렉토리 경로               |

