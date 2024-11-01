import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_sample_template(output_path):
    """Create a sample Excel template with example journal entries"""
    # Create sample data with the new structure
    sample_data = {
        'document_id': [
            27441,
            27441,
        ],
        'date': [
            '2024-01-01',
            '2024-01-01',
        ],
        'account_code': [
            '11050501',
            '11100501',
        ],
        'movement': [
            'Debit',
            'Credit',
        ],
        'customer_identification': [
            '13832081',
            '13832081',
        ],
        'branch_office': [
            0,
            0,
        ],
        'description': [
            'Descripción Débito',
            'Descripción Crédito',
        ],
        'cost_center': [
            235,
            235,
        ],
        'value': [
            119000,
            119000,
        ],
        'observations': [
            'Observaciones',
            'Observaciones',
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to Excel with formatting
    writer = pd.ExcelWriter(output_path, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Journal Entries')
    
    # Access workbook and worksheet
    workbook = writer.book
    worksheet = workbook['Journal Entries']
    
    # Format headers
    for cell in worksheet[1]:
        cell.style = 'Headline 3'
        cell.fill = writer.book.styles.fills[2]  # Light grey fill
    
    # Adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    # Save the file
    writer.close()
    
if __name__ == "__main__":
    create_sample_template('assets/sample_template.xlsx')
