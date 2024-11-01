import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_sample_template(output_path):
    """Create a sample Excel template with example journal entries"""
    # Create sample data with various common accounting scenarios
    sample_data = {
        'date': [
            # Regular expense entry
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d'),
            # Sales entry
            (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            # Payroll entry
            (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        ],
        'account': [
            # Regular expense
            '610505', # Office supplies expense
            '110505', # Bank account
            # Sales entry
            '110505', # Bank account
            '410505', # Sales revenue
            # Payroll entry
            '510505', # Salary expense
            '237005', # Payroll payable
            '110505', # Bank account
        ],
        'description': [
            'Office supplies purchase',
            'Payment for office supplies',
            'Customer payment received',
            'Sales revenue recorded',
            'Monthly salary expense',
            'Payroll tax liability',
            'Net salary payment'
        ],
        'debit': [
            1000.00, # Expense debit
            0.00,    # Bank credit
            2500.00, # Bank debit
            0.00,    # Sales credit
            3000.00, # Salary debit
            0.00,    # Tax liability
            0.00,    # Bank payment
        ],
        'credit': [
            0.00,    # Expense debit
            1000.00, # Bank credit
            0.00,    # Bank debit
            2500.00, # Sales credit
            0.00,    # Salary debit
            500.00,  # Tax liability
            2500.00, # Bank payment
        ],
        'reference': [
            'INV-001',
            'INV-001',
            'SALE-001',
            'SALE-001',
            'PAY-001',
            'PAY-001',
            'PAY-001'
        ],
        'department': [
            'ADMIN',
            'ADMIN',
            'SALES',
            'SALES',
            'HR',
            'HR',
            'HR'
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
