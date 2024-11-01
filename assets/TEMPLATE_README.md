# Journal Entry Template Guide

This document provides guidance on using the sample Excel template for journal entries.

## Template Structure

The template includes the following columns:

1. **document_id** (Required)
   - Format: Integer
   - Unique identifier for the document
   - Example: 27441

2. **date** (Required)
   - Format: YYYY-MM-DD
   - Must be current or past date
   - Example: 2024-01-01

3. **account_code** (Required)
   - Format: Numeric string
   - Must be valid Siigo account number
   - Example: 11050501

4. **movement** (Required)
   - Format: Text
   - Valid values: "Debit" or "Credit"
   - Example: "Debit"

5. **customer_identification** (Required)
   - Format: Text
   - Customer's identification number
   - Example: "13832081"

6. **branch_office** (Required)
   - Format: Integer
   - Default: 0
   - Example: 0

7. **description** (Required)
   - Format: Text (max 255 characters)
   - Should be clear and descriptive
   - Example: "Descripción Débito"

8. **cost_center** (Required)
   - Format: Integer
   - Cost center identifier
   - Example: 235

9. **value** (Required)
   - Format: Numeric (positive numbers only)
   - Example: 119000.00

10. **observations** (Required)
    - Format: Text (max 500 characters)
    - Additional notes or comments
    - Example: "Observaciones"

## Business Rules

1. Total debits must equal total credits for each document_id
2. All values must be positive numbers
3. Each entry must specify either Debit or Credit movement
4. Dates must not be in the future
5. Branch office must be 0 or greater
6. Cost center must be a valid integer

## Sample Entries

The template includes example entries showing:

1. **Balanced Journal Entry**
   - Paired debit and credit entries
   - Matching values
   - Same document_id for related entries

## Tips for Usage

1. Always use matching document_id for related entries
2. Ensure debit and credit entries balance for each document
3. Use clear, consistent descriptions
4. Verify account codes before submission
5. Double-check customer identification numbers
