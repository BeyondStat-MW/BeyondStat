
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import datetime
import re
import os

# Define SERVICE_ACCOUNT_FILE for BigQuery authentication
SERVICE_ACCOUNT_FILE = "ycg-key.json"

def get_client():
    credentials = None
    project_id = "ycgcenter" # Default
    
    # 1. Try Loading from Secrets (for Streamlit Cloud)
    if "ycg_service_account" in st.secrets:
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive"]
            key_info = dict(st.secrets["ycg_service_account"])
            credentials = service_account.Credentials.from_service_account_info(
                key_info, scopes=scopes
            )
            project_id = credentials.project_id
        except Exception as e:
            print(f"Secret Load Error: {e}")
            pass # Fallback to file

    # 2. Try Loading from Local File (for Local Development)
    if not credentials:
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            try:
                # FIXED: Must include Drive scope for External Tables
                scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive"]
                credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
                project_id = credentials.project_id
            except Exception as e:
                 st.error(f"인증 파일 로드 실패: {e}")
                 return None
    
    # If still no credentials, rely on default chain (but warn)
    if not credentials:
        pass

    try:
        if credentials:
            return bigquery.Client(credentials=credentials, project=project_id)
        else:
            return bigquery.Client(project="ycgcenter")
    except Exception as e:
        st.error(f"BigQuery 연결 실패: {e}")
        return None

@st.cache_data(ttl=600)
def load_vald_data(player_name):
    """
    Queries all 5 VALD tables for a specific player name.
    Attempts exact match first, then fuzzy match (cleaned name), then substring match.
    """
    client = get_client()
    if not client: return {}

    tables = {
        "CMJ": "vald_cmj",
        "Nordbord": "vald_nordbord",
        "ForceFrame": "vald_forceframe", 
        "SJ": "vald_sj",
        "HJ": "vald_hj" 
    }
    
    data_dict = {}

    # Define Name Cleaning Strategy
    # Remove "(18)" or "(Num)" from start or end
    # e.g. "(18)안 선우" -> "안 선우" -> trim -> "안선우"
    
    # 1. Exact Name
    candidates = [player_name]
    
    # 2. Cleaned Name (Remove parentheses and digits)
    cleaned = re.sub(r'\(\d+\)', '', player_name).strip()
    if cleaned != player_name:
        candidates.append(cleaned)
        
    # 3. No Space Name (e.g. "안 선우" -> "안선우")
    nospace = cleaned.replace(" ", "")
    if nospace != cleaned:
        candidates.append(nospace)
        
    print(f"Searching VALD for candidates: {candidates}")

    # Potential Name Columns to check in order
    # FIXED: Prioritize 'Name' because we are searching by Name string. 
    name_col_candidates = ['Name', 'Player Name', 'Player_Name', 'Player', '이름', '선수명', 'Player_ID']

    for test_name, table_id in tables.items():
        found_df = pd.DataFrame()
        
        # 1. Determine the valid Name Column for this table
        valid_name_col = None
        try:
            # Check schema efficiently
            schema_q = f"SELECT * FROM `ycgcenter.YCGCenter_db.{table_id}` LIMIT 0"
            schema_df = client.query(schema_q).to_dataframe()
            user_cols = set(schema_df.columns)
            
            # Case insensitive check
            user_cols_lower = {c.lower(): c for c in user_cols}
            
            for nc in name_col_candidates:
                if nc.lower() in user_cols_lower:
                    valid_name_col = user_cols_lower[nc.lower()]
                    break
            
            # print(f"[{test_name}] Columns: {list(user_cols)}")    
            if not valid_name_col:
                print(f"[{test_name}] No matching Name column found.")
                continue
            else:
                pass 
                # print(f"[{test_name}] Selected Name Column: {valid_name_col}")
                
        except Exception as e:
            print(f"[{test_name}] Schema check failed: {e}")
            continue

        # 2. Query using the found valid column
        # Determine Date Column dynamically (Test_Date vs Date)
        date_col = 'Test_Date'
        if 'Date' in user_cols: date_col = 'Date'
        elif 'date' in user_cols: date_col = 'date'
        
        # Iteratively try querying until data found
        for cand in candidates:
            # Try Exact Match
            query = f"""
                SELECT *
                FROM `ycgcenter.YCGCenter_db.{table_id}`
                WHERE `{valid_name_col}` = '{cand}'
                ORDER BY `{date_col}` ASC
            """
            try:
                # print(f"   Querying: WHERE {valid_name_col} = '{cand}' ORDER BY {date_col}")
                df = client.query(query).to_dataframe()
                if not df.empty:
                    found_df = df
                    break # Found!
            except Exception as e:
                # print(f"   Query Failed: {e}")
                pass
            
            # Try Like Match (if exact failed)
            query_like = f"""
                SELECT *
                FROM `ycgcenter.YCGCenter_db.{table_id}`
                WHERE `{valid_name_col}` LIKE '%{cand}%'
                ORDER BY `{date_col}` ASC
            """
            try:
                df_like = client.query(query_like).to_dataframe()
                if not df_like.empty:
                    found_df = df_like
                    break
            except Exception: pass
            
            # [NEW] Try Ignore-Space Match (Ultimate Fallback)
            cand_nospace = cand.replace(" ", "")
            if cand_nospace:
                query_nospace = f"""
                    SELECT *
                    FROM `ycgcenter.YCGCenter_db.{table_id}`
                    WHERE REPLACE(`{valid_name_col}`, ' ', '') LIKE '%{cand_nospace}%'
                    ORDER BY `{date_col}` ASC
                """
                try:
                    df_ns = client.query(query_nospace).to_dataframe()
                    if not df_ns.empty:
                        found_df = df_ns
                        break
                except Exception: pass
            
        if not found_df.empty:
             if 'Test_Date' in found_df.columns:
                found_df['Test_Date'] = pd.to_datetime(found_df['Test_Date'])
             data_dict[test_name] = found_df
        else:
             data_dict[test_name] = pd.DataFrame() # Empty
             
    return data_dict

@st.cache_data(ttl=600)
def get_vald_player_list():
    """
    Returns a list of unique player names found in the VALD CMJ table.
    """
    client = get_client()
    if not client: return []
    
    table_id = "vald_cmj"
    try:
        # Determine Name column
        schema_q = f"SELECT * FROM `ycgcenter.YCGCenter_db.{table_id}` LIMIT 0"
        schema_df = client.query(schema_q).to_dataframe()
        user_cols = {c.lower(): c for c in schema_df.columns}
        
        valid_name_col = None
        for nc in ['Name', 'Player Name', 'Player_Name', 'Player', '이름', '선수명']:
            if nc.lower() in user_cols:
                valid_name_col = user_cols[nc.lower()]
                break
        
        if not valid_name_col: return []

        query = f"SELECT DISTINCT `{valid_name_col}` FROM `ycgcenter.YCGCenter_db.{table_id}` ORDER BY `{valid_name_col}`"
        df = client.query(query).to_dataframe()
        return df[valid_name_col].tolist()
        
    except Exception as e:
        print(f"Error fetching VALD player list: {e}")
        return []
