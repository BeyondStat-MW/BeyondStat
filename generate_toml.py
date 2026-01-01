import json
import os

def generate_toml():
    print("# Copy and paste the output below into your Streamlit Cloud Secrets")
    print("# ----------------------------------------------------------------")
    
    # 1. Gangwon FC
    if os.path.exists("gangwon_fc/gangwon-key.json"):
        with open("gangwon_fc/gangwon-key.json", "r") as f:
            key_content = json.load(f)
            print("\n[gangwon_service_account]")
            for k, v in key_content.items():
                if k == "private_key":
                    print(f'{k} = """{v}"""')
                else:
                    print(f'{k} = "{v}"')
    else:
        print("\n# [WARNING] gangwon_fc/gangwon-key.json not found!")

    # 2. K-League
    if os.path.exists("service-account-key.json"):
        with open("service-account-key.json", "r") as f:
            key_content = json.load(f)
            print("\n[kleague_service_account]")
            for k, v in key_content.items():
                if k == "private_key":
                    print(f'{k} = """{v}"""')
                else:
                    print(f'{k} = "{v}"')
    
    # 3. Yoon Center
    if os.path.exists("ycg-key.json"):
        with open("ycg-key.json", "r") as f:
            key_content = json.load(f)
            print("\n[ycg_service_account]")
            for k, v in key_content.items():
                if k == "private_key":
                    print(f'{k} = """{v}"""')
                else:
                    print(f'{k} = "{v}"')

if __name__ == "__main__":
    generate_toml()
