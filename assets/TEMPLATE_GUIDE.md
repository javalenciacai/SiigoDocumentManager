# Journal Entry Template Guide

## Overview

This guide explains how to create and format journal entries for the Siigo Journal Entry Processor.

## File Format

The application accepts Excel files (.xlsx or .xls) with the following specifications:

### Required Columns

1. **document_id** (Integer)
   - Unique identifier for grouping related entries
   - Example: 27441

2. **date** (YYYY-MM-DD)
   - Transaction date
   - Must not be in the future
   - Example: 2024-01-01

3. **account_code** (String)
   - Valid Siigo account number
   - Example: 11050501

4. **movement** (String)
   - Must be either "Debit" or "Credit"
   - Case sensitive

5. **customer_identification** (String)
   - Customer's identification number
   - Example: 13832081

6. **branch_office** (Integer)
   - Branch office identifier
   - Minimum value: 0
   - Example: 0

7. **description** (String)
   - Transaction description
   - Maximum 255 characters
   - Example: "Office supplies purchase"

8. **cost_center** (Integer)
   - Valid cost center ID
   - Example: 235

9. **value** (Numeric)
   - Transaction amount
   - Must be positive
   - Example: 119000.00

10. **observations** (String)
    - Additional notes
    - Maximum 500 characters

## Business Rules

1. **Balanced Entries**
   - Total debits must equal total credits for each document_id
   - All entries with the same document_id are processed together

2. **Date Validation**
   - Dates must be in YYYY-MM-DD format
   - Future dates are not allowed
   - Must be a valid calendar date

3. **Account Validation**
   - Account codes must exist in Siigo
   - Must match the company's chart of accounts

4. **Amount Rules**
   - All values must be positive numbers
   - Decimal places are supported
   - Zero values are not allowed

## Examples

### Valid Entry Pair
```
document_id,date,account_code,movement,customer_identification,branch_office,description,cost_center,value,observations
27441,2024-01-01,11050501,Debit,13832081,0,Purchase Invoice,235,119000.00,January purchase
27441,2024-01-01,11100501,Credit,13832081,0,Payment for purchase,235,119000.00,January purchase
```

### Common Errors to Avoid

1. Unbalanced entries
```
# Wrong - Total debit ≠ Total credit
27441,2024-01-01,11050501,Debit,13832081,0,Purchase,235,119000.00,Note
27441,2024-01-01,11100501,Credit,13832081,0,Payment,235,100000.00,Note
```

2. Invalid date format
```
# Wrong - Incorrect date format
27441,01-01-2024,11050501,Debit,13832081,0,Purchase,235,119000.00,Note
```

3. Missing required fields
```
# Wrong - Missing customer_identification
27441,2024-01-01,11050501,Debit,,0,Purchase,235,119000.00,Note
```

## Tips

1. Use the provided sample template as a starting point
2. Validate your entries before uploading
3. Group related entries under the same document_id
4. Keep descriptions clear and concise
5. Double-check account codes and cost centers

## Support

For additional help:
1. Check the sample template in assets/sample_template.xlsx
2. Refer to the error messages in the application
3. Contact support if you encounter persistent issues
