import base64
import io
import os
import polars as pl
import logging

logger = logging.getLogger(__name__)

# Fallback datasets
FALLBACK_DATASETS = {
    'in_control.csv': """value
1.2
1.5
1.0
1.3
1.4
1.1
1.6
1.2
1.7
1.3
1.5
1.4
1.2
1.8
1.1
1.4
1.6
1.3
1.5
1.2""",

    'out_of_control.csv': """value
1.2
1.5
1.0
2.8
2.9
3.0
2.7
2.8
1.2
1.7
1.3
1.5
1.4
1.2
2.7
2.9
3.1
2.8
1.5
1.2"""
}

# Function to read predefined datasets
def load_predefined_dataset(filename):
    """Load a predefined dataset from the data/test directory"""
    # Try multiple possible locations for the data files
    possible_paths = [
        os.path.join('data', 'test', filename),  # Relative to current working directory
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'test', filename),  # Relative to module
        os.path.join('/workspace/source/app/data/test', filename),  # Absolute path in deployment
    ]
    
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                logger.info(f"Loading data from: {file_path}")
                df = pl.read_csv(file_path, columns=[0])
                return df
        except Exception as e:
            logger.warning(f"Error loading predefined dataset from {file_path}: {e}")
            continue
    
    # If we reach here, no file was found. Use fallback data
    logger.warning(f"Could not find dataset {filename} in any of the expected locations. Using fallback data.")
    if filename in FALLBACK_DATASETS:
        try:
            logger.info(f"Using fallback data for {filename}")
            df = pl.read_csv(io.StringIO(FALLBACK_DATASETS[filename]), columns=[0])
            return df
        except Exception as e:
            logger.error(f"Error loading fallback dataset: {e}")
    
    logger.error(f"No data available for {filename}")
    return None



def parse_csv(contents):
    """Parse uploaded CSV file contents from Dash Upload component"""
    if contents is None:
        return None
    
    try:
        # Remove the data URI prefix (e.g., 'data:text/csv;base64,')
        content_string = contents.split(',')[1]
        # Decode base64 and convert to DataFrame
        decoded = base64.b64decode(content_string).decode('utf-8')
        return pl.read_csv(io.StringIO(decoded), columns=[0])
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return None
