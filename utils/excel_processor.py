import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import error_logger

class ExcelProcessor:
    def __init__(self, file):
        self.file = file
        self.valid_account_codes = set()  # In a real implementation, this would be populated from Siigo API
        
    def read_excel(self):
        """Read and validate Excel file"""
        try:
            df = pd.read_excel(self.file)
            error_logger.log_info(f"Successfully read Excel file with {len(df)} rows")
            self._validate_dataframe(df)
            return df
        except Exception as e:
            error_logger.log_error(
                'validation_errors',
                f"Error reading Excel file: {str(e)}",
                {'filename': getattr(self.file, 'name', 'unknown')}
            )
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _validate_dataframe(self, df):
        """Validate DataFrame structure and content"""
        required_columns = ['date', 'account', 'description', 'debit', 'credit']
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            error_logger.log_error(
                'validation_errors',
                error_msg,
                {'missing_columns': missing_columns}
            )
            raise Exception(error_msg)
        
        # Validate data types
        invalid_dates = df[~pd.to_datetime(df['date'], errors='coerce').notna()]
        if not invalid_dates.empty:
            error_msg = "Invalid date format in 'date' column"
            error_logger.log_error(
                'validation_errors',
                error_msg,
                {'invalid_rows': invalid_dates.index.tolist()}
            )
            raise Exception(error_msg)
        
        # Validate numeric columns
        for col in ['debit', 'credit']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            invalid_numbers = df[df[col].isna()]
            if not invalid_numbers.empty:
                error_msg = f"Invalid numeric values in '{col}' column"
                error_logger.log_error(
                    'validation_errors',
                    error_msg,
                    {'column': col, 'invalid_rows': invalid_numbers.index.tolist()}
                )
                raise Exception(error_msg)
        
        # Validate account codes
        invalid_accounts = df[~df['account'].astype(str).str.match(r'^\d+$')]
        if not invalid_accounts.empty:
            error_msg = "Account codes must be numeric"
            error_logger.log_error(
                'validation_errors',
                error_msg,
                {'invalid_rows': invalid_accounts.index.tolist()}
            )
            raise Exception(error_msg)
        
        # Validate balanced entries
        for date, group in df.groupby('date'):
            total_debit = group['debit'].sum()
            total_credit = group['credit'].sum()
            if not np.isclose(total_debit, total_credit, rtol=1e-05):
                error_msg = f"Journal entries for date {date} are not balanced"
                error_logger.log_error(
                    'validation_errors',
                    error_msg,
                    {
                        'date': str(date),
                        'total_debit': float(total_debit),
                        'total_credit': float(total_credit)
                    }
                )
                raise Exception(error_msg)
        
        error_logger.log_info("Excel file validation completed successfully")
    
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
                entries.append(entry)
            return entries
        except Exception as e:
            error_logger.log_error(
                'processing_errors',
                f"Error formatting entries: {str(e)}",
                {'date': df_group['date'].iloc[0]}
            )
            raise Exception(f"Error formatting entries: {str(e)}")
