import sys
import os

# Ensure we can import from current directory
sys.path.append(os.getcwd())

try:
    from gangwon_fc.utils import gangwon_data_loader as dl
    
    if hasattr(dl, 'get_full_team_data'):
        print("SUCCESS: get_full_team_data exists.")
    else:
        print("ERROR: get_full_team_data NOT found in module.")
        print("Dir:", dir(dl))
        
except Exception as e:
    print(f"Import Error: {e}")
