import requests
import logging
import csv
from pathlib import Path
from typing import List, Dict


# Configure logging to both console and file
def setup_logging(log_file: str = 'digicert_processor.log'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def load_order_ids_from_csv(csv_path: str) -> List[str]:
    """
    Load order IDs from a CSV file.
    
    Args:
        csv_path: Path to the CSV file containing order IDs
        
    Returns:
        List of order IDs
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV file is malformed
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
    
    order_ids = []
    try:
        with open(csv_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row:  # Skip empty rows
                    order_ids.append(row[0].strip())
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    if not order_ids:
        raise ValueError("No order IDs found in CSV file")
    
    logger.info(f"Loaded {len(order_ids)} order IDs from {csv_path}")
    return order_ids

def process_single_order(order_id: str, headers: Dict[str, str], metadata_id: int) -> bool:
    """
    Process a single Digicert order to update custom field with user's email.
    
    Args:
        order_id: The Digicert order ID to process
        headers: API headers including authorization
        metadata_id: The custom field ID to update
        
    Returns:
        bool: True if operation was successful, False otherwise
    """
    try:
        # Validate input
        if not order_id or not isinstance(order_id, str):
            logger.error(f"Invalid order_id: {order_id}")
            return False
        
        # Step 1: Get certificate data
        get_url = f'https://www.digicert.com/services/v2/order/certificate/{order_id}'
        
        logger.info(f"Processing order {order_id}")
        get_response = requests.get(get_url, headers=headers, timeout=30)
        get_response.raise_for_status()
        
        try:
            get_json_data = get_response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON for order {order_id}: {e}")
            return False
        
        # Safely extract email
        try:
            email = get_json_data["user"]["email"]
            if not email:
                logger.error(f"No email found for order {order_id}")
                return False
        except KeyError as e:
            logger.error(f"Missing expected data in response for order {order_id}: {e}")
            return False
            
        # Step 2: Update custom field
        post_url = f'https://www.digicert.com/services/v2/order/certificate/{order_id}/custom-field'
        payload = {
            "metadata_id": metadata_id,
            "value": email
        }
        
        post_response = requests.post(post_url, headers=headers, json=payload, timeout=30)
        post_response.raise_for_status()
        
        logger.info(f"Successfully updated order {order_id} (metadata {metadata_id}) with email {email}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for order {order_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing order {order_id}: {e}", exc_info=True)
        return False

def process_orders_from_csv(
    csv_path: str,
    headers: Dict[str, str],
    metadata_id: int
) -> Dict[str, int]:
    """
    Process all orders from a CSV file.
    
    Args:
        csv_path: Path to CSV file containing order IDs
        headers: API headers including authorization
        metadata_id: The custom field ID to update
        
    Returns:
        Dictionary with processing statistics:
        {
            'total': X,
            'success': Y,
            'failed': Z
        }
    """
    stats = {'total': 0, 'success': 0, 'failed': 0}
    
    try:
        order_ids = load_order_ids_from_csv(csv_path)
        stats['total'] = len(order_ids)
        
        for order_id in order_ids:
            if process_single_order(order_id, headers, metadata_id):
                stats['success'] += 1
            else:
                stats['failed'] += 1
                
    except Exception as e:
        logger.error(f"Fatal error in processing batch: {e}", exc_info=True)
    
    logger.info(f"Processing complete. Results: {stats}")
    return stats

# Example usage
if __name__ == "__main__":
    # Configuration - these would ideally come from config file or environment variables
    CONFIG = {
        'API_KEY': 'B7IXNAZQJXXXXXX--BRING YOUR OWN API KEY---XXXXXX35UFDPOH',
        'METADATA_ID': 8835,  # Your custom field ID
        'CSV_FILE_PATH': 'order_ids.csv'
    }
    
    # Configure API headers
    API_HEADERS = {
        'X-DC-DEVKEY': CONFIG['API_KEY'],
        'Content-Type': 'application/json'
    }
    
    # Process all orders
    results = process_orders_from_csv(
        csv_path=CONFIG['CSV_FILE_PATH'],
        headers=API_HEADERS,
        metadata_id=CONFIG['METADATA_ID']
    )
    print(f"Final results: {results}")