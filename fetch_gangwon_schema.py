
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Configuration
KEY_PATH = "gangwon_fc/gangwon-key.json"
PROJECT_ID = "gangwonfc"
DATASET_ID = "vald_data"
TABLE_ID = "vald_all_data"

def get_headers():
    if not os.path.exists(KEY_PATH):
        print(f"Error: Key file not found at {KEY_PATH}")
        return

    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_PATH, 
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
        )
        client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
        
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        table = client.get_table(table_ref)
        
        print("\n### Gangwon FC - vald_all_data Schema ###")
        print(f"Total Columns: {len(table.schema)}\n")
        
        columns = [field.name for field in table.schema]
        
        # Print comfortably for user to copy
        print("--- Column List ---")
        for col in columns:
            print(col)
            
    except Exception as e:
        print(f"Failed to fetch schema: {e}")

if __name__ == "__main__":
    get_headers()
