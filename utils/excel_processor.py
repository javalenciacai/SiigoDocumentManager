import pandas as pd
import numpy as np

class ExcelProcessor:
    def __init__(self, file):
        self.file = file
        
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
        
        # Validate numeric columns
        for col in ['debit', 'credit']:
            if not pd.to_numeric(df[col], errors='coerce').notna().all():
                raise Exception(f"Invalid numeric values in '{col}' column")
        
        # Validate balanced entries
        total_debit = df['debit'].sum()
        total_credit = df['credit'].sum()
        if not np.isclose(total_debit, total_credit, rtol=1e-05):
            raise Exception("Journal entries are not balanced")
