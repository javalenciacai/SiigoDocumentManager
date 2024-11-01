import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import error_logger

class TemplateValidator:
    def __init__(self):
        self.template_version = "2.0"
        self.required_columns = {
            'document_id': {'type': 'int'},
            'date': {'type': 'datetime', 'format': '%Y-%m-%d'},
            'account_code': {'type': 'string', 'pattern': r'^\d+$'},
            'movement': {'type': 'string', 'values': ['Debit', 'Credit']},
            'customer_identification': {'type': 'string'},
            'branch_office': {'type': 'int', 'min': 0},
            'description': {'type': 'string', 'max_length': 255},
            'cost_center': {'type': 'int', 'min': 0},
            'value': {'type': 'float', 'min': 0},
            'observations': {'type': 'string', 'max_length': 500}
        }
        
    def validate_template(self, df):
        """Validate the Excel template structure and data"""
        errors = []
        
        try:
            # Check template structure
            self._validate_columns(df, errors)
            
            if not errors:
                # Validate data formats
                self._validate_data_formats(df, errors)
                
                # Validate business rules
                self._validate_business_rules(df, errors)
            
            if errors:
                error_msg = "\n".join(errors)
                error_logger.log_error(
                    'validation_errors',
                    "Template validation failed",
                    {'errors': errors}
                )
                raise ValueError(error_msg)
                
            error_logger.log_info("Template validation completed successfully")
            return True
            
        except Exception as e:
            error_logger.log_error(
                'validation_errors',
                str(e),
                {'template_version': self.template_version}
            )
            raise
            
    def _validate_columns(self, df, errors):
        """Validate template columns"""
        # Check required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            
        # Check for unknown columns
        unknown_columns = [col for col in df.columns if col not in self.required_columns]
        if unknown_columns:
            errors.append(f"Unknown columns found: {', '.join(unknown_columns)}")
            
    def _validate_data_formats(self, df, errors):
        """Validate data formats for each column"""
        for col, rules in self.required_columns.items():
            if col not in df.columns:
                continue
                
            if rules['type'] == 'datetime':
                try:
                    invalid_dates = []
                    for idx, value in df[col].items():
                        try:
                            datetime.strptime(str(value), rules['format'])
                        except ValueError:
                            invalid_dates.append(idx)
                    if invalid_dates:
                        errors.append(f"Invalid date format in column '{col}' at rows: {invalid_dates}. Required format: YYYY-MM-DD")
                except Exception:
                    errors.append(f"Invalid date format in column '{col}'. Required format: YYYY-MM-DD")
                    
            elif rules['type'] == 'float':
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid_numbers = df[df[col].isna()]
                if not invalid_numbers.empty:
                    errors.append(f"Invalid numeric values in column '{col}' at rows: {invalid_numbers.index.tolist()}")
                
                if 'min' in rules:
                    invalid_min = df[df[col] < rules['min']]
                    if not invalid_min.empty:
                        errors.append(f"Values below minimum ({rules['min']}) in column '{col}' at rows: {invalid_min.index.tolist()}")
                    
            elif rules['type'] == 'int':
                try:
                    df[col] = df[col].astype(int)
                except:
                    errors.append(f"Invalid integer values in column '{col}'")
                
                if 'min' in rules:
                    invalid_min = df[df[col] < rules['min']]
                    if not invalid_min.empty:
                        errors.append(f"Values below minimum ({rules['min']}) in column '{col}' at rows: {invalid_min.index.tolist()}")
                    
            elif rules['type'] == 'string':
                if 'values' in rules:
                    invalid_values = df[~df[col].isin(rules['values'])]
                    if not invalid_values.empty:
                        errors.append(f"Invalid values in column '{col}' at rows: {invalid_values.index.tolist()}. Allowed values: {rules['values']}")
                        
                if 'pattern' in rules:
                    invalid_pattern = df[~df[col].astype(str).str.match(rules['pattern'])]
                    if not invalid_pattern.empty:
                        errors.append(f"Invalid format in column '{col}' at rows: {invalid_pattern.index.tolist()}")
                        
                if 'max_length' in rules:
                    too_long = df[df[col].astype(str).str.len() > rules['max_length']]
                    if not too_long.empty:
                        errors.append(f"Values exceeding maximum length ({rules['max_length']}) in column '{col}' at rows: {too_long.index.tolist()}")
                        
    def _validate_business_rules(self, df, errors):
        """Validate business rules"""
        # Check for future dates
        try:
            dates = pd.to_datetime(df['date'], format='%Y-%m-%d')
            future_dates = df[dates > datetime.now()]
            if not future_dates.empty:
                errors.append(f"Future dates found at rows: {future_dates.index.tolist()}")
        except Exception:
            # Date format errors will be caught in _validate_data_formats
            pass
        
        # Validate balanced entries by document_id (Debit/Credit should have same value)
        for doc_id, group in df.groupby('document_id'):
            debit_sum = group[group['movement'] == 'Debit']['value'].sum()
            credit_sum = group[group['movement'] == 'Credit']['value'].sum()
            if not np.isclose(debit_sum, credit_sum, rtol=1e-05):
                errors.append(f"Journal entries for document_id {doc_id} are not balanced (Debit: {debit_sum}, Credit: {credit_sum})")
