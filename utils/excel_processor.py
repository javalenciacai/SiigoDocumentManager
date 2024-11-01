import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import error_logger
from utils.template_validator import TemplateValidator

class ExcelProcessor:
    def __init__(self, file):
        self.file = file
        self.template_validator = TemplateValidator()
        
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
    
    def format_entries_for_api(self, df_group):
        """Format entries according to Siigo API specifications"""
        try:
            items = []
            for _, row in df_group.iterrows():
                item = {
                    "account": {
                        "code": str(row['account_code']),
                        "movement": row['movement']
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
                
            # Create the complete payload
            payload = {
                "document": {"id": int(df_group['document_id'].iloc[0])},
                "date": df_group['date'].iloc[0],
                "items": items,
                "observations": str(df_group['observations'].iloc[0])
            }
            
            return payload
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error formatting entries: {str(e)}",
                {'date': df_group['date'].iloc[0] if not df_group.empty else None}
            )
            raise Exception(f"Error formatting entries: {str(e)}")
