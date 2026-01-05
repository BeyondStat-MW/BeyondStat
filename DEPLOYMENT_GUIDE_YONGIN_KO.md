# 용인 FC 대시보드 배포 가이드 (기존 앱 업데이트)

이미 운영 중인 **BeyondStat 메인 앱**에 **Yongin FC 페이지를 추가**하는 절차입니다. 앱을 새로 만들 필요 없이, 기존 앱 설정을 업데이트하면 됩니다.

## 1. Secrets (환경 변수) 추가 설정 [가장 중요]
기존 앱이 Yongin FC 데이터에 접근할 수 있도록 보안 키를 추가해야 합니다.

1.  **키 텍스트 생성**: 로컬 터미널에서 아래 명령어를 실행하세요.
    ```bash
    python generate_toml.py
    ```
2.  **텍스트 복사**: 결과 내용 중 `[yongin_service_account]`로 시작하는 부분부터 끝까지 복사합니다.
3.  **Streamlit Cloud 접속**:
    *   [Streamlit Cloud](https://share.streamlit.io/)에 로그인합니다.
    *   운영 중인 **기존 앱**의 'Settings' (점 세 개 버튼) -> **"Settings"** -> **"Secrets"**를 클릭합니다.
4.  **붙여넣기 및 저장**:
    *   기존에 입력된 내용 **맨 아래쪽**에 복사한 내용을 붙여넣으세요.
    *   (주의: 기존 내용을 지우지 말고 추가해야 합니다!)
    *   **"Save"** 버튼을 누릅니다.

## 2. 코드 업데이트 (배포 트리거)
변경된 코드를 GitHub에 올리면 Streamlit Cloud가 자동으로 감지하여 재배포합니다.

터미널에서 아래 명령어를 순서대로 입력하세요:
```bash
git add .
git commit -m "Yongin FC 페이지 추가 및 배포"
git push origin main
```

## 3. 확인
1.  잠시 후(약 1~2분) Streamlit Cloud 앱이 자동으로 재부팅됩니다.
2.  앱에 접속하여 사이드바 또는 메인 화면에 **"Yongin FC"** 메뉴가 생겼는지 확인합니다.
3.  해당 메뉴로 들어가서 데이터가 정상적으로 뜨는지 확인합니다.
