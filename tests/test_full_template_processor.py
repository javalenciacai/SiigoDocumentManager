import pytest
import pandas as pd
from utils.excel_processor import ExcelProcessor
import io

@pytest.fixture
def full_template_file():
    """Fixture to create a mock file object for the full template."""
    file_path = "templates/plantilla_completa.xlsx"
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # Use io.BytesIO to simulate a file in memory that pandas can read
    return io.BytesIO(file_content)

def test_full_template_detection_and_processing(full_template_file):
    """
    Tests that the ExcelProcessor correctly identifies and processes the full template.
    """
    # 1. Initialize processor and read the Excel file
    processor = ExcelProcessor(full_template_file)
    df = processor.read_excel()

    # 2. Assert that the template was correctly identified as 'full'
    assert processor.is_full_template is True
    assert not df.empty

    # 3. Group data and format for API
    # In our template, all rows belong to the same document, so there's one group.
    grouped = df.groupby('document_id')
    first_group_key = list(grouped.groups.keys())[0]
    df_group = grouped.get_group(first_group_key)
    
    payload = processor.format_entries_for_api(df_group)

    # 4. Assert the payload structure and content are correct
    assert payload is not None
    
    # Top-level fields
    assert payload['document']['id'] == 27441
    assert payload['date'] == '2025-09-01'
    assert payload['number'] == 1020
    assert payload['observations'] == 'Sample observation for the definitive template.'
    assert payload['currency']['code'] == 'COP'
    assert payload['currency']['exchange_rate'] == 1.0

    # Item-level fields (we have one item in the template)
    assert len(payload['items']) == 1
    item = payload['items'][0]
    
    assert item['account']['code'] == '110505'
    assert item['account']['movement'] == 'Debit'
    assert item['customer']['identification'] == '123456789'
    assert item['value'] == 1500.00
    assert item['cost_center'] == 123
    assert item['description'] == 'Item with all possible fields'

    # Nested object fields
    assert item['due']['prefix'] == 'FV'
    assert item['due']['consecutive'] == 1
    assert item['due']['date'] == '2025-09-30'
    
    assert item['tax']['id'] == 12345
    assert item['tax']['name'] == 'IVA'
    assert item['taxes']['base_value'] == 1260.50

    assert item['fixed_assets'] == 678
    
    assert item['product']['code'] == 'PROD-001'
    assert item['product']['warehouse'] == 302
