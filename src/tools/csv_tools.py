import pandas as pd
import os
from typing import List, Any
from agents import function_tool
from tools.shared import log

@function_tool
def get_csv_shape(file_path: str) -> str:
    """
    Gets the number of rows and columns in a CSV file.
    
    Args:
        file_path: The path to the CSV file.
        
    Returns:
        A string describing the shape (e.g., "Rows: 100, Columns: 50").
    """
    log(f"📏 Calculating shape of {file_path}...")
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        rows, cols = df.shape
        log(f"   -> Found {rows} rows and {cols} columns")
        return f"Rows: {rows}, Columns: {cols}"
    except Exception as e:
        return f"Error reading CSV file: {str(e)}"

@function_tool
def get_csv_columns(file_path: str, offset: int = 0, limit: int = 200) -> List[str]:
    """
    Gets the column names of a CSV file with pagination support.
    
    Args:
        file_path: The path to the CSV file.
        offset: The starting index (0-based) of the columns to return.
        limit: The maximum number of columns to return.
        
    Returns:
        A list of column names.
    """
    end_idx = offset + limit
    log(f"📊 Reading Headers (Cols {offset} to {end_idx}) from {file_path}")
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', nrows=0)
        all_columns = df.columns.tolist()
        print(all_columns[offset : offset + limit])
        return all_columns[offset : offset + limit]
    except Exception as e:
        return [f"Error reading CSV file: {str(e)}"]

@function_tool
def read_csv_head(file_path: str, n_rows: int = 3) -> List[List[Any]]:
    """
    Reads the first n rows of a CSV file, INCLUDING the headers as the first row.
    
    Args:
        file_path: The path to the CSV file.
        n_rows: The number of data rows to read (headers are extra).
        
    Returns:
        A list of lists. The first list is the headers. The subsequent lists are the row values.
    """
    log(f"👀 Reading headers and first {n_rows} rows from {file_path}")
    try:
        df = pd.read_csv(file_path, nrows=n_rows, encoding='utf-8-sig')
        # Get headers
        headers = df.columns.tolist()
        # Get values
        values = df.where(pd.notnull(df), None).values.tolist()
        # Combine
        return [headers] + values
    except Exception as e:
        return [[f"Error reading CSV file: {str(e)}"]]

@function_tool
def read_csv_column(file_path: str, column_index: int = 0, offset: int = 0, limit: int = 200) -> List[Any]:
    """
    Reads values from a specific column in the CSV with pagination support.
    
    Args:
        file_path: The path to the CSV file.
        column_index: The index of the column to read (0-based). Default is 0.
        offset: The starting index (0-based) of the rows to read.
        limit: The maximum number of rows to return.
        
    Returns:
        A list containing the values of the specified column slice.
    """
    end_idx = offset + limit
    log(f"🧐 Reading First Column (Rows {offset} to {end_idx}) from {file_path}")
    try:
        # Read the full column (efficient enough for typical CSV sizes) and slice in memory
        # This avoids complex skiprows logic with headers
        df = pd.read_csv(file_path, usecols=[column_index], encoding='utf-8-sig')
        
        # Slice the dataframe
        subset = df.iloc[offset : offset + limit, 0]
        
        # Return the values as a list, handling NaNs
        return subset.where(pd.notnull(subset), None).tolist()
    except Exception as e:
        return [f"Error reading column: {str(e)}"]

@function_tool
def delete_columns(file_path: str, column_names: List[str]) -> str:
    """
    Deletes multiple columns from a CSV file by their names.
    
    Args:
        file_path: The path to the CSV file.
        column_names: A list of column names to delete.
        
    Returns:
        A success message.
    """
    log(f"🗑️ Deleting columns {column_names} from {file_path}")
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Filter columns that actually exist in the dataframe
        to_drop = [c for c in column_names if c in df.columns]
        
        if not to_drop:
            return "No matching columns found to delete."
            
        df.drop(columns=to_drop, inplace=True)
        
        # Clean column names by removing pandas duplicate suffixes (e.g., .1, .2)
        df.columns = df.columns.str.replace(r'\.\d+$', '', regex=True)

        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        rows, cols = df.shape
        return f"Successfully deleted {len(to_drop)} columns. New shape: Rows: {rows}, Columns: {cols}. WAIT for this confirmation before proceeding."
    except Exception as e:
        return f"Error deleting columns: {str(e)}"

@function_tool
def delete_rows_by_values(file_path: str, column_index: int, values_to_delete: List[str]) -> str:
    """
    Deletes rows where the value in a specific column matches any of the provided values EXACTLY.
    
    Args:
        file_path: The path to the CSV file.
        column_index: The index of the column to check (0-based).
        values_to_delete: A list of exact values (strings) to identify rows for deletion.
        
    Returns:
        A success message.
    """
    log(f"✂️ Deleting rows in {file_path} where column {column_index} is in {values_to_delete}")
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        if column_index >= len(df.columns):
            return f"Column index {column_index} out of bounds"
            
        col_name = df.columns[column_index]
        
        # Filter rows
        original_count = len(df)
        
        # Convert column and values to string for comparison to be safe, or keep as is?
        # Let's try to match types if possible, but string comparison is safest for mixed types in CSVs.
        # We'll convert both to string for the mask.
        
        # Normalize values to delete to strings
        values_str = [str(v) for v in values_to_delete]
        
        # Create mask: True if value is in the list
        mask = df[col_name].astype(str).isin(values_str)
        
        df_clean = df[~mask]
        
        deleted_count = original_count - len(df_clean)
        
        df_clean.to_csv(file_path, index=False, encoding='utf-8-sig')
        rows, cols = df_clean.shape
        return f"Successfully deleted {deleted_count} rows. New shape: Rows: {rows}, Columns: {cols}. WAIT for this confirmation before proceeding."
    except Exception as e:
        return f"Error deleting rows: {str(e)}"
