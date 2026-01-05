# 용인 FC 대시보드 배포 가이드 (Deployment Guide)

본 문서는 **Yongin FC 대시보드**를 Streamlit Cloud에 배포하기 위한 단계별 가이드입니다. 강원 FC 배포 방식과 동일한 절차를 따릅니다.

## 1. 사전 준비 (Prerequisites)
*   **GitHub 저장소**: 코드가 GitHub에 업로드되어 있어야 합니다. (현재 로컬 작업을 Commit & Push 필요)
*   **Streamlit Cloud 계정**: GitHub 계정과 연동된 Streamlit Cloud 계정이 필요합니다.
*   **GCP 서비스 키**: `yongin_fc/yongin-key.json` 파일이 로컬에 존재해야 합니다. (Secrets 생성용)

## 2. GitHub 코드 업로드
터미널에서 변경 사항을 모두 커밋하고 원격 저장소로 업로드합니다.
```bash
git add .
git commit -m "Yongin FC Dashboard Release v1.0"
git push origin main
```

## 3. Streamlit Cloud 앱 생성
1.  [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 로그인합니다.
2.  **"New app"** 버튼을 클릭합니다.
3.  **"Use existing repo"**를 선택합니다.
4.  다음 정보를 입력합니다:
    *   **Repository**: 배포할 GitHub 저장소를 선택합니다.
    *   **Branch**: `main` (또는 작업 중인 브랜치)
    *   **Main file path**: `Home.py`
        *   *주의: `pages/4_Yongin_FC.py`가 아닌 메인 진입점 `Home.py`를 선택해야 합니다. 통합 로그인/게이트키퍼가 여기서 작동합니다.*

## 4. Secrets (환경 변수) 설정 [가장 중요]
보안을 위해 GCP 서비스 계정 키(`yongin-key.json`) 파일은 GitHub에 업로드되지 않습니다. 대신 Streamlit Cloud의 **Secrets** 기능을 통해 직접 주입해야 합니다.

### 4.1 Secrets 생성 스크립트 실행
로컬 터미널에서 아래 스크립트를 실행하여 Secrets에 넣을 텍스트를 자동 생성합니다.
```bash
python generate_toml.py
```

### 4.2 Secrets 복사 및 붙여넣기
1.  스크립트 실행 결과 중 `[yongin_service_account]` 섹션을 복사합니다. (아래 예시)
    ```toml
    [yongin_service_account]
    type = "service_account"
    project_id = "yonginfc"
    private_key_id = "..."
    private_key = """-----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----"""
    client_email = "..."
    ...
    ```
2.  Streamlit Cloud의 앱 설정 화면에서 **"Advanced settings"** -> **"Secrets"** 영역을 엽니다.
3.  복사한 내용을 붙여넣습니다. (기존에 다른 섹션이 있다면 그 아래에 이어 붙입니다.)
4.  **"Save"**를 클릭합니다.

## 5. 배포 완료 및 접속 테스트
1.  **"Deploy!"** 버튼을 클릭합니다.
2.  배포가 완료될 때까지 기다립니다 (약 2-3분 소요).
3.  배포된 URL에 접속하여 기능이 정상 작동하는지 확인합니다.
4.  **로그인 테스트**:
    *   Yongin FC 계정으로 로그인을 시도합니다. (로컬 테스트 시 사용한 계정 정보 확인)
    *   팀 대시보드, 선수 상세, 인사이트 탭이 정상적으로 로딩되는지 확인합니다.

---
**문의**: 배포 중 오류 발생 시 에러 로그를 캡처하여 전달해 주세요.
