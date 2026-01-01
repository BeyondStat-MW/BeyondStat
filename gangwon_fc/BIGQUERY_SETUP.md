# 강원 FC 대시보드 - BigQuery 및 GCP 설정 가이드

실제 데이터를 연동하기 위해 **Google Cloud Platform (GCP)**에서 단 한 번의 설정이 필요합니다. 아래 단계를 순서대로 따라해주세요.

## 1단계: 프로젝트 생성 (Google Cloud Console)
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다.
2. 좌측 상단의 프로젝트 선택 목록을 클릭하고 **[새 프로젝트]**를 선택합니다.
3. **프로젝트 이름**에 `gangwon-fc-db`를 입력하고 **[만들기]**를 클릭합니다. (이미 있다면 해당 프로젝트 선택)

## 2단계: API 사용 설정 (필수)
구글 시트를 읽어오기 위해 2가지 API를 켜야 합니다.
1. 상단 검색창에 **"BigQuery API"**를 검색하고 **[사용]**을 클릭합니다.
2. 상단 검색창에 **"Google Drive API"**를 검색하고 **[사용]**을 클릭합니다. (시트 데이터 접근용)

## 3단계: 서비스 계정 키 생성 (`gangwon-key.json`)
대시보드가 BigQuery에 접속할 수 "열쇠"를 만드는 과정입니다.
1. 좌측 메뉴에서 **IAM 및 관리자 > 서비스 계정**으로 이동합니다.
2. **[+ 서비스 계정 만들기]**를 클릭합니다.
    - 이름: `gangwon-dashboard` (임의 지정 가능)
    - **[완료]**를 클릭하여 생성합니다.
3. 생성된 계정(`...@gangwon-fc-db.iam.gserviceaccount.com`)을 클릭합니다.
4. **[키]** 탭으로 이동 -> **[키 추가]** -> **[새 키 만들기]** 선택.
5. **JSON**을 선택하고 **[만들기]**를 클릭하면 파일이 다운로드됩니다.
6. 다운로드된 파일의 이름을 **`gangwon-key.json`**으로 변경합니다.
7. 이 파일을 프로젝트의 `gangwon_fc/` 폴더 안으로 복사해 넣습니다.

## 4단계: 구글 시트 권한 부여 (중요!)
방금 만든 서비스 계정이 구글 시트를 볼 수 있도록 초대해야 합니다.
1. `gangwon-key.json` 파일을 메모장으로 열어 **`client_email`** 값을 복사합니다.
   (예: `gangwon-dashboard@gangwon-fc-db.iam.gserviceaccount.com`)
2. [강원 FC 데이터 구글 시트](https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit)로 이동합니다.
3. 우측 상단 **[공유]** 버튼을 클릭합니다.
4. 복사한 **이메일 주소**를 붙여넣고 **[뷰어]** 권한으로 공유합니다.

## 5단계: BigQuery 테이블 생성
1. GCP 콘솔 검색창에 **"BigQuery"**를 검색하여 이동합니다.
2. 좌측 탐색기에서 프로젝트(`gangwon-fc-db`) 옆의 점 3개 메뉴 -> **[데이터세트 만들기]** 클릭.
    - 데이터세트 ID: `vald_data`
    - 위치: `asia-northeast3 (서울)` 권장 (혹은 기본값 US)
    - **[데이터세트 만들기]** 클릭.
3. 상단 **[쿼리 편집기]**를 엽니다.
4. 아래 SQL 코드를 복사해서 붙여넣고 **[실행]** 버튼을 누릅니다.
   (이 코드는 `gangwon_fc/gangwon_schema.sql` 파일에도 있습니다.)

```sql
-- 1. CMJ
CREATE OR REPLACE EXTERNAL TABLE `gangwon-fc-db.vald_data.vald_cmj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'CMJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 2. Nordbord
CREATE OR REPLACE EXTERNAL TABLE `gangwon-fc-db.vald_data.vald_nordbord`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'Nordbord',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 3. ForceFrame
CREATE OR REPLACE EXTERNAL TABLE `gangwon-fc-db.vald_data.vald_forceframe`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'ForceFrame',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 4. SJ
CREATE OR REPLACE EXTERNAL TABLE `gangwon-fc-db.vald_data.vald_sj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'SJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);

-- 5. HJ
CREATE OR REPLACE EXTERNAL TABLE `gangwon-fc-db.vald_data.vald_hj`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio/edit'],
  sheet_range = 'HJ',
  skip_leading_rows = 1,
  max_bad_records = 0
);
```

## 완료
위 5단계를 마치고 `gangwon-key.json` 파일을 프로젝트 폴더에 넣으시면 준비 끝입니다!
