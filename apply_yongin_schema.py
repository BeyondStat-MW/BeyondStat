import streamlit as st
from yongin_fc.utils import yongin_data_loader as loader
from google.cloud import bigquery

def apply_schema():
    print("Initializing BigQuery Client...")
    client = loader.get_db_client()
    
    # Read SQL file (Standard Auto-Detect)
    print("Reading SQL Schema dictionary...")
    with open("yongin_fc/yongin_schema.sql", "r") as f:
        sql = f.read()
        
    # Split by semicolon to handle multiple statements if any (though likely just one CREATE OR REPLACE)
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for i, stmt in enumerate(statements):
        print(f"Executing Statement {i+1}...")
        try:
            job = client.query(stmt)
            job.result() # Wait
            print(f"Statement {i+1} Success!")
        except Exception as e:
            print(f"Statement {i+1} Failed: {e}")

if __name__ == "__main__":
    apply_schema()
