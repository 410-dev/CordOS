# Versioning 서비스

## 용도
CordOS 의 버전 관리를 위한 서비스입니다. 최신 버전 확인 혹은 업데이트를 담당합니다.<br>
서비스 로드시 업데이트가 준비된 상태라면 업데이트 파일을 적용합니다.


## configure
`versioning upgrade`: 최신 버전으로 업데이트를 시도합니다. 이미 최신 버전일 경우, `--reinstall` 플래그를 추가하여 새 이미지 파일로 덮어씌울 수 있습니다.<br>
`versioning latest` : 최신 버전을 확인합니다.<br>
`versioning branch` : 현재 브랜치를 확인합니다.<br>


## 레지스트리
| 키 이름                                                     | 기본 값                                                                                 | 설명                                           |
|----------------------------------------------------------|--------------------------------------------------------------------------------------|----------------------------------------------|
| `SOFTWARE.CordOS.Kernel.Profiles.Version`                | 현재 시스템 버전                                                                            | 현재 시스템 버전을 문자열로 표시합니다.                       |
| `SOFTWARE.CordOS.Kernel.Profiles.Build`                  | 현재 시스템 빌드 번호                                                                         | 현재 시스템 빌드 번호를 문자열로 표시합니다.                    |
| `SOFTWARE.CordOS.Kernel.Services.versioning.Branch`      | stable                                                                               | 현재 브랜치를 문자열로 표시합니다.                          |
| `SOFTWARE.CordOS.Kernel.Services.versioning.ImageURL`    | https://github.com/410-dev/cordOS/archive/<branch\>.zip                              | 최신 버전의 시스템 이미지를 받을 URL 을 표시합니다.              |
| `SOFTWARE.CordOS.Kernel.Services.versioning.MetaURL`     | https://raw.githubusercontent.com/410-dev/CordOS/<branch\>/defaults/registry.cordreg | 최신 버전의 정보를 불러올 원격 레지스트리 파일을 불러올 URL 을 표시합니다. |
| `SOFTWARE.CordOS.Kernel.Services.versioning.ForceReboot` | 1                                                                                    | 업데이트 준비 완료시 강제 재시동 여부를 표시합니다.                |
| `SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeMode`       | None                                                                                 | 업데이트 파일 압축 해제 위치를 표시합니다.                     |
| `SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue`      | 0                                                                                    | 부팅시에 업데이트 파일을 적용할지에 대한 여부입니다.                |

