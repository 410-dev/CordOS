# Registry 파일
핵심 레지스트리가 부트 단계에서 고쳐지기 위해 사용되는 파일입니다.
기본으로 설치되는 레지스트리 파일은 다음과 같습니다.<br>
`defaults/registry.cordreg`<br>
<br>
제3자 제공 레지스트리 파일은 [regautoinstall](../kernelservices/regautoinstall.md) 서비스 문서를 따르십시오.<br><br>
## 레지스트리 파일 구조
레지스트리 파일은 다음과 같은 구조로 되어 있습니다.<br>
```
# Comment
key1=value1
?optionalkey1=value1
```

각 줄은 다음을 의미합니다
- `#`로 시작하는 줄은 주석입니다. 주석은 무시됩니다. In-line 주석은 지원되지 않으므로 주석은 별도의 줄에 작성되어야 합니다.
- `key=value` 형식의 줄은 레지스트리 키와 값을 정의합니다. 이는 레지스트리 파일이 로드될 때 반드시 덮어씌워집니다.
- `?optionalkey=value` 형식의 줄은 레지스트리 키와 값을 정의합니다. 레지스트리에 키가 존재하지 않으면 새로 생성합니다.

