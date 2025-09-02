import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.template_validator import TemplateValidator

class TestTemplateValidator(unittest.TestCase):
    def setUp(self):
        self.validator = TemplateValidator()
        self.base_data = {
            'document_id': [1, 1],
            'date': ['2024-01-01', '2024-01-01'],
            'account_code': ['110505', '413505'],
            'movement': ['Debit', 'Credit'],
            'customer_identification': ['12345', '12345'],
            'branch_office': [0, 0],
            'cost_center': [10, 10],
            'value': [1000.00, 1000.00],
            'description': ['Venta', 'Ingreso'],
            'observations': ['Obs', 'Obs']
        }

    def test_valid_template(self):
        """Test validation of a valid simple template"""
        df = pd.DataFrame(self.base_data)
        # Should not raise any exception
        self.validator.validate_template(df)

    def test_missing_required_columns(self):
        """Test validation with missing required columns"""
        data = {'date': ['2024-01-01'], 'description': ['Test entry']}
        df = pd.DataFrame(data)
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            self.validator.validate_template(df)

    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        data = self.base_data.copy()
        data['date'] = ['invalid-date', '2024-01-01']
        df = pd.DataFrame(data)
        with self.assertRaisesRegex(ValueError, r"Invalid date format in column 'date' at rows: \[0\]. Required format: YYYY-MM-DD"):
            self.validator.validate_template(df)

    def test_unbalanced_entries(self):
        """Test validation with unbalanced entries (debit != credit)"""
        data = self.base_data.copy()
        data['value'] = [1000.00, 500.00] # Debit is 1000, Credit is 500
        df = pd.DataFrame(data)
        with self.assertRaisesRegex(ValueError, r"Journal entries for document_id 1 are not balanced \(Debit: 1000.0, Credit: 500.0\)"):
            self.validator.validate_template(df)

    def test_invalid_movement_values(self):
        """Test validation with invalid 'movement' values"""
        data = self.base_data.copy()
        data['movement'] = ['Debito', 'Credito'] # Spanish instead of English
        df = pd.DataFrame(data)
        with self.assertRaisesRegex(ValueError, r"Invalid values in column 'movement' at rows: \[0, 1\]. Allowed values: \['Debit', 'Credit'\]"):
            self.validator.validate_template(df)

if __name__ == '__main__':
    unittest.main()