import pandas as pd
from datetime import datetime

def create_simple_template():
    """Creates and saves the simple Excel template."""
    df = pd.DataFrame({
        'document_id': [123, 123],
        'date': [datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')],
        'account_code': ['110505', '111005'],
        'movement': ['Debit', 'Credit'],
        'customer_identification': ['123456789', '987654321'],
        'branch_office': [0, 0],
        'description': ['Venta de producto A', 'Venta de producto B'],
        'cost_center': [10, 20],
        'value': [150.00, 150.00],
        'observations': ['Muestra para plantilla simple.', 'Muestra para plantilla simple.']
    })

    output_path = "/home/runner/workspace/templates/plantilla_simple.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl', datetime_format='YYYY-MM-DD') as writer:
        df.to_excel(writer, index=False, sheet_name='JournalEntries')

    print(f"Simple template created at {output_path}")

if __name__ == "__main__":
    create_simple_template()
