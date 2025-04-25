# digicert-custom-field

## Description
A Python script that automates updating DigiCert order custom fields with user email addresses by processing order IDs from a CSV file.

## Prerequisites
- Python 3.6+
- `requests` package (`pip install requests`)

##  Configuration Variables
Set these in the script's `CONFIG` dictionary:

| Variable        | Description                     | Example Value      | 
|-----------------|---------------------------------|--------------------|
| `API_KEY`       | Your DigiCert API key           | `'x1y2z3a4b5c6'`   |
| `METADATA_ID`   | Custom field ID to update       | `8835`             | 
| `CSV_FILE_PATH` | Path to CSV with order IDs      | `'orders.csv'`     |

## Input File Format
Create a CSV file with one order ID per line (no header):
>12345
>
>67890
>
>44882


## Usage
1. Save script as `digicert_processor.py`
2. Update configuration variables
3. Run: `python digicert_processor.py`


## Outputs
- **Console:** Summary statistics
- **Log File:** `digicert_processor.log` with detailed processing records


## Sample Log
>2023-05-15 14:30:45 - INFO - Loaded 3 order IDs from orders.csv
>
>2023-05-15 14:30:46 - INFO - Processing order 12345
>
>2023-05-15 14:30:47 - INFO - Successfully updated order 12345 (metadata 8835)
>
>2023-05-15 14:30:48 - ERROR - Failed to process order ABCDE: 404 Not Found
>
>2023-05-15 14:30:49 - INFO - Processing complete. Results: 2 success, 1 failed


## Error Handling
The script handles:
- Invalid/missing order IDs
- API connection issues
- Malformed responses
- Missing email data
- CSV file errors
