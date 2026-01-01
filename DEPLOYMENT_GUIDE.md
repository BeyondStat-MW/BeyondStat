
# 🚀 통합 대시보드 배포 가이드 (Step-by-Step)

이 가이드를 따라하면 **K-League, 윤청구 센터, 강원 FC**가 모두 포함된 통합 대시보드를 웹사이트로 만들 수 있습니다.

## Q: 기존의 것도 전부 다 올라가나요?
**네, 맞습니다!**
`Home.py`가 메인 대문 역할을 하며, 여기서 K-League(`pages/1_...`), Yoon Center(`pages/2_...`), Gangwon FC(`pages/3_...`)로 각각 이동하는 구조입니다. 이 모든 파일이 하나의 프로젝트 폴더에 있으므로 한 번에 배포됩니다.

---

## 1단계: GitHub 저장소 만들기
Streamlit Cloud는 GitHub에 있는 코드를 가져와서 보여줍니다. 먼저 코드를 GitHub에 올려야 합니다.

1. [GitHub.com](https://github.com/)에 로그인합니다. (계정이 없으면 가입)
2. 우측 상단 `+` 버튼을 누르고 **New repository**를 클릭합니다.
3. **Repository name**에 `beyondstat-portal` (또는 원하는 이름)을 입력합니다.
4. **Public** (공개) 또는 **Private** (비공개) 중 선택합니다. 
   - *팁: 데이터 보안을 위해 **Private**을 추천합니다.*
5. **Create repository** 버튼을 클릭합니다.

## 2단계: 코드 업로드하기 (가장 쉬운 방법)
초보자에게 가장 쉬운 '웹 업로드' 방식을 안내해 드립니다. (Git 명령어를 아신다면 터미널에서 `git push` 하셔도 됩니다.)

1. 방금 만든 GitHub 저장소 화면에서 파란색 글씨의 **uploading an existing file** 링크를 찾거나, **Add file > Upload files** 버튼을 누릅니다.
2. 로컬 컴퓨터의 프로젝트 폴더(`beyondstat_dashboard`) 안에 있는 **모든 파일과 폴더**를 드래그해서 GitHub 웹페이지에 놓습니다.
   - **주의**: `gangwon-key.json` 같은 **보안 키 파일은 올리지 마세요!** (나중에 따로 설정합니다.)
   - 반드시 포함되어야 할 것들:
     - `Home.py`
     - `pages/` 폴더 전체
     - `gangwon_fc/` 폴더 전체
     - `utils/` 폴더 전체
     - `requirements.txt`
3. 파일들이 올라가면 아래 **Commit changes** 박스에 "Initial commit"이라고 적고 녹색 **Commit changes** 버튼을 누릅니다.

## 3단계: Streamlit Cloud 연결하기

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2. 우측 상단 **New app** 버튼을 클릭합니다.
3. **Use existing repo**를 선택합니다.
4. **Repository**: 방금 만든 `beyondstat-portal`을 선택합니다.
5. **Branch**: `main` (기본값)
6. **Main file path**: `Home.py` (자동으로 잡히지 않으면 직접 입력하세요)
7. **Deploy!** 버튼을 누르기 **전에**, 아래 4단계를 먼저 하세요! (이미 눌렀다면 설정에서 수정 가능)

## 4단계: 보안 키(Secrets) 설정 (★3개 계정 통합)
K-League, 윤청구 센터, 강원 FC가 각각 다른 서비스 계정을 사용하므로, **3개의 키를 모두 등록**해야 합니다.
이를 위해 제가 **TOML 변환 스크립트**를 만들어 두었습니다.

1. 로컬 터미널에서 아래 명령어를 실행하세요.
   ```bash
   python3 generate_toml.py
   ```
2. 화면에 출력되는 내용을 **몽땅 복사**합니다.
   - 형식:
     ```toml
     [kleague_service_account]
     ...
     
     [ycg_service_account]
     ...
     
     [gangwon_service_account]
     ...
     ```
3. Streamlit Cloud의 **Advanced settings > Secrets** 창에 그대로 붙여넣고 저장합니다.

## 5단계: 배포 완료 및 확인
1. 이제 **Deploy!** 버튼을 누릅니다.
2. 화면에 "Oven baking..." 같은 문구가 나오며 배포가 진행됩니다. (약 1~3분 소요)
3. 완료되면 **풍선 효과(🎈)**와 함께 대시보드가 열립니다!
4. 주소창의 URL(예: `beyondstat-portal.streamlit.app`)을 복사해서 관계자들에게 공유하면 됩니다.

---
### 문제 발생 시 체크리스트
- **Error: Module not found**: `requirements.txt` 파일이 GitHub에 잘 올라갔는지 확인하세요.
- **Error: Authentication failed**: Secrets 설정에서 오타가 없는지, `[gcp_service_account]` 헤더를 빠뜨리지 않았는지 확인하세요.
