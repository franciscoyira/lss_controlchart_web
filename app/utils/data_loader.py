import base64
import io
import os
import polars as pl

# Resolve the data directory relative to the repo root so loading works
# regardless of the current working directory (python app/app.py, gunicorn, etc.)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(_REPO_ROOT, 'data', 'test')


def _prepare(df):
    """Validate and normalize a raw DataFrame: keep the first column as a
    numeric 'value' column, dropping rows that aren't numbers.

    Returns None if the data is unusable (no numeric values or fewer than
    2 data points, which is the minimum to compute control statistics).
    """
    if df is None or df.width == 0:
        return None
    df = df.rename({df.columns[0]: 'value'})
    df = df.with_columns(pl.col('value').cast(pl.Float64, strict=False)).drop_nulls('value')
    if df.height < 2:
        return None
    return df


# Function to read predefined datasets
def load_predefined_dataset(filename):
    """Load a predefined dataset from the data/test directory"""
    file_path = os.path.join(DATA_DIR, filename)
    try:
        df = pl.read_csv(file_path, columns=[0])
        return _prepare(df)
    except Exception as e:
        print(f"Error loading predefined dataset: {e}")
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
        return _prepare(pl.read_csv(io.StringIO(decoded), columns=[0]))
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None
