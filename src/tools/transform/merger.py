import pandas as pd
import os
from agents import function_tool
from tools.shared import log


@function_tool
def merge_and_clean_csvs(temp_folder: str, output_folder: str, output_filename: str) -> str:
    """
    Merges all CSV files in a temporary folder into a single consolidated CSV file.
    
    The process involves:
    1. Iterating through CSVs in the temp folder.
    2. Merging them based on the first column (renamed to 'cooperativa').
    3. Performing a Left Join starting with the first CSV (Primary Key source).
    4. Cleaning the result: removing empty columns, all-zero columns, and constant columns.
    
    Args:
        temp_folder: Path to the folder containing CSVs to merge (e.g., 'data/preprocessed/temp/').
        output_folder: Path where the final CSV will be saved (e.g., 'data/preprocessed/').
        output_filename: The name of the final CSV file (e.g., '2025-EEFF-MEN.csv').
        
    Returns:
        A success message with the path of the created file.
    """
    log("🏗️ Starting CSV Merge and Clean process...")
    
    output_path = os.path.join(output_folder, output_filename)
    try:
        files = [f for f in os.listdir(temp_folder) if f.endswith('.csv')]
        files.sort()
        
        if not files:
            return "❌ No CSV files found in the temporary folder."
            
        log(f"📂 Found {len(files)} CSV files to merge.")
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"
    try:
        first_file_path = os.path.join(temp_folder, files[0])
        log(f"🔹 Loading Master CSV: {files[0]}")
        df_master = pd.read_csv(first_file_path, encoding='utf-8-sig')
        if not df_master.empty:
            old_name = df_master.columns[0]
            df_master.rename(columns={old_name: 'cooperativa'}, inplace=True)
            log(f"   -> Renamed primary key column '{old_name}' to 'cooperativa'")
        for filename in files[1:]:
            file_path = os.path.join(temp_folder, filename)
            log(f"🔹 Merging: {filename}")
            
            df_curr = pd.read_csv(file_path, encoding='utf-8-sig')
            
            if df_curr.empty:
                log(f"   ⚠️ Skipping empty file: {filename}")
                continue
            df_curr.rename(columns={df_curr.columns[0]: 'cooperativa'}, inplace=True)
            if df_curr['cooperativa'].duplicated().any():
                log(f"   ⚠️ Found duplicate keys in {filename}. Keeping first occurrence.")
                df_curr.drop_duplicates(subset=['cooperativa'], keep='first', inplace=True)
            df_master = pd.merge(df_master, df_curr, on='cooperativa', how='left')
            
        log(f"✅ Merge complete. Shape: {df_master.shape}")
        
    except Exception as e:
        return f"❌ Error during merge process: {str(e)}"
    try:
        log("🧹 Starting Post-Merge Cleaning...")
        initial_cols = df_master.shape[1]
        cols_before_nan = df_master.shape[1]
        df_master.dropna(axis=1, how='all', inplace=True)
        nan_dropped = cols_before_nan - df_master.shape[1]
        if nan_dropped > 0:
            log(f"   -> Dropped {nan_dropped} columns with all NaNs.")
        numeric_cols = df_master.select_dtypes(include=['number']).columns
        zero_cols = [col for col in numeric_cols if (df_master[col] == 0).all()]
        if zero_cols:
            df_master.drop(columns=zero_cols, inplace=True)
            log(f"   -> Dropped {len(zero_cols)} all-zero columns.")
        constant_cols = [col for col in df_master.columns if df_master[col].nunique(dropna=True) <= 1]
        if constant_cols:
            df_master.drop(columns=constant_cols, inplace=True)
            log(f"   -> Dropped {len(constant_cols)} constant columns.")
            
        final_cols = df_master.shape[1]
        log(f"✨ Cleaning complete. Removed {initial_cols - final_cols} columns in total.")
        
    except Exception as e:
        return f"❌ Error during cleaning process: {str(e)}"
    try:
        os.makedirs(output_folder, exist_ok=True)
        df_master.to_csv(output_path, index=False, encoding='utf-8-sig')
        log(f"💾 Saved consolidated file to: {output_path}")
        return f"Successfully merged and cleaned data. Saved to {output_path}"
    except Exception as e:
        return f"❌ Error saving file: {str(e)}"
