import unittest
import pandas as pd
from io import BytesIO
from utils.excel_processor import ExcelProcessor

class TestExcelProcessor(unittest.TestCase):
    def create_test_excel(self, data):
        """Helper function to create test Excel file"""
        df = pd.DataFrame(data)
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer

    def test_valid_excel_file(self):
        """Test processing of valid Excel file"""
        test_data = {
            'date': ['2024-01-01', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test debit', 'Test credit'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 1000.00]
        }
        excel_file = self.create_test_excel(test_data)
        processor = ExcelProcessor(excel_file)
        df = processor.read_excel()
        self.assertEqual(len(df), 2)

    def test_missing_columns(self):
        """Test Excel file with missing required columns"""
        test_data = {
            'date': ['2024-01-01'],
            'description': ['Test entry']
        }
        excel_file = self.create_test_excel(test_data)
        processor = ExcelProcessor(excel_file)
        with self.assertRaises(Exception) as context:
            processor.read_excel()
        self.assertTrue("Missing required columns" in str(context.exception))

    def test_invalid_date_format(self):
        """Test Excel file with invalid date format"""
        test_data = {
            'date': ['invalid-date', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test 1', 'Test 2'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 1000.00]
        }
        excel_file = self.create_test_excel(test_data)
        processor = ExcelProcessor(excel_file)
        with self.assertRaises(Exception) as context:
            processor.read_excel()
        self.assertTrue("Invalid date format" in str(context.exception))

    def test_unbalanced_entries(self):
        """Test Excel file with unbalanced debit and credit entries"""
        test_data = {
            'date': ['2024-01-01', '2024-01-01'],
            'account': ['1010', '2020'],
            'description': ['Test 1', 'Test 2'],
            'debit': [1000.00, 0.00],
            'credit': [0.00, 500.00]  # Unbalanced
        }
        excel_file = self.create_test_excel(test_data)
        processor = ExcelProcessor(excel_file)
        with self.assertRaises(Exception) as context:
            processor.read_excel()
        self.assertTrue("not balanced" in str(context.exception))

if __name__ == '__main__':
    unittest.main()