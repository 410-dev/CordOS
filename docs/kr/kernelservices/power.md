# Power 서비스

## 용도
CordOS 의 전원 관리 서비스입니다. 이 서비스의 설정을 활용하여 CordOS 를 종료하거나 재시동 할 수 있습니다.

## configure
`power off`: 시스템 종료를 시도하며 모든 서비스가 종료될 때 까지 대기합니다.<br>
`power reboot`: 시스템 재시동을 시도하며 모든 서비스가 종료된 후 재시동 합니다.<br>
`power halt`: 시스템을 강제로 정지합니다. 이 때 확인 절차로 동일한 명령어를 한번 더 입력해야 합니다.<br>
`power reset`: 시스템을 강제로 재시동합니다. 이 때 확인 절차로 동일한 명령어를 한번 더 입력해야 합니다.<br>
`power halt-cancel`: 시스템 강제 정지 확인 절차를 취소합니다.<br>
`power reset-cancel`: 시스템 강제 재시동 확인 절차를 취소합니다.<br>

## IPC
| 키 이름                          | 기본 값 | 설정 가능한 값     | 설명               |
|-------------------------------|------|--------------|------------------|
| `KernelHaltSignal.{User ID}`  | None | 0 / 1        | 시스템 강제 종료 확인 여부  |
| `KernelResetSignal.{User ID}` | None | 0 / 1        | 시스템 강제 재시작 확인 여부 |
| `power.off`                   | None | 0 / 1        | 시스템 종료 예약 여부     |
| `power.off.state`             | None | REBOOT / OFF | 시스템 종료 상태        |

