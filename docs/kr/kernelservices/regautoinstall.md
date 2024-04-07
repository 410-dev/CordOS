# RegAutoInstall 서비스

## 용도
CordOS 기반 시스템에서 커스텀 레지스트리를 자동등록 하기 위해 사용되는 서비스입니다.<br>
부트 단계에서 레지스트리를 읽어들여 등록합니다.<br>
서비스가 읽어들이는 레지스트리 파일 위치는 `/AUTOREGINST` 와 `/PERSISTAUTOREGINST` 디렉토리 내부의 .cordreg 파일 입니다. <br>
`/AUTOREGINST`: 레지스트리 파일이 등록된 후 삭제됩니다.<br>
`/PERSISTAUTOREGINST`: 레지스트리 파일이 등록된 후 삭제되지 않습니다. 매 부팅마다 등록됩니다.<br>
레지스트리 파일 작성 방법은 [레지스트리](../developerguide/RegistryFile.md) 문서를 참조하세요.



## configure
이 서비스는 설정을 지원하지 않습니다.
