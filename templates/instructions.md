# Siigo Journal Entry Processor - User Instructions

## Getting Started

### Authentication
1. Launch the application and enter your Siigo credentials:
   - Username: Your Siigo API username
   - Access Key: Your Siigo API access key
2. After successful login, you'll see your company name displayed in the header

## Journal Entry Processing

### Upload and Immediate Processing
1. Navigate to the "Journal Entry Processing" tab
2. Click "Choose an Excel file" to upload your journal entries
3. The system will validate your file automatically
4. If validation succeeds:
   - Preview your data in the expandable section
   - Click "Process Entries" to process immediately
   - Review the results showing success/failure counts

### Scheduling Recurring Entries
1. After uploading a valid file:
   - Select frequency (daily/weekly/monthly)
   - For weekly: Choose day of the week
   - For monthly: Select day of month (1-28)
   - Set desired processing time
2. Click "Schedule Processing" to create the schedule
3. The task will run automatically at specified times

## Managing Scheduled Tasks

### View Scheduled Tasks
1. Go to the "Scheduled Documents" tab
2. View all active schedules with:
   - File name
   - Next run time
   - Frequency details
3. Click "Refresh" to update the list

### Cancel Scheduled Tasks
1. Find the task in "Scheduled Documents"
2. Expand the task details
3. Click "Cancel Schedule" to stop future processing

## Catalog Management

### Cost Centers
1. Navigate to the "Catalogs" tab
2. View all available cost centers
3. Use the search box to filter cost centers
4. Click "Refresh Catalogs" to update the data

### Document Types
1. In the "Catalogs" tab:
2. Scroll to Document Types section
3. Search for specific document types
4. View all available document types

## Processing Status and History

### View Processing Status
1. Check the "Processing Status" tab for:
   - Current processing activities
   - Success/failure statistics
   - Error details if any

### Review Processed Documents
1. Go to "Processed Documents" tab
2. View historical processing results
3. Filter by date range if needed

## Excel Template Requirements

### Required Columns
- document_id: Unique identifier
- date: Transaction date (YYYY-MM-DD)
- account_code: Valid Siigo account number
- movement: "Debit" or "Credit"
- customer_identification: Customer ID
- branch_office: Branch number (0 or greater)
- description: Transaction description (max 255 chars)
- cost_center: Valid cost center ID
- value: Transaction amount (positive number)
- observations: Additional notes (max 500 chars)

### Business Rules
1. Total debits must equal total credits for each document_id
2. Dates must be in YYYY-MM-DD format and not in future
3. All amounts must be positive numbers
4. Account codes must be valid Siigo accounts
5. Cost centers must exist in the system

## Troubleshooting

### Common Issues
1. File Upload Errors:
   - Verify file format (.xlsx or .xls)
   - Check column names and data types
   - Ensure no missing required fields

2. Processing Errors:
   - Verify balanced debit/credit entries
   - Check account code validity
   - Confirm cost center existence

3. Scheduling Issues:
   - Verify selected time is in future
   - Check frequency settings
   - Ensure file remains accessible

### Error Messages
- Watch for error messages in:
  - File validation results
  - Processing status updates
  - Schedule creation feedback
  - API response details

## Best Practices

1. File Preparation:
   - Use the provided template
   - Validate data before upload
   - Keep file size manageable

2. Scheduling:
   - Choose appropriate frequencies
   - Monitor scheduled task status
   - Review processing results regularly

3. Data Management:
   - Maintain organized file naming
   - Document special entries
   - Regular backup of important files

## Support
- Check the sample template in assets folder
- Review error logs for detailed information
- Contact system administrator for access issues
