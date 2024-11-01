import unittest
import pandas as pd
from datetime import datetime, timedelta
from utils.template_validator import TemplateValidator

class TestTemplateValidator(unittest.TestCase):
    def setUp(self):
        self.validator = TemplateValidator()
        
    def test_valid_template(self):
        """Test validation of a valid template"""
        data = {
            'date': ['2024-01-01', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test debit', 'Test credit'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 1000.00],
            'reference': ['REF001', 'REF002']
        }
        df = pd.DataFrame(data)
        self.assertTrue(self.validator.validate_template(df))
        
    def test_missing_required_columns(self):
        """Test validation with missing required columns"""
        data = {
            'date': ['2024-01-01'],
            'description': ['Test entry']
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as context:
            self.validator.validate_template(df)
        self.assertTrue("Missing required columns" in str(context.exception))
        
    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        data = {
            'date': ['invalid-date', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test 1', 'Test 2'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 1000.00]
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as context:
            self.validator.validate_template(df)
        self.assertTrue("Invalid date format" in str(context.exception))
        
    def test_unbalanced_entries(self):
        """Test validation with unbalanced entries"""
        data = {
            'date': ['2024-01-01', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test 1', 'Test 2'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 500.00]
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as context:
            self.validator.validate_template(df)
        self.assertTrue("not balanced" in str(context.exception))
        
    def test_future_dates(self):
        """Test validation with future dates"""
        future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        data = {
            'date': [future_date, future_date],
            'account': ['1010', '2020'],
            'description': ['Test 1', 'Test 2'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 1000.00]
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as context:
            self.validator.validate_template(df)
        self.assertTrue("Future dates found" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
