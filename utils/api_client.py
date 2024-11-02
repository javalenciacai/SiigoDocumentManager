import requests
import os
from datetime import datetime
from utils.logger import error_logger
import jwt  # Change this line to use PyJWT directly

class SiigoAPI:
    def __init__(self, username, access_key):
        self.username = username
        self.access_key = access_key
        self.base_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')  # Add default URL
        self.token = None
        self.company_name = None
        
    def _extract_company_name(self, token):
        try:
            # Use jwt.decode directly
            decoded = jwt.decode(
                jwt=token,
                key=None,
                algorithms=["HS256"],
                options={"verify_signature": False}
            )
            
            # Get the company name from the decoded token
            company_name = decoded.get('cloud_tenant_company_key')
            if not company_name:
                company_name = decoded.get('company_name')
            if not company_name:
                error_logger.log_error(
                    'authentication_errors',
                    "Company name not found in token",
                    {'token_claims': list(decoded.keys())}
                )
                return 'Unknown Company'
            error_logger.log_info(f"Successfully extracted company name: {company_name}")
            return company_name
        except Exception as e:
            error_logger.log_error(
                'authentication_errors',
                f"Error decoding JWT token: {str(e)}",
                {'error_type': str(type(e))}
            )
            return 'Unknown Company'

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
            self.company_name = self._extract_company_name(self.token)
            error_logger.log_info(f"Successfully authenticated user: {self.username}")
            return True
        except requests.exceptions.RequestException as e:
            error_response = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                except:
                    error_response = e.response.text

            error_logger.log_error(
                'authentication_errors',
                str(e),
                {
                    'username': self.username,
                    'status_code': getattr(e.response, 'status_code', None),
                    'error_details': error_response
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
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/journals",
                headers=headers,
                json=entry_data
            )
            response.raise_for_status()
            result = response.json()
            error_logger.log_info(
                f"Successfully created journal entry for date {entry_data['date']}"
            )
            return result
        except requests.exceptions.RequestException as e:
            error_response = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                except:
                    error_response = e.response.text

            error_logger.log_error(
                'api_errors',
                f"API error: {str(e)}",
                {
                    'status_code': getattr(e.response, 'status_code', None),
                    'error_details': error_response,
                    'request_payload': entry_data
                }
            )
            raise Exception(f"API error: {str(e)}\nDetails: {error_response}")

    def get_cost_centers(self):
        """Fetch cost centers from Siigo API"""
        if not self.token:
            error_msg = "Not authenticated"
            error_logger.log_error('api_errors', error_msg)
            raise Exception(error_msg)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Partner-Id": "EmpreSAAS"
        }

        try:
            response = requests.get(
                f"{self.base_url}/v1/cost-centers",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            error_logger.log_info("Successfully fetched cost centers")
            return result
        except Exception as e:
            error_logger.log_error(
                'api_errors',
                f"Error fetching cost centers: {str(e)}"
            )
            raise

    def get_document_types(self):
        """Fetch document types from Siigo API"""
        if not self.token:
            error_msg = "Not authenticated"
            error_logger.log_error('api_errors', error_msg)
            raise Exception(error_msg)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Partner-Id": "EmpreSAAS"
        }

        try:
            response = requests.get(
                f"{self.base_url}/v1/document-types",
                headers=headers,
                params={"type": "CC"}  # Filter for journal vouchers
            )
            response.raise_for_status()
            result = response.json()
            error_logger.log_info("Successfully fetched document types")
            return result
        except Exception as e:
            error_logger.log_error(
                'api_errors',
                f"Error fetching document types: {str(e)}"
            )
            raise
