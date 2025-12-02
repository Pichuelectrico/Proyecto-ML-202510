import os
from typing import List
import pandas as pd
from agents import function_tool
from tools.shared import log

RATING_ORDER = ["AAA","AA","A","BBB","BB","B","C","D","E"]
RATING_MAP = {r: i for i, r in enumerate(RATING_ORDER)}

def _normalize_rating(r: str) -> str:
    if not isinstance(r, str):
        return ""
    r = r.replace("*", "").strip()
    parts = [p.strip() for p in r.split('/') if p.strip()]
    candidates = []
    for p in parts:
        base = p.rstrip('+-')
        main = ''.join([c for c in base if c.isalpha()])
        main = main.upper()
        if main in RATING_MAP:
            candidates.append(main)
    if not candidates:
        return ""
    worst = max(candidates, key=lambda x: RATING_MAP.get(x, -1))
    return worst

@function_tool
def get_first_column(file_path: str) -> List[str]:
    """
    Returns the list of values in the first column of a CSV file.
    """
    log(f"🔍 Reading first column of {file_path}")
    try:
        df = pd.read_csv(file_path, usecols=[0], encoding='utf-8-sig')
        return df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    except Exception as e:
        return [f"Error: {str(e)}"]

@function_tool
def create_dataset(cooperatives: List[str], abbreviations: List[str], output_path: str = "data/processed/dataset.csv") -> str:
    """
    Initializes the dataset CSV with two columns: 'cooperativa' and 'abreviacion'.
    """
    log(f"🆕 Creating dataset at {output_path} with {len(cooperatives)} rows")
    try:
        if len(cooperatives) != len(abbreviations):
            return f"Error: Length mismatch. Cooperatives: {len(cooperatives)}, Abbreviations: {len(abbreviations)}"
        
        df = pd.DataFrame({
            "cooperativa": cooperatives,
            "abreviacion": abbreviations
        })
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return f"Successfully created dataset at {output_path}"
    except Exception as e:
        return f"Error creating dataset: {str(e)}"

@function_tool
def append_aligned_columns(file_path: str, index_mapping: List[int], output_path: str = "data/processed/dataset.csv") -> str:
    """
    Appends columns from a source CSV to the dataset, reordering rows based on index_mapping.
    
    Args:
        file_path: Source CSV path.
        index_mapping: List of integers. The i-th element represents the index of the row in the SOURCE CSV 
                       that corresponds to the i-th row in the DESTINATION dataset. 
                       Use -1 if the destination row has no match in the source (will fill with NaN).
        output_path: Path to the dataset being built.
    """
    log(f"📎 Appending columns from {file_path} to {output_path}")
    try:
        if not os.path.exists(output_path):
            return "Error: Output dataset does not exist. Create it first."
        df_source = pd.read_csv(file_path, encoding='utf-8-sig')
        df_source_data = df_source.iloc[:, 1:]
        df_target = pd.read_csv(output_path, encoding='utf-8-sig')
        if len(index_mapping) != len(df_target):
            return f"Error: Mapping length {len(index_mapping)} != Target length {len(df_target)}"
        aligned_rows = []
        for src_idx in index_mapping:
            if src_idx == -1:
                aligned_rows.append({col: None for col in df_source_data.columns})
            elif 0 <= src_idx < len(df_source):
                aligned_rows.append(df_source_data.iloc[src_idx].to_dict())
            else:
                return f"Error: Source index {src_idx} out of bounds (0-{len(df_source)-1})"
                
        df_aligned = pd.DataFrame(aligned_rows)
        df_target.reset_index(drop=True, inplace=True)
        df_aligned.reset_index(drop=True, inplace=True)
        
        df_final = pd.concat([df_target, df_aligned], axis=1)
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return f"Successfully appended {len(df_aligned.columns)} columns from {file_path}"
    except Exception as e:
        return f"Error appending columns: {str(e)}"

