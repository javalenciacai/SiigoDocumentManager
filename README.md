# Siigo Journal Entry Processor

A Streamlit application for automated journal entry processing using Siigo API. This application allows users to upload, validate, and process journal entries in batch, with support for scheduling recurring entries.

## Features

- 📊 Excel template validation and processing
- 🔄 Recurring journal entry scheduling (daily/weekly/monthly)
- 📈 Processing status dashboard
- 📁 Export functionality
- 🔍 Cost centers and document types lookup
- 📝 Comprehensive error logging
- 🔐 Secure API integration

## Prerequisites

- Python 3.11 or higher
- Siigo API credentials (username and access key)
- Required Python packages (installed automatically)

## Setup

1. Clone the repository
2. Set up environment variables:
   - `SIIGO_USERNAME`: Your Siigo API username
   - `SIIGO_ACCESS_KEY`: Your Siigo API access key
   - `SIIGO_API_URL`: Siigo API base URL (defaults to https://api.siigo.com)

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run main.py
```

## Project Structure

```
├── main.py                 # Main Streamlit application
├── utils/                  # Utility modules
│   ├── api_client.py      # Siigo API integration
│   ├── excel_processor.py # Excel file processing
│   ├── template_validator.py # Excel template validation
│   ├── scheduler.py       # Task scheduling
│   ├── database.py       # SQLite database operations
│   └── logger.py         # Error logging
├── tests/                 # Unit tests
├── assets/               # Static assets
└── templates/            # Documentation templates
```

## Excel Template Format

The application expects Excel files with the following columns:

- `document_id`: Unique identifier for the document
- `date`: Transaction date (YYYY-MM-DD)
- `account_code`: Account number
- `movement`: "Debit" or "Credit"
- `customer_identification`: Customer ID
- `branch_office`: Branch office number
- `description`: Transaction description
- `cost_center`: Cost center ID
- `value`: Transaction amount
- `observations`: Additional notes

See `assets/sample_template.xlsx` for an example.

## Features Documentation

### 1. Journal Entry Processing
- Upload Excel files containing journal entries
- Validate entries against business rules
- Process entries immediately or schedule for later
- View processing results and errors

### 2. Scheduling
- Schedule recurring journal entries
- Support for daily, weekly, or monthly processing
- Flexible time selection
- View and manage scheduled tasks

### 3. Catalog Lookup
- Search and view cost centers
- Browse document types
- Real-time data from Siigo API

### 4. Error Handling
- Comprehensive error logging
- User-friendly error messages
- Detailed validation feedback

## API Integration

### Authentication
```python
api_client = SiigoAPI(username, access_key)
api_client.authenticate()
```

### Create Journal Entry
```python
entry_data = {
    "document": {"id": document_id},
    "date": "2024-01-01",
    "items": [
        {
            "account": {
                "code": "11050501",
                "movement": "Debit"
            },
            "customer": {
                "identification": "13832081",
                "branch_office": 0
            },
            "description": "Sample entry",
            "cost_center": 235,
            "value": 119000.00
        }
    ],
    "observations": "Sample journal entry"
}
api_client.create_journal_entry(entry_data)
```

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

## Error Logging

Logs are stored in the `logs` directory with daily rotation:
- `app_YYYYMMDD.log`: Detailed application logs
- Error statistics and recent errors visible in UI

## Security

- API credentials stored securely in environment variables
- JWT token-based authentication
- Company-specific data isolation

## Support

For issues and feature requests, please open an issue in the repository.

## License

This project is proprietary and confidential.
