import sys
import os
import pandas as pd

# Ensure we can import from current directory
sys.path.append(os.getcwd())

try:
    from gangwon_fc.utils import gangwon_data_loader as dl
    import importlib
    importlib.reload(dl)
    
    print("Fetching Team Data...")
    df = dl.get_full_team_data()
    
    if df.empty:
        print("DATAFRAME IS EMPTY!")
    else:
        print(f"DATAFRAME SHAPE: {df.shape}")
        print("\n--- ALL COLUMNS ---")
        for c in sorted(df.columns):
            print(f"- {c}")
            
        print("\n--- SAMPLE ROW (First 5 Cols) ---")
        print(df.iloc[0].head())
        
        # Check specific targets
        targets = ["CMJ_Height_Imp_mom", "SquatJ_Height_Imp_mom", "SLJ_Height_L", "SLJ_Height_R"]
        print("\n--- TARGET CHECK ---")
        for t in targets:
            exists = t in df.columns
            print(f"'{t}': {'EXISTS' if exists else 'MISSING'}")
            
            if exists:
                # Check for non-nulls
                non_null = df[t].count()
                print(f"  -> Non-null count: {non_null}")

except Exception as e:
    print(f"Error: {e}")
