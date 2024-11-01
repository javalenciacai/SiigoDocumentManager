import pandas as pd

def create_test_files():
    # Valid data
    valid_data = {
        'date': ['2024-01-01', '2024-01-01'],
        'account': ['1010', '2020'],
        'description': ['Test debit', 'Test credit'],
        'debit': [1000.00, 0.00],
        'credit': [0.00, 1000.00],
        'reference': ['REF001', 'REF002']
    }
    pd.DataFrame(valid_data).to_excel('valid_template.xlsx', index=False)
    
    # Invalid data (unbalanced)
    invalid_data = {
        'date': ['2024-01-01', '2024-01-01'],
        'account': ['1010', '2020'],
        'description': ['Test debit', 'Test credit'],
        'debit': [1000.00, 0.00],
        'credit': [0.00, 500.00],  # Unbalanced
        'reference': ['REF001', 'REF002']
    }
    pd.DataFrame(invalid_data).to_excel('invalid_template.xlsx', index=False)

if __name__ == '__main__':
    create_test_files()
