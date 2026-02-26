# Module for reading data from ODBC-compliant databases
from __future__ import annotations
from typing import Optional
import pandas as pd
import pyodbc

def load_dataset_odbc(conn_str: str, sql: str, chunksize: Optional[int] = None) -> pd.DataFrame:
    """
    Execute SQL query against an ODBC database and return results as a DataFrame.
    
    Args:
        conn_str: Connection string for ODBC database (e.g., "Driver={SQL Server};...")
        sql: SQL query to execute
        chunksize: Optional chunk size for reading large datasets in memory-efficient batches.
                   If None, reads entire dataset at once. If specified, reads and concatenates
                   data in chunks to reduce memory usage for large tables.
    
    Returns:
        DataFrame containing the query results. Returns empty DataFrame if no results or chunksize
        processing yields no chunks.
    """
    # Establish ODBC connection using context manager to ensure proper cleanup
    with pyodbc.connect(conn_str) as conn:
        # If chunksize is specified, read data in chunks for memory efficiency
        #if chunksize:
        #    parts = []
        #    # Read SQL query in chunks and accumulate them in a list
        #    for chunk in pd.read_sql(sql, conn, chunksize=chunksize):
        #        parts.append(chunk)
        #    # Concatenate all chunks into a single DataFrame, resetting index; return empty DataFrame if no chunks
        #    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        ## If no chunksize specified, read entire query result into memory at once
        return pd.read_sql(sql, conn)
