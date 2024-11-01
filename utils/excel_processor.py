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
            entries = []
            for _, row in df_group.iterrows():
                entry = {
                    "account": str(row['account']),
                    "description": row['description'],
                    "debit": float(row['debit']) if row['debit'] > 0 else 0,
                    "credit": float(row['credit']) if row['credit'] > 0 else 0
                }
                # Add optional fields if present
                if 'reference' in row:
                    entry['reference'] = str(row['reference'])
                if 'department' in row:
                    entry['department'] = str(row['department'])
                entries.append(entry)
            return entries
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error formatting entries: {str(e)}",
                {'date': df_group['date'].iloc[0]}
            )
            raise Exception(f"Error formatting entries: {str(e)}")
