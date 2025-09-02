import pandas as pd

def create_truly_full_template():
    """Creates and saves the truly complete Excel template based on full API spec."""
    columns = [
        # Simple template columns
        'document_id',
        'date',
        'observations',
        'account_code',
        'movement',
        'customer_identification',
        'branch_office',
        'description',
        'cost_center',
        'value',
        # Document level fields
        'document_type',
        # Item level fields
        'due_date',
        # Fields for the 'taxes' object array
        'tax_id',
        'tax_name',
        'tax_type',
        'tax_rate',
        'tax_value',
        # Fields for the 'retentions' object array
        'retention_id'
    ]
    df = pd.DataFrame(columns=columns)
    
    # Add an example row with data types hint
    example_row = {
        'document_id': 125,
        'date': '2024-02-15',
        'observations': 'Complete template sample with all fields.',
        'account_code': '130505',
        'movement': 'Debit',
        'customer_identification': '987654321',
        'branch_office': 0,
        'description': 'Item with taxes and retentions',
        'cost_center': 30,
        'value': 100000.00,
        'document_type': 'Manual',
        'due_date': '2024-03-15',
        'tax_id': 13245,
        'tax_name': 'Iva',
        'tax_type': 'IVA',
        'tax_rate': 19.0,
        'tax_value': 19000.00,
        'retention_id': 23456
    }
    df.loc[0] = example_row
    
    # Set data types for columns
    df['date'] = pd.to_datetime(df['date'])
    df['due_date'] = pd.to_datetime(df['due_date'])

    output_path = "/home/runner/workspace/templates/plantilla_completa.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl', datetime_format='YYYY-MM-DD') as writer:
        df.to_excel(writer, index=False, sheet_name='JournalEntries')

    print(f"Template created at {output_path}")

if __name__ == "__main__":
    create_truly_full_template()
