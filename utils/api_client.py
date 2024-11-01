import requests
import os
from datetime import datetime

class SiigoAPI:
    def __init__(self, username, access_key):
        self.username = username
        self.access_key = access_key
        self.base_url = os.getenv('SIIGO_API_URL')
        self.token = None
        
    def authenticate(self):
        """Authenticate with Siigo API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Partner-Id": "EmpreSAAS"
            }
            response = requests.post(
                f"{self.base_url}/auth",
                headers=headers,
                json={
                    "username": self.username,
                    "access_key": self.access_key
                }
            )
            response.raise_for_status()
            self.token = response.json().get('access_token')
            return True
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def create_journal_entry(self, entry_data):
        """Create a journal entry in Siigo"""
        if not self.token:
            raise Exception("Not authenticated")
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Partner-Id": "EmpreSAAS"
        }
        
        # Transform entry_data to Siigo API format
        payload = self._format_entry_data(entry_data)
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/journals",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API error: {str(e)}")
    
    def _format_entry_data(self, entry_data):
        """Format entry data according to Siigo API specifications"""
        return {
            "document_date": entry_data.get('date', datetime.now().strftime("%Y-%m-%d")),
            "description": entry_data.get('description', ''),
            "entries": [
                {
                    "account": entry_data.get('account'),
                    "debit": entry_data.get('debit', 0),
                    "credit": entry_data.get('credit', 0),
                    "description": entry_data.get('line_description', '')
                }
            ]
        }
