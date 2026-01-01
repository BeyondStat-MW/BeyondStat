
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Define SERVICE_ACCOUNT_FILE for BigQuery authentication
SERVICE_ACCOUNT_FILE = "service-account-key.json"

@st.cache_data(ttl=600)
def load_data(data_project, dataset, table):
    credentials = None
    project_id = None
    
    # 1. Try Loading from Secrets (for Streamlit Cloud)
    if "kleague_service_account" in st.secrets:
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive"]
            # Convert AttrDict to dict for safety
            key_info = dict(st.secrets["kleague_service_account"])
            credentials = service_account.Credentials.from_service_account_info(
                key_info, scopes=scopes
            )
            project_id = credentials.project_id
        except Exception as e:
            pass # Fallback to file

    # 2. Try Loading from Local File (for Local Development)
    if not credentials:
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
            project_id = credentials.project_id
        else:
            # Debugging Help: Show available keys
            found_keys = list(st.secrets.keys())
            raise FileNotFoundError(
                f"인증 실패: 'kleague_service_account' 키가 Secrets에 없습니다. 현재 등록된 키: {found_keys}"
            )
    
    # Client 생성
    client = bigquery.Client(credentials=credentials, project=project_id)
    
    query = f"SELECT * FROM `{data_project}.{dataset}.{table}`"
    
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
    
        # [CRITICAL] Enforce Test_ID as string globally
        if 'Test_ID' in df.columns:
            df['Test_ID'] = df['Test_ID'].astype(str)
            
        return df
    except Exception as e:
        raise Exception(f"Query failed for `{data_project}.{dataset}.{table}`: {str(e)}")

def process_data(df):
    df_clean = df.copy()
    
    # 컬럼명 정규화 (BigQuery 결과가 'Birth_Date' 또는 'Birth_date'로 올 수 있음)
    if 'Birth_Date' in df_clean.columns:
        df_clean.rename(columns={'Birth_Date': 'Birth_date'}, inplace=True)
    
    # 숫자 변환
    numeric_cols = [
        'Height', 'Weight', 'Age', 'APHV', 
        '_5m_sec_', '_10m_sec_', '_30m_sec_', 
        'CMJ_Height_cm_', 'Flex', 'HamECC_L_N_', 'HamECC_R_N_'
    ]
    
    # Auto-add all Point columns to numeric conversion
    point_cols = [c for c in df_clean.columns if 'Point' in c]
    numeric_cols.extend(point_cols)
    
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # 날짜 변환
    if 'Date' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')

    if 'Birth_date' in df_clean.columns:
        df_clean['Birth_date'] = pd.to_datetime(df_clean['Birth_date'], errors='coerce')
        df_clean['Birth_Year'] = df_clean['Birth_date'].dt.year
        df_clean['Birth_Month'] = df_clean['Birth_date'].dt.month
        
        # Quarter 계산
        df_clean['Birth_Quarter'] = df_clean['Birth_Month'].apply(lambda x: (x-1)//3 + 1 if pd.notnull(x) else 0)
        
        # 숫자형 변환 (오류 방지)
        df_clean['Birth_Year_Int'] = df_clean['Birth_Year'].fillna(0).astype(int)
    else:
        # 컬럼이 없을 경우 에러 방지를 위해 기본값 채움
        df_clean['Birth_Year_Int'] = 0
        df_clean['Birth_Quarter'] = 0
        
    return df_clean

def inject_missing_test_ids(df):
    missing_ids = ['25_1', '25_2']
    new_rows = []
    
    existing_ids = df['Test_ID'].unique()
    
    for mid in missing_ids:
        if mid not in existing_ids:
            # Create a dummy row
            dummy = df.iloc[0].to_dict() if not df.empty else {}
            dummy['Test_ID'] = mid
            # Randomize or zero out other metrics to avoid confusion
            # Setting 'Name' to 'Data Pending' to distinct
            dummy['Name'] = 'Data Pending' 
            dummy['Player'] = 'Data Pending'
            dummy['Team'] = 'TBD'
            new_rows.append(dummy)
    
    if new_rows:
        return pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    return df
