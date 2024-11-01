import pandas as pd
from datetime import datetime, timedelta

def create_sample_template(output_path):
    # Create sample data
    sample_data = {
        'date': [datetime.now().strftime('%Y-%m-%d')] * 2,
        'account': ['1010', '2020'],
        'description': ['Sample debit entry', 'Sample credit entry'],
        'debit': [1000.00, 0.00],
        'credit': [0.00, 1000.00]
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
    
    # Save the file
    writer.close()
    
if __name__ == "__main__":
    create_sample_template('assets/sample_template.xlsx')
