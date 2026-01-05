import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import streamlit as st

# Setup Credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'yongin_fc/yongin-key.json'  # CORRECT PATH
SPREADSHEET_ID = '1M7K8SwfAulrto3G9p97a4ENfYerHIh6VFpALvj17mf0'
RANGE_NAME = "'All Data'!A1:ZZ1" 

def get_headers():
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return []
            
        headers = values[0]
        print(f"Found {len(headers)} columns.")
        return headers
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    headers = get_headers()
    
    # Generate SQL
    if headers:
        sql = "CREATE OR REPLACE EXTERNAL TABLE `yonginfc.vald_data.vald_all_data` (\n"
        
        seen_headers = {} # name -> count
        
        for i, h in enumerate(headers):
            # Sanitize header for BigQuery column name
            safe_h = h.strip().replace(' ', '_').replace(':', '').replace('(', '').replace(')', '').replace('-', '_').replace('%', 'Pct').replace('/', '_').replace('.', '')
            
            # Handle duplicates or empty
            if not safe_h: safe_h = f"Col_{i}"
            
            # BigQuery columns cannot start with number
            if safe_h[0].isdigit(): safe_h = f"_{safe_h}"
            
            # Deduplicate
            if safe_h in seen_headers:
                seen_headers[safe_h] += 1
                safe_h = f"{safe_h}_{seen_headers[safe_h]}"
            else:
                seen_headers[safe_h] = 1
            
            comma = "," if i < len(headers) - 1 else ""
            sql += f"  `{safe_h}` STRING{comma}\n"
            
        sql += ")\nOPTIONS (\n"
        sql += "  format = 'GOOGLE_SHEETS',\n"
        sql += f"  uris = ['https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit'],\n"
        sql += "  sheet_range = 'All Data',\n"
        sql += "  skip_leading_rows = 1,\n"
        sql += "  max_bad_records = 0\n"
        sql += ");"
        
        print("\n--- GENERATED SQL ---")
        print(sql)
        
        # Save to file
        with open("yongin_fc/yongin_full_schema.sql", "w") as f:
            f.write(sql)
            
        print("\nSaved to yongin_fc/yongin_full_schema.sql")
