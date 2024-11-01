import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import error_logger
from utils.template_validator import TemplateValidator
import jsonschema
from typing import Dict, Any

class ExcelProcessor:
    def __init__(self, file):
        self.file = file
        self.template_validator = TemplateValidator()
        self.api_schema = {
            "type": "object",
            "required": ["document", "date", "items", "observations"],
            "properties": {
                "document": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {"type": "integer"}
                    }
                },
                "date": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["account", "customer", "description", "cost_center", "value"],
                        "properties": {
                            "account": {
                                "type": "object",
                                "required": ["code", "movement"],
                                "properties": {
                                    "code": {"type": "string"},
                                    "movement": {"type": "string", "enum": ["Debit", "Credit"]}
                                }
                            },
                            "customer": {
                                "type": "object",
                                "required": ["identification", "branch_office"],
                                "properties": {
                                    "identification": {"type": "string"},
                                    "branch_office": {"type": "integer", "minimum": 0}
                                }
                            },
                            "description": {"type": "string", "maxLength": 255},
                            "cost_center": {"type": "integer", "minimum": 0},
                            "value": {"type": "number", "minimum": 0}
                        }
                    }
                },
                "observations": {"type": "string", "maxLength": 500}
            }
        }
        
    def read_excel(self):
        """Read and validate Excel file"""
        try:
            df = pd.read_excel(self.file)
            error_logger.log_info(f"Successfully read Excel file with {len(df)} rows")
            
            # Validate template structure and data
            self.template_validator.validate_template(df)
            
            return df
        except Exception as e:
            error_logger.log_error(
                'validation_errors',
                f"Error reading Excel file: {str(e)}",
                {'filename': getattr(self.file, 'name', 'unknown')}
            )
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _format_date(self, date_value: Any) -> str:
        """Format date to YYYY-MM-DD string"""
        try:
            if isinstance(date_value, pd.Timestamp):
                return date_value.strftime('%Y-%m-%d')
            elif isinstance(date_value, str):
                return datetime.strptime(date_value, '%Y-%m-%d').strftime('%Y-%m-%d')
            elif isinstance(date_value, datetime):
                return date_value.strftime('%Y-%m-%d')
            else:
                raise ValueError(f"Unsupported date format: {type(date_value)}")
        except Exception as e:
            raise ValueError(f"Error formatting date: {str(e)}")

    def _validate_payload(self, payload: Dict) -> None:
        """Validate payload against JSON schema"""
        try:
            jsonschema.validate(instance=payload, schema=self.api_schema)
        except jsonschema.exceptions.ValidationError as e:
            error_logger.log_error(
                'validation_errors',
                'JSON schema validation failed',
                {'error': str(e)}
            )
            raise ValueError(f"Invalid payload format: {str(e)}")
    
    def format_entries_for_api(self, df_group):
        """Format entries according to Siigo API specifications"""
        try:
            items = []
            for _, row in df_group.iterrows():
                item = {
                    "account": {
                        "code": str(row['account_code']),
                        "movement": str(row['movement'])
                    },
                    "customer": {
                        "identification": str(row['customer_identification']),
                        "branch_office": int(row['branch_office'])
                    },
                    "description": str(row['description']),
                    "cost_center": int(row['cost_center']),
                    "value": float(row['value'])
                }
                items.append(item)
                
            # Create the complete payload with proper date formatting
            date_str = self._format_date(df_group['date'].iloc[0])
            
            payload = {
                "document": {"id": int(df_group['document_id'].iloc[0])},
                "date": date_str,
                "items": items,
                "observations": str(df_group['observations'].iloc[0])
            }
            
            # Validate payload against schema
            self._validate_payload(payload)
            
            return payload
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error formatting entries: {str(e)}",
                {'date': df_group['date'].iloc[0] if not df_group.empty else None}
            )
            raise Exception(f"Error formatting entries: {str(e)}")
