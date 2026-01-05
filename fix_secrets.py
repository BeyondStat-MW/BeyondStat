
import json
import os
import sys

def fix_secrets():
    print("Starting Deep Inspection & Fix of Secrets...")
    
    secrets_path = ".streamlit/secrets.toml"
    os.makedirs(".streamlit", exist_ok=True)
    
    toml_lines = []
    
    # 1. Gangwon FC
    p_gangwon = "gangwon_fc/gangwon-key.json"
    if os.path.exists(p_gangwon):
        try:
            with open(p_gangwon, "r") as f:
                key = json.load(f)
                pk = key.get("private_key", "")
                print(f"[Gangwon] Source Key Found. Private Key Length: {len(pk)}")
                if len(pk) < 100:
                    print(f"[Gangwon] CRITICAL ERROR: Source key is too short! ({len(pk)} chars)")
                
                toml_lines.append("[gangwon_service_account]")
                for k, v in key.items():
                    # json.dumps handles escaping (newlines, quotes) perfectly for TOML single-line strings
                    toml_lines.append(f'{k} = {json.dumps(v)}')
                toml_lines.append("")
        except Exception as e:
            print(f"[Gangwon] Error reading json: {e}")
    else:
        print(f"[Gangwon] Key file NOT found at {p_gangwon}")

    # 2. Yongin FC
    p_yongin = "yongin_fc/yongin-key.json"
    if os.path.exists(p_yongin):
        try:
            with open(p_yongin, "r") as f:
                key = json.load(f)
                pk = key.get("private_key", "")
                print(f"[Yongin] Source Key Found. Private Key Length: {len(pk)}")
                
                toml_lines.append("[yongin_service_account]")
                for k, v in key.items():
                    toml_lines.append(f'{k} = {json.dumps(v)}')
                toml_lines.append("")
        except Exception as e:
            print(f"[Yongin] Error reading json: {e}")
            
    # Write to secrets.toml
    try:
        with open(secrets_path, "w") as f:
            f.write("\n".join(toml_lines))
        print(f"Successfully wrote {len(toml_lines)} lines to {secrets_path}")
    except Exception as e:
        print(f"Failed to write secrets.toml: {e}")

if __name__ == "__main__":
    fix_secrets()
