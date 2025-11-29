import pandas as pd
import os
import csv
import warnings
from typing import List, Any, Union
from agents import function_tool
from tools.shared import log

# Suppress specific warnings from openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

@function_tool
def get_excel_sheet_names(file_path: str) -> List[str]:
    """
    Gets the names of all sheets in an Excel file.
    
    Args:
        file_path: The path to the Excel file.
        
    Returns:
        A list of sheet names.
    """
    log(f"📑 Getting sheet names from {file_path}")
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        return [f"Error reading excel file: {str(e)}"]

@function_tool
def read_excel_range(file_path: str, sheet_name: str, start_row: int, start_col: int, end_row: int, end_col: int) -> List[List[Any]]:
    """
    Reads a range of cells from an Excel sheet.
    
    Args:
        file_path: The path to the Excel file.
        sheet_name: The name of the sheet to read.
        start_row: The starting row index (0-based).
        start_col: The starting column index (0-based).
        end_row: The ending row index (0-based).
        end_col: The ending column index (0-based).
        
    Returns:
        A list of lists containing the cell values.
    """
    log(f"🔍 Reading range {start_row},{start_col} to {end_row},{end_col} from {sheet_name} in {file_path}")
    try:
        # Read the specific sheet
        # We use header=None to read raw data without assuming a header
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Slice the dataframe
        # Ensure indices are within bounds
        max_row, max_col = df.shape
        
        s_row = max(0, start_row)
        e_row = min(max_row, end_row + 1) # +1 because iloc is exclusive at the end
        s_col = max(0, start_col)
        e_col = min(max_col, end_col + 1)
        
        if s_row >= max_row or s_col >= max_col:
            return []

        subset = df.iloc[s_row:e_row, s_col:e_col]
        
        # Convert to list of lists, handling NaNs
        return subset.where(pd.notnull(subset), None).values.tolist()
    except Exception as e:
        log(f"Error reading range: {str(e)}")
        return [[f"Error: {str(e)}"]]

@function_tool
def extract_range_to_csv(
    excel_path: str,
    sheet_name: str,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
    output_csv_path: str,
    transpose: bool = False
) -> str:
    """
    Extracts a specific range from an Excel sheet and saves it as a CSV file.
    Handles reading large ranges efficiently without passing data through the agent.
    
    Args:
        excel_path: Path to the source Excel file.
        sheet_name: Name of the sheet.
        start_row: Starting row index (0-based).
        start_col: Starting column index (0-based).
        end_row: Ending row index (0-based).
        end_col: Ending column index (0-based).
        output_csv_path: Path where the CSV will be saved.
        transpose: If True, swaps rows and columns before saving.
        
    Returns:
        Success message.
    """
    log(f"💾 Extracting range {start_row},{start_col} to {end_row},{end_col} from {sheet_name} to {output_csv_path} (Transpose={transpose})")
    try:
        # Read specific range
        # Using header=None to treat everything as data
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
        
        max_row, max_col = df.shape
        s_row = max(0, start_row)
        e_row = min(max_row, end_row + 1)
        s_col = max(0, start_col)
        e_col = min(max_col, end_col + 1)
        
        subset = df.iloc[s_row:e_row, s_col:e_col]
        
        if transpose:
            subset = subset.transpose()
            
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        # Save to CSV without index and header (since we read without header)
        # Use utf-8-sig to ensure Excel opens it correctly with special characters
        subset.to_csv(output_csv_path, index=False, header=False, encoding='utf-8-sig')
        
        return f"Successfully created CSV at {output_csv_path}"
    except Exception as e:
        return f"Error extracting to CSV: {str(e)}"
