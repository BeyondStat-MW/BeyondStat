from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st
import os

# Manual setup to avoid loader complexity
KEY_FILE = "gangwon-key.json"
for path in [KEY_FILE, os.path.join("gangwon_fc", KEY_FILE)]:
    if os.path.exists(path):
        creds = service_account.Credentials.from_service_account_file(path)
        client = bigquery.Client(credentials=creds, project="gangwonfc")
        
        query = "SELECT * FROM `gangwonfc.vald_data.vald_all_data` LIMIT 1"
        df = client.query(query).to_dataframe()
        
        print("COLUMNS FOUND:")
        print(df.columns.tolist())
        break
