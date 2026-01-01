
import pandas as pd
import requests
from io import StringIO

SHEET_ID = "1TKxBm1wyTxLdhVmP8Q9xDKILmRDV_eYvqEjaDJSvIio"
SHEET_NAME = "All Data"

# Construct Export URL
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

print(f"Downloading from: {url}")

try:
    response = requests.get(url)
    response.raise_for_status()
    
    # Check if we got a login page or valid CSV
    content = response.text
    if "<html" in content[:100].lower():
        print("Error: Received HTML instead of CSV. Sheet is likely private.")
    else:
        # Parse CSV
        df = pd.read_csv(StringIO(content))
        print("\n--- Headers ---")
        for col in df.columns:
            print(col)
            
except Exception as e:
    print(f"Download Failed: {e}")
