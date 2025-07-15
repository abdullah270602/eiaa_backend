import pandas as pd
from typing import Dict, List

def apply_column_mapping(
    df: pd.DataFrame,
    mapping: Dict[str, str],
    unmatched_columns: List[str]
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(mapping, dict):
        raise TypeError("mapping must be a dictionary")
    if not isinstance(unmatched_columns, list):
        raise TypeError("unmatched_columns must be a list")
    if df.empty:
        raise ValueError("DataFrame is empty")
    if not mapping:
        raise ValueError("Column mapping dictionary is empty")
        
    try:
        df = df.rename(columns=mapping)
        
        matched_cols = list(mapping.values())
        unmatched_cols = [col for col in df.columns if col not in matched_cols]
        
        final_cols = matched_cols + [col for col in unmatched_cols if col in unmatched_columns]
        
        if not final_cols:
            raise ValueError("No columns matched the mapping criteria")
            
        return df[final_cols]
    except KeyError as e:
        import traceback; traceback.print_exc();
        raise KeyError(f"Column mapping failed: {str(e)}")
    except Exception as e:
        import traceback; traceback.print_exc();
        raise RuntimeError(f"An error occurred while applying column mapping: {str(e)}")
