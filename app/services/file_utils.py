import re
import pandas as pd
from typing import Tuple, Dict, List, Union
from io import BytesIO

def extract_preview_data(file: BytesIO, extension: str) -> Tuple[Dict[str, List[str]], pd.DataFrame]:
    """Reads file and returns a sample of the first 10 values for each column, and full df"""
    try:
        if extension == ".csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        preview_data = {
            col: df[col].dropna().astype(str).head(10).tolist()
            for col in df.columns
        }
        return preview_data, df
    except pd.errors.EmptyDataError:
        raise ValueError("The file appears to be empty")
    except Exception as e:
        import traceback; traceback.print_exc();
        raise ValueError(f"Error reading file: {str(e)}")


def clean_json_response(raw: str) -> str:
    """Removes markdown-style ```json ... ``` blocks and trims whitespace."""
    try:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
        return match.group(1).strip() if match else raw.strip()
    except Exception as e:
        import traceback; traceback.print_exc();
        raise ValueError(f"Error cleaning JSON response: {str(e)}")