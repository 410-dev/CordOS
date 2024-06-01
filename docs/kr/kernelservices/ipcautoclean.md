# IPCAutoClean 서비스

## 용도
IPCAutoClean 서비스는 커널 내 IPC 메모리가 과도하게 사용되는 것을 방지하기 위해 IPC 메모리를 주기적으로 정리하는 서비스입니다.
0.5초 주기로 kernel.ipc 모듈의 removeExpired() 를 실행합니다.

## configure
`ipcautoclean enabled`: IPCAutoClean 서비스를 활성화 합니다.<br>
`ipcautoclean disabled`: IPCAutoClean 서비스를 비활성화 합니다.<br>
`ipcautoclean expire=n`: IPC 메모리가 만료되기까지 시간을 설정합니다. (단위: 초)

## 레지스트리
| 키 이름 | 기본 값 | 설명                                     |
| ---- | ---- |----------------------------------------|
| `SOFTWARE.CordOS.Kernel.IPC.EnableAutoCleaner` | 1 | IPCAutoClean 서비스 활성화 여부                |
| `SOFTWARE.CordOS.Kernel.IPC.MemoryLiveTime` | 1800 | IPC 메모리가 만료되기까지 시간 (초) (-1 이면 만료되지 않음) |

