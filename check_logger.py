from datetime import datetime
import csv
import os

def log_check_execution(check_id: str, items_count: int, log_file: str = 'checks.csv') -> None:
    """
    Log the execution of a check module to a CSV file.
    
    Args:
        check_id: The ID of the check that was executed
        items_count: Number of findings/items returned by the check
        log_file: Path to the CSV log file (default: checks.csv in current directory)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        # Write header if file is new
        if not file_exists:
            writer.writerow(['DateTime', 'CheckID', 'ItemsReturned'])
        # Write data row
        writer.writerow([timestamp, check_id, items_count])

