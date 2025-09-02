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
        self.is_full_template = False  # Flag to indicate template type
        self.template_validator = TemplateValidator()
        # Schema now reflects the full API capabilities
        self.api_schema = {
            "type": "object",
            "properties": {
                "document": {"type": "object", "properties": {"id": {"type": "integer"}}},
                "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "number": {"type": "integer"},
                "currency": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "exchange_rate": {"type": "number"}
                    }
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "account": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string"},
                                    "movement": {"type": "string", "enum": ["Debit", "Credit"]}
                                }
                            },
                            "customer": {
                                "type": "object",
                                "properties": {
                                    "identification": {"type": "string"},
                                    "branch_office": {"type": "integer"}
                                }
                            },
                            "cost_center": {"type": "integer"},
                            "value": {"type": "number"},
                            "description": {"type": "string"},
                            "due": {
                                "type": "object",
                                "properties": {
                                    "prefix": {"type": "string"},
                                    "consecutive": {"type": "integer"},
                                    "quote": {"type": "integer"},
                                    "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}
                                }
                            },
                            "tax": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "percentage": {"type": "number"}
                                }
                            },
                            "taxes": {
                                "type": "object",
                                "properties": {"base_value": {"type": "number"}}
                            },
                            "fixed_assets": {"type": "integer"},
                            "product": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "warehouse": {"type": "integer"}
                                }
                            }
                        },
                        "required": ["account", "customer", "value"]
                    }
                },
                "observations": {"type": "string"}
            },
            "required": ["document", "date", "items"]
        }
        
    def read_excel(self):
        """Read and validate Excel file, and detect template type."""
        try:
            df = pd.read_excel(self.file)
            error_logger.log_info(f"Successfully read Excel file with {len(df)} rows")

            # Detect template type based on a column unique to the full template
            self.is_full_template = 'tax_id' in df.columns
            
            # Basic validation for the simple template
            if not self.is_full_template:
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
        """Format date to YYYY-MM-DD string, returning None if input is invalid."""
        if pd.isna(date_value):
            return None
        try:
            # Convert to pandas Timestamp first for robust parsing
            ts = pd.to_datetime(date_value)
            return ts.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def _validate_payload(self, payload: Dict) -> None:
        """Validate payload against JSON schema."""
        try:
            jsonschema.validate(instance=payload, schema=self.api_schema)
        except jsonschema.exceptions.ValidationError as e:
            error_logger.log_error(
                'validation_errors',
                'JSON schema validation failed',
                {'error': str(e), 'payload': payload}
            )
            raise ValueError(f"Invalid payload format: {str(e)}")

    def _format_simple_payload(self, df_group):
        """Formats the payload for the simple template."""
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
                "value": float(row['value'])
            }
            # Add cost_center only if it has a valid value
            if 'cost_center' in row and pd.notna(row['cost_center']):
                item['cost_center'] = int(row['cost_center'])
            
            items.append(item)
        
        date_str = self._format_date(df_group['date'].iloc[0])
        
        return {
            "document": {"id": int(df_group['document_id'].iloc[0])},
            "date": date_str,
            "items": items,
            "observations": str(df_group['observations'].iloc[0])
        }

    def _format_full_payload(self, df_group):
        """Formats the payload for the full template, handling optional fields."""
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
                "value": float(row['value'])
            }
            # Add optional fields only if they have valid values
            if 'cost_center' in row and pd.notna(row['cost_center']):
                item['cost_center'] = int(row['cost_center'])
            if 'description' in row and pd.notna(row['description']):
                item['description'] = str(row['description'])
            
            # Due object
            if 'due_prefix' in row and pd.notna(row['due_prefix']):
                item['due'] = {
                    "prefix": str(row['due_prefix']),
                    "consecutive": int(row['due_consecutive']),
                    "quote": int(row['due_quote']),
                    "date": self._format_date(row['due_date'])
                }

            # Tax object
            if 'tax_id' in row and pd.notna(row['tax_id']):
                item['tax'] = {
                    "id": int(row['tax_id']),
                    "name": str(row['tax_name']),
                    "type": str(row['tax_type']),
                    "percentage": float(row['tax_percentage'])
                }
                item['taxes'] = {"base_value": float(row['tax_base_value'])}

            # Fixed Assets
            if 'fixed_asset_id' in row and pd.notna(row['fixed_asset_id']):
                item['fixed_assets'] = int(row['fixed_asset_id'])

            # Product object
            if 'product_code' in row and pd.notna(row['product_code']):
                item['product'] = {
                    "code": str(row['product_code']),
                    "quantity": float(row['product_quantity']),
                    "warehouse": int(row['product_warehouse'])
                }
            items.append(item)

        first_row = df_group.iloc[0]
        payload = {
            "document": {"id": int(first_row['document_id'])},
            "date": self._format_date(first_row['date']),
            "items": items
        }
        # Add optional top-level fields
        if 'document_number' in first_row and pd.notna(first_row['document_number']):
            payload['number'] = int(first_row['document_number'])
        if 'currency_code' in first_row and pd.notna(first_row['currency_code']):
            payload['currency'] = {
                "code": str(first_row['currency_code']),
                "exchange_rate": float(first_row['currency_exchange_rate'])
            }
        if 'observations' in first_row and pd.notna(first_row['observations']):
            payload['observations'] = str(first_row['observations'])
            
        return payload

    def format_entries_for_api(self, df_group):
        """
        Dispatcher method to format entries based on the detected template type.
        """
        try:
            if self.is_full_template:
                payload = self._format_full_payload(df_group)
            else:
                payload = self._format_simple_payload(df_group)
            
            # Validate the final payload against the comprehensive schema
            self._validate_payload(payload)
            
            return payload
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error formatting entries: {str(e)}",
                {'document_id': df_group['document_id'].iloc[0] if not df_group.empty else None}
            )
            raise Exception(f"Error formatting entries: {str(e)}")