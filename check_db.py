import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.getcwd())

from gangwon_fc.utils import gangwon_data_loader as data_loader

print("--- Starting Data Connection Check ---")

try:
    print("Attempting to fetch full team data...")
    df = data_loader.get_full_team_data()
    
    if df.empty:
        print("❌ Dataframe is EMPTY.")
    else:
        print(f"✅ Dataframe loaded successfully.")
        print(f"   - Total Rows: {len(df)}")
        print(f"   - Columns: {list(df.columns)}")
        
        if 'Test_Date' in df.columns:
            min_date = df['Test_Date'].min()
            max_date = df['Test_Date'].max()
            print(f"   - Date Range: {min_date} ~ {max_date}")
            print(f"   - Unique Dates: {sorted(df['Test_Date'].unique())}")
        else:
            print("❌ 'Test_Date' column missing.")
            
except Exception as e:
    print(f"❌ Error during data loading: {e}")
    import traceback
    traceback.print_exc()

print("--- Check Complete ---")
