# CordOS
Discord 봇을 빠르게 제작하기 위한 프레임워크입니다.

## 시작하기
1. `git clone https://github.com/410-dev/CordOS.git` 로 프로젝트를 다운로드 받습니다.
2. `boot.ps1`, `boot.sh`, `boot.bat` (이하 시동파일) 중 하나를 실행하여 프로젝트를 시작/초기화 합니다.
3. `etc/config.json` 파일의 `token` 값을 자신의 봇 토큰으로 변경합니다.
4. 다시 시동파일을 실행하여 봇을 시작합니다.

## 명령어 추가하기
`storage/commands` 혹은 `/commands` 폴더에 명령어 번들을 집어넣습니다. 명령어 번들 제작 방법은 [여기](docs/kr/developerguide/Commands.md)를 참고하세요.

## 백그라운드 서비스 추가하기
`etc/services` 폴더에 백그라운드 서비스 번들을 집어넣습니다. 백그라운드 서비스 번들 제작 방법은 [여기](docs/kr/developerguide/Services.md)를 참고하세요.

## 문서 읽기
- [한국어 가이드](docs/kr/README.md) (미완)

## 업데이트 브랜치
CordOS 는 다음과 같은 브랜치를 가지고 있습니다.
- `stable`: 안정적인 버전이 배포되는 브랜치입니다. ***현재 CordOS 는 개발 단계이므로 이 브랜치 또한 안정적이지 않을 수 있습니다.***
- `beta`: 안정적인 버전이 배포되기 전에 테스트되는 브랜치입니다. 이 브랜치는 안정적이지 않을 수 있습니다.
- `dev`: 개발에 사용되는 브랜치입니다. 이 브랜치는 실행되지 않을 수 있습니다.
