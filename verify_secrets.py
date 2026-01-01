import toml
import sys

try:
    config = toml.load(".streamlit/secrets.toml")
    print("SUCCESS: secrets.toml is valid TOML.")
    # Check if keys exist
    expected_keys = ["gangwon_service_account", "kleague_service_account", "ycg_service_account"]
    for k in expected_keys:
        if k in config:
            print(f"Found key: {k}")
        else:
            print(f"MISSING key: {k}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