@function_tool
def append_cleaned_risk_column(file_path: str, column_name: str, index_mapping: List[int], output_path: str = "data/processed/dataset.csv") -> str:
    """
    Appends a specific risk column from the source CSV, cleaning the values (worst rating logic), and renaming it to 'Label'.
    
    Args:
        file_path: Source CSV path (risk file).
        column_name: The specific column header to extract.
        index_mapping: Mapping array (target_i -> source_j).
        output_path: Path to dataset.
    """
    log(f"🏷️ Appending cleaned risk column '{column_name}' from {file_path}")
    try:
        if not os.path.exists(output_path):
            return "Error: Output dataset does not exist."
            
        df_source = pd.read_csv(file_path, encoding='utf-8-sig')
        if column_name not in df_source.columns:
            return f"Error: Column '{column_name}' not found in {file_path}"
        raw_values = df_source[column_name].astype(str).tolist()
        cleaned_labels = []
        for src_idx in index_mapping:
            if src_idx == -1 or src_idx >= len(raw_values):
                cleaned_labels.append("")
            else:
                val = raw_values[src_idx]
                cleaned_labels.append(_normalize_rating(val))
        df_target = pd.read_csv(output_path, encoding='utf-8-sig')
        if len(cleaned_labels) != len(df_target):
             return f"Error: Label count {len(cleaned_labels)} != Target length {len(df_target)}"
             
        df_target['Label'] = cleaned_labels
        df_target.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return "Successfully appended cleaned 'Label' column."
    except Exception as e:
        return f"Error appending risk column: {str(e)}"

@function_tool
def finalize_and_clean_dataset(file_path: str) -> str:
    """
    Performs professional cleaning and normalization on the consolidated dataset.
    Steps:
    1. Correct data types (remove symbols, convert to float).
    2. Remove garbage columns (>50% nulls, constant).
    3. Impute nulls with median.
    4. Remove duplicates.
    5. Normalize features (StandardScaler logic), excluding 'cooperativa', 'abreviacion', 'Label'.
    
    Args:
        file_path: Path to the consolidated dataset CSV.
    """
    log(f"🧹 Starting professional cleaning and normalization for {file_path}")
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        special_names = {'cooperativa', 'abreviacion', 'label', 'entity', 'segmento'}
        
        non_feature_cols = [c for c in df.columns if c.lower() in special_names]
        feature_cols = [c for c in df.columns if c not in non_feature_cols]
        
        log(f"   -> Identified {len(feature_cols)} feature columns and {len(non_feature_cols)} metadata columns.")
        for col in feature_cols:
            df[col] = df[col].astype(str).str.replace(r'[%,$]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
        threshold = len(df) * 0.5
        df = df.dropna(axis=1, thresh=threshold)
        feature_cols = [c for c in df.columns if c not in non_feature_cols]
        cols_to_drop = [c for c in feature_cols if df[c].nunique(dropna=True) <= 1]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
            log(f"   -> Dropped {len(cols_to_drop)} constant columns.")
            
        feature_cols = [c for c in df.columns if c not in non_feature_cols]
        for col in feature_cols:
            median_val = df[col].median()
            if pd.notnull(median_val):
                df[col] = df[col].fillna(median_val)
            else:
                df[col] = df[col].fillna(0)
        coop_col = next((c for c in df.columns if c.lower() == 'cooperativa'), None)
        if coop_col:
            df.dropna(subset=[coop_col], inplace=True)
        if coop_col:
            initial_rows = len(df)
            df.drop_duplicates(subset=[coop_col], keep='first', inplace=True)
            if len(df) < initial_rows:
                log(f"   -> Removed {initial_rows - len(df)} duplicate rows.")
        for col in feature_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()
            
            if std_val != 0 and not pd.isna(std_val):
                df[col] = (df[col] - mean_val) / std_val
            else:
                df[col] = 0.0
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        return f"Successfully cleaned and normalized dataset. Final shape: {df.shape}"
        
    except Exception as e:
        return f"Error in final cleaning: {str(e)}"
