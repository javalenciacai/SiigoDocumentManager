import pandas as pd
import numpy as np
from datetime import datetime

class ExcelProcessor:
    def __init__(self, file):
        self.file = file
        self.valid_account_codes = set()  # In a real implementation, this would be populated from Siigo API
        
    def read_excel(self):
        """Read and validate Excel file"""
        try:
            df = pd.read_excel(self.file)
            self._validate_dataframe(df)
            return df
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _validate_dataframe(self, df):
        """Validate DataFrame structure and content"""
        required_columns = ['date', 'account', 'description', 'debit', 'credit']
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate data types
        if not pd.to_datetime(df['date'], errors='coerce').notna().all():
            raise Exception("Invalid date format in 'date' column")
        
        # Validate numeric columns and convert to float
        for col in ['debit', 'credit']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isna().any():
                raise Exception(f"Invalid numeric values in '{col}' column")
        
        # Validate account codes
        if not df['account'].astype(str).str.match(r'^\d+$').all():
            raise Exception("Account codes must be numeric")
        
        # Validate balanced entries (group by date)
        for date, group in df.groupby('date'):
            total_debit = group['debit'].sum()
            total_credit = group['credit'].sum()
            if not np.isclose(total_debit, total_credit, rtol=1e-05):
                raise Exception(f"Journal entries for date {date} are not balanced")
    
    def format_entries_for_api(self, df_group):
        """Format entries according to Siigo API specifications"""
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
