import pandas as pd
from typing import List
import os

def load_template_columns(template_path: str) -> List[str]:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found at: {template_path}")
    
    try:
        df = pd.read_csv(template_path)
    except pd.errors.EmptyDataError:
        raise ValueError("Template file is empty")
    except pd.errors.ParserError:
        raise ValueError("Invalid CSV format in template file")
    except Exception as e:
        raise Exception(f"Error loading template file: {str(e)}")
        
    return df.columns.tolist()

def get_required_columns() -> List[str]:
    return ["Account Reference"]
