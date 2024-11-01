import requests
import os
from datetime import datetime
from utils.logger import error_logger

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
            error_logger.log_info(f"Successfully authenticated user: {self.username}")
            return True
        except requests.exceptions.RequestException as e:
            error_logger.log_error(
                'authentication_errors',
                str(e),
                {
                    'username': self.username,
                    'status_code': getattr(e.response, 'status_code', None),
                    'response_text': getattr(e.response, 'text', None)
                }
            )
            return False
        except Exception as e:
            error_logger.log_error(
                'authentication_errors',
                str(e),
                {'username': self.username}
            )
            return False
    
    def create_journal_entry(self, entry_data):
        """Create a journal entry in Siigo"""
        if not self.token:
            error_msg = "Not authenticated"
            error_logger.log_error('api_errors', error_msg)
            raise Exception(error_msg)
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Partner-Id": "EmpreSAAS"
        }
        
        # Format the payload according to Siigo API requirements
        payload = {
            "document_date": entry_data['date'],
            "description": "Journal Entry",
            "entries": entry_data['entries']
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/journals",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            error_logger.log_info(
                f"Successfully created journal entry for date {entry_data['date']}"
            )
            return result
        except requests.exceptions.RequestException as e:
            error_msg = f"API error: {str(e)}"
            error_logger.log_error(
                'api_errors',
                error_msg,
                {
                    'status_code': getattr(e.response, 'status_code', None),
                    'response_text': getattr(e.response, 'text', None),
                    'date': entry_data['date']
                }
            )
            raise Exception(error_msg)
