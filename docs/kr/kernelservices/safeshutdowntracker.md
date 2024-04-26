# SafeShutdownTracker 서비스

## 용도
NanoPyOS 의 정상 종료를 추적하기 위한 서비스입니다.<br>
해당 서비스는 매초 현재 시간을 기록하며, 비정상적으로 종료되지 않았을 경우 서비스 재시작시 경고와 함께 이전 종료 시간을 출력합니다.



## configure
`SafeShutdownTracker enabled`: SafeShutdownTracker 서비스를 활성화 합니다.<br>
`SafeShutdownTracker disabled`: SafeShutdownTracker 서비스를 비활성화 합니다.<br>
