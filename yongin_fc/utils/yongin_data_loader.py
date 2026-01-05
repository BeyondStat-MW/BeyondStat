
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import re
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# --- Configuration ---
# Update this to the actual key file for Yongin FC
SERVICE_ACCOUNT_FILE = "yongin-key.json" 
PROJECT_ID = "yonginfc"
DATASET_ID = "vald_data"

# --- Mock Data Generator (For Demo/Dev) ---
def generate_mock_data(player_name, test_type):
    dates = pd.date_range(end=datetime.date.today(), periods=10, freq='W')
    count = len(dates)
    
    data = {'Test_Date': dates}
    
    if test_type == "CMJ":
        data.update({
            'Jump_Height': np.random.uniform(35, 50, count),
            'Peak_Power_BM': np.random.uniform(50, 65, count),
            'RSI_Modified': np.random.uniform(0.3, 0.6, count),
            'Asymmetry_Index': np.random.uniform(-10, 10, count)
        })
    elif test_type == "Nordbord":
        data.update({
            'Max_Force_Left': np.random.uniform(300, 450, count),
            'Max_Force_Right': np.random.uniform(300, 450, count),
            'Imbalance': np.random.uniform(0, 15, count)
        })
    elif test_type == "ForceFrame":
        data.update({
            'Max_Force_Left': np.random.uniform(250, 400, count),
            'Max_Force_Right': np.random.uniform(250, 400, count),
            'Strength_Ratio': np.random.uniform(0.9, 1.1, count)
        })
    
    # Add generic columns
    data['Name'] = player_name
    return pd.DataFrame(data)

def get_db_client():
    """Attempts to create a BigQuery client. Returns None if credentials missing."""
    credentials = None
    
    # Define Scopes
    scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    
    # 1. Try Secrets (Cloud Deployment)
    # Check for standard 'gcp_service_account' or custom 'yongin_service_account'
    if "gcp_service_account" in st.secrets:
        try:
            # Create credentials from the secrets dictionary
            # st.secrets returns a AttrDict, we might need to convert to dict
            key_info = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(
                key_info, scopes=scopes
            )
            # print("Loaded credentials from Streamlit Secrets (gcp_service_account)")
        except Exception as e:
            print(f"Failed to load secrets: {e}")

    elif "yongin_service_account" in st.secrets:
         try:
            key_info = dict(st.secrets["yongin_service_account"])
            credentials = service_account.Credentials.from_service_account_info(
                key_info, scopes=scopes
            )
         except Exception: pass
            
    # 2. Try File (Local Development)
    if not credentials:
        possible_paths = [SERVICE_ACCOUNT_FILE, os.path.join("yongin_fc", SERVICE_ACCOUNT_FILE)]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    credentials = service_account.Credentials.from_service_account_file(path, scopes=scopes)
                    print(f"Loaded credentials from: {path}") 
                    break
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
                    pass
        
    if credentials:
        return bigquery.Client(credentials=credentials, project=PROJECT_ID)
    else:
        return None

@st.cache_data(ttl=600)
def get_player_list():
    """Fetch unique player list from vald_all_data table."""
    client = get_db_client()
    
    if client:
        try:
            # Query the single table "vald_all_data"
            # Note: Column name "Name" should exist based on inspection
            query = f"SELECT DISTINCT Name FROM `{PROJECT_ID}.{DATASET_ID}.vald_all_data` ORDER BY Name"
            df = client.query(query).to_dataframe()
            players = df['Name'].tolist()
            if not players:
                return ["No Players Found in DB"]
            return players
        except Exception as e:
            print(f"DB Connection Error: {e}")
            return [f"DB Error: {e}"]
            
    return ["DB Connection Failed"]

@st.cache_data(ttl=600)
def get_full_team_data():
    """
    Fetch ALL data for Team Dashboard aggregation.
    Returns the raw DataFrame with normalized columns.
    """
    client = get_db_client()
    if client:
        try:
            query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.vald_all_data` ORDER BY Date DESC"
            df = client.query(query).to_dataframe()
            
            if not df.empty:
                # Normalize Columns
                df.columns = [c.replace(' ', '_').replace(':', '_').replace('(', '_').replace(')', '').replace('-', '_') for c in df.columns]
                
                # Standardize Date
                if 'Date' in df.columns:
                    df['Test_Date'] = pd.to_datetime(df['Date']).dt.date
                
                # Ensure derived numeric columns exist (coerce errors to NaN)
                numeric_candidates = [
                    'CMJ_Height_Imp_mom', 'CMJ_Height_Imp_mom_', 
                    'SquatJ_Height_Imp_mom', 'SquatJ_Height_Imp_mom_',
                    'SLJ_Height_L', 'SLJ_Height_R', 'SLJ_Height_Imp_mom_', 
                    'SLJ_Height_L_Imp_mom_', 'SLJ_Height_R_Imp_mom_',
                    'Hamstring_Ecc_L', 'Hamstring_Ecc_R',
                    'Hamstring_ISO_L', 'Hamstring_ISO_R',
                    'HipAdd_L', 'HipAdd_R',
                    'HipAdd_L', 'HipAdd_R',
                    'HipAbd_L', 'HipAbd_R',
                    'HopTest_MeanRSI', 
                    'HipFlexion_Kicker_L', 'HipFlexion_Kicker_R'
                ]
                
                for col in numeric_candidates:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df
                
        except Exception as e:
            print(f"Team Data Query Failed: {e}")
            pass
            
    return pd.DataFrame()

@st.cache_data(ttl=600)
def load_player_data(player_name):
    """
    Load all test data for a player.
    Similar to get_full_team_data but filtered for a specific player.
    """
    client = get_db_client()
    
    if client:
        try:
            query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.vald_all_data` WHERE Name = '{player_name}' ORDER BY Date"
            df = client.query(query).to_dataframe()
            
            if not df.empty:
                # Normalize Columns
                df.columns = [c.replace(' ', '_').replace(':', '_').replace('(', '_').replace(')', '').replace('-', '_') for c in df.columns]
                
                if 'Date' in df.columns:
                    df['Test_Date'] = pd.to_datetime(df['Date']).dt.date
                
                # Ensure numerics
                numeric_candidates = [
                    'CMJ_Height_Imp_mom', 'CMJ_RSI_mod_Imp_mom', 'SquatJ_Height_Imp_mom', 
                    'SLJ_Height_L', 'SLJ_Height_R',
                    'Hamstring_Ecc_L', 'Hamstring_Ecc_R', 'Hamstring_Ecc_Imbalance',
                    'Hamstring_ISO_L', 'Hamstring_ISO_R',
                    'HipAdd_L', 'HipAdd_R', 'HipAdd_Imbalance',
                    'HipAdd_L', 'HipAdd_R', 'HipAdd_Imbalance',
                    'HipAbd_L', 'HipAbd_R',
                    'HopTest_MeanRSI',
                    'HipFlexion_Kicker_L', 'HipFlexion_Kicker_R', 'HipFlexion_Kicker_Imbalance'
                ]
                for col in numeric_candidates:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                # Return the whole DF for flexibility in the dashboard
                return df
                
        except Exception as e:
            print(f"Query Failed: {e}")
            pass
    
    return pd.DataFrame()

def get_team_aggregates():
    """Get team-wide stats for top cards."""
    # Simplified Mock for now
    return {
        "Avg_CMJ_Height": 42.5,
        "Avg_Nordbord_Force": 380,
        "Team_Readiness": 88
    }
