# Siigo API Integration Documentation

This document details the integration with Siigo's API for journal entry processing.

## Base URL

The API base URL is configurable via the `SIIGO_API_URL` environment variable, defaulting to `https://api.siigo.com`.

## Authentication

### Endpoint
```
POST /auth
```

### Headers
```
Content-Type: application/json
Partner-Id: EmpreSAAS
```

### Request Body
```json
{
    "username": "your_username",
    "access_key": "your_access_key"
}
```

### Response
```json
{
    "access_token": "jwt_token"
}
```

## Journal Entries

### Create Journal Entry

#### Endpoint
```
POST /v1/journals
```

#### Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
Partner-Id: EmpreSAAS
```

#### Request Schema
```json
{
    "document": {
        "id": "integer"
    },
    "date": "string (YYYY-MM-DD)",
    "items": [
        {
            "account": {
                "code": "string",
                "movement": "string (Debit/Credit)"
            },
            "customer": {
                "identification": "string",
                "branch_office": "integer"
            },
            "description": "string (max 255 chars)",
            "cost_center": "integer",
            "value": "number"
        }
    ],
    "observations": "string (max 500 chars)"
}
```

#### Response
Success response with status code 200 and created journal entry details.

## Cost Centers

### Get Cost Centers

#### Endpoint
```
GET /v1/cost-centers
```

#### Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
Partner-Id: EmpreSAAS
```

#### Response
List of available cost centers.

## Document Types

### Get Document Types

#### Endpoint
```
GET /v1/document-types
```

#### Query Parameters
```
type=FV (Filter for journal vouchers)
```

#### Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
Partner-Id: EmpreSAAS
```

#### Response
List of available document types.

## Error Handling

The API client includes comprehensive error handling:

1. Authentication Errors
   - Invalid credentials
   - Expired tokens
   - Network issues

2. API Errors
   - Invalid request format
   - Business rule violations
   - Server errors

### Error Response Format
```json
{
    "error": "string",
    "message": "string",
    "details": "object (optional)"
}
```

## Rate Limiting

The API implements rate limiting. The client handles rate limit errors by:
1. Logging the error
2. Providing user-friendly error messages
3. Suggesting appropriate retry intervals

## Best Practices

1. Token Management
   - Store tokens securely
   - Refresh when expired
   - Never expose in logs

2. Error Handling
   - Log all API errors
   - Provide clear user feedback
   - Include error details for debugging

3. Data Validation
   - Validate data before sending
   - Check response status codes
   - Verify response data format

## Example Usage

```python
from utils.api_client import SiigoAPI

# Initialize client
api_client = SiigoAPI(username, access_key)

# Authenticate
if api_client.authenticate():
    # Create journal entry
    entry_data = {
        "document": {"id": 27441},
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
    
    try:
        response = api_client.create_journal_entry(entry_data)
        print(f"Entry created successfully: {response}")
    except Exception as e:
        print(f"Error creating entry: {e}")
```
