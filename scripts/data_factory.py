import polars as pl
import os

def get_data_path():
    # Your specific local path
    local = r"C:\Users\Twan\Downloads\sf-loan-performance-data-sample.csv"
    return local if os.path.exists(local) else "sf-loan-performance-data-sample.csv"

def load_fannie_tape():
    path = get_data_path()
    # The 'Factory' pattern: Centralizing data loading
    return pl.read_csv(path, separator="|", has_header=False, truncate_ragged_lines=True)
