import pandas as pd

def create_test_files():
    # Valid data
    valid_data = {
        'document_id': [27441, 27441],
        'date': ['2024-01-01', '2024-01-01'],
        'account_code': ['11050501', '11100501'],
        'movement': ['Debit', 'Credit'],
        'customer_identification': ['13832081', '13832081'],
        'branch_office': [0, 0],
        'description': ['Descripción Débito', 'Descripción Crédito'],
        'cost_center': [235, 235],
        'value': [119000.00, 119000.00],
        'observations': ['Observaciones', 'Observaciones']
    }
    pd.DataFrame(valid_data).to_excel('valid_template.xlsx', index=False)
    
    # Invalid data (unbalanced)
    invalid_data = {
        'document_id': [27441, 27441],
        'date': ['2024-01-01', '2024-01-01'],
        'account_code': ['11050501', '11100501'],
        'movement': ['Debit', 'Credit'],
        'customer_identification': ['13832081', '13832081'],
        'branch_office': [0, 0],
        'description': ['Test debit', 'Test credit'],
        'cost_center': [235, 235],
        'value': [119000.00, 90000.00],  # Unbalanced
        'observations': ['Observaciones', 'Observaciones']
    }
    pd.DataFrame(invalid_data).to_excel('invalid_template.xlsx', index=False)

if __name__ == '__main__':
    create_test_files()
