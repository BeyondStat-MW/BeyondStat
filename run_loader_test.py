
import sys
import os

# Ensure gangwon_fc/utils is in path
sys.path.append(os.path.join(os.getcwd(), 'gangwon_fc'))

# Import the loader
try:
    from gangwon_fc.utils import gangwon_data_loader
    print("Loader imported successfully.")
except ImportError as e:
    print(f"Import failed: {e}")
    # Try alternate import if path issue
    sys.path.append(os.getcwd())
    from gangwon_fc.utils import gangwon_data_loader

def test_connection():
    print("Attempting to get DB client...")
    client = gangwon_data_loader.get_db_client()
    
    if client:
        print("Client successfully created!")
        try:
            query = "SELECT * FROM `gangwonfc.vald_data.vald_all_data` LIMIT 0"
            df = client.query(query).to_dataframe()
            print("Query Successful!")
            print("Columns:", df.columns.tolist())
        except Exception as e:
            print(f"Query Failed: {e}")
    else:
        print("Failed to get client (init returned None).")

if __name__ == "__main__":
    test_connection()
