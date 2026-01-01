
import requests
import streamlit as st
import time

class ValdApiClient:
    def __init__(self):
        # Load secrets safely
        try:
            self.client_id = st.secrets["vald_api"]["client_id"]
            self.client_secret = st.secrets["vald_api"]["client_secret"]
            self.base_url = st.secrets["vald_api"].get("base_url", "https://api.valdperformance.com")
            self.token_url = st.secrets["vald_api"].get("token_url", "https://auth.prd.vald.com/oauth/token")
        except KeyError:
            st.error("❌ secrets.toml에 [vald_api] 설정이 없습니다. Migration Guide를 참고하세요.")
            self.client_id = None
            
        self.access_token = None
        self.token_expiry = 0

    def get_token(self):
        """
        Authenticates with Client Credentials Flow and returns Access Token.
        Caches token until expiry.
        """
        if not self.client_id:
            return None

        # Check if current token is valid (with 60s buffer)
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "https://api.valdperformance.com" 
        }

        try:
            response = requests.post(self.token_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data["access_token"]
            self.token_expiry = time.time() + data.get("expires_in", 3600)
            return self.access_token
            
        except Exception as e:
            st.error(f"VALD Auth Failed: {e}")
            return None

    def get_athletes(self):
        """
        Fetches list of athletes.
        """
        token = self.get_token()
        if not token: return None

        headers = {"Authorization": f"Bearer {token}"}
        # Endpoint may vary by region, checking documentation is recommended
        url = f"{self.base_url}/management/athletes" 
        
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json() # Returns list of dicts
        except Exception as e:
            st.error(f"Failed to fetch athletes: {e}")
            return None
            
    def get_test_results(self, test_type_id=None, from_date=None):
        """
        Fetches test results.
        Note: Exact endpoint depends on VALD API version (e.g. /fusions for aggregate data)
        """
        token = self.get_token()
        if not token: return None

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/monitoring/tests"  # Placeholder endpoint
        
        params = {}
        if from_date: params['fromDate'] = from_date
        
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            st.error(f"Failed to fetch tests: {e}")
            return None
